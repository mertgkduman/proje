"""Build a candidate with three distinct Istanbul Airport parliamentary motions."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
import uygulamalar as rules

receipt_path, output = map(Path, sys.argv[1:])
practices = Path('data/practices')
assets = output / 'sources'
prefix = '0407-iyi-airport'
now = datetime.now(timezone.utc).isoformat(timespec='seconds')


def read(path):
    return json.loads(path.read_bytes())


def digest(data):
    return sha256(data).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)


base_files = [practices / f'04-iyi{suffix}.json' for suffix in ('', '-review')]
assert [digest(p.read_bytes()) for p in base_files] == [
    '20cedb9d27fba78c62cded057745dd405212effac12268ebf54ef3a372f97337',
    '721b77e6b2f52a693e8b5ff2f7ccd6e47d8212924b48dabc961fd22d4fc84a03',
]
package, review = map(read, base_files)
entries, records = package['entries'], package['practice_records']
assert [len(records[name]) for name in ('practice_event', 'practice_relation', 'practice_closure')] == [23, 15, 0]
proof = read(receipt_path)
captures = {row['id']: row for row in proof['captures']}


def entry(table, **values):
    entries.append(dict(kind=table, values=values))


def add(table, **values):
    records[table].append(values)


sources = {}
unpublished = 'TBMM’nin erişim anındaki sicil görünümü. Tarih alanı ayrı önerge işlemini gösteriyor.'
for key, title, date, author, basis in (
    ('beyaz-detail', 'TBMM 7/3166 yazılı soru sicili', None, None, unpublished),
    ('beyaz-filing', 'Ümit Beyaz imzalı 7/3166 yazılı soru önergesi', '2018-10-17', 'Ümit Beyaz',
     'İmzalı nüshada basılı tarih 17 Ekim, İYİ Parti Grup Başkanlığı kaşesi 20 Eylül 2018.'),
    ('beyaz-unanswered', '25 Ekim 2018 Gelen Kâğıtlar No. 16', '2018-10-25', None,
     'TBMM yayımındaki süresinde cevaplandırılmayan yazılı sorular bölümü, 575. sıra.'),
    ('general-8-3-detail', 'TBMM 8/3 genel görüşme önergesi sicili', None, None, unpublished),
    ('general-8-3-filing', 'Ümit Özdağ ve 20 milletvekilinin imzaladığı 8/3 genel görüşme önergesi', '2018-10-31', 'Ümit Özdağ ve 20 milletvekili',
     'İmzalı metin 31 Ekim. Grup kaşesi 2 Kasım 2018, No. 01.'),
    ('research-10-970-detail', 'TBMM 10/970 Meclis araştırması önergesi sicili', None, None, unpublished),
    ('research-10-970-filing', 'İsmail Tatlıoğlu ve 19 milletvekilinin imzaladığı 10/970 araştırma önergesi', '2019-02-15', 'İsmail Tatlıoğlu ve 19 milletvekili',
     'Meclis araştırması imzalı özgün nüsha. Grup kaşesi 15 Şubat 2019, No. 100.'),
):
    capture = captures[key]
    original = Path(capture['path'])
    raw = original.read_bytes()
    assert capture['status'] == 200 and digest(raw) == capture['sha256']
    source_kind = original.suffix[1:]
    relative = Path('objects', capture['sha256'])
    raw_path = relative / ('original.pdf' if source_kind == 'pdf' else 'original.html.bin')
    readable = relative / 'readable.html'
    save(assets / raw_path, raw)
    save(assets / readable, readable_bytes(raw, source_kind, legacy=True))
    identity, version = f'{prefix}-{key}', f'{prefix}-{key}-v1'
    url = capture['final_url']
    precision = 'day' if date else 'unknown'
    entry('document', id=identity, party_id='iyi', title=title, source_kind='official')
    entry('document_version', id=version, document_id=identity, original_url=capture['url'], final_url=url,
          document_date=date, date_precision=precision, date_unknown_reason=None if date else unpublished,
          version_label=title, accessed_at=capture['retrieved_at'], verified_at=now,
          mime='application/pdf' if source_kind=='pdf' else 'text/html', sha256=capture['sha256'],
          original_path=str(raw_path), readable_path=str(readable))
    entry('source_attribution', version_id=version, kind='official', publisher='Türkiye Büyük Millet Meclisi',
          author=author, social_handle=None, published_at=date, date_precision=precision,
          public_url=url, basis=basis)
    if source_kind == 'html':
        charset = 'utf-8' if 'charset=utf-8' in capture['mime'].lower() else None
        view = build_view(raw, url, assets, fetch_assets=False, http_charset=charset)
        validate_view(assets, view)
        entry('archive_view', version_id=version, **view)
    sources[key] = dict(version=version, url=url, original=original, basis=basis)

lapse = 'Yasama D&#xF6;nemi Sona Erdi&#x11F;inden H&#xFC;k&#xFC;ms&#xFC;z Say&#x131;ld&#x131;'
passages = {}
for key, source, page, exact, section in (
    ('beyaz-id','beyaz-detail',None,'7 / 3166','Önerge sicilinde esas numarası 7/3166.'),
    ('beyaz-received','beyaz-detail',None,'20.09.2018','TBMM siciline göre Başkanlığa geliş 20 Eylül 2018.'),
    ('beyaz-mp','beyaz-detail',None,'&#xDC;mit BEYAZ','Soru sahibi İstanbul milletvekili Ümit Beyaz.'),
    ('beyaz-list-date','beyaz-unanswered',None,'25 Ekim 2018 Perşembe','No. 16 Gelen Kâğıtlar listesi 25 Ekim 2018 tarihli.'),
    ('beyaz-list-state','beyaz-unanswered',None,'Süresi İçinde Cevaplandırılmayan Yazılı Soru Önergeleri','Süresinde cevaplandırılmayan yazılı sorular başlığı.'),
    ('beyaz-list-id','beyaz-unanswered',None,'(7/3166)','7/3166, No. 16 listesinin cevaplandırılmayanlar bölümünde 575. sırada.'),
    ('ozdag-date','general-8-3-detail',None,'02/11/2018','TBMM 8/3 sicilinin geliş tarihi 2 Kasım 2018.'),
    ('ozdag-sign','general-8-3-filing',0,'talep ederiz. 31.10.2018','Genel görüşme isteminin imzalı metin tarihi 31 Ekim 2018.'),
    ('ozdag-occupational','general-8-3-filing',0,'kazaları, işçilerin iş güvenliği ve sosyal haklarındaki iddia olunan usulsüzlükler ile','İmzalı metin iş kazalarını, iş güvenliği ve sosyal hak iddialarını görüşmeye açmayı istiyor.'),
    ('ozdag-status','general-8-3-detail',None,lapse,'TBMM 8/3 sicilinde yasama dönemi sonunda hükümsüzlük.'),
    ('tatlioglu-date','research-10-970-detail',None,'15/02/2019','TBMM 10/970 sicilinde Başkanlığa geliş 15 Şubat 2019.'),
    ('tatlioglu-file','research-10-970-filing',0,'inşaatı, finansmanı, ortaklık yapısı','İmzalı 10/970 metni yapım, finansman ve ortaklık yapısını incelenecek konular arasında gösteriyor.'),
    ('tatlioglu-purpose','research-10-970-filing',0,'Meclis Araştırması açılmasını arz ve teklif ederiz.','İmzalı metin araştırma açılması talebi içeriyor.'),
    ('tatlioglu-status','research-10-970-detail',None,lapse,'TBMM 10/970 sicilinde yasama dönemi sonunda hükümsüzlük.'),
):
    item = sources[source]
    body = html_source_text(item['original'].read_bytes()) if page is None else pdf_page_text(item['original'], page)
    assert exact in body, (source, exact)
    row = dict(id=f'{prefix}-{key}',version_id=item['version'],exact=exact,prefix=None,suffix=None,article=None,
               section=section,pdf_page_index=page,printed_page=None)
    entry('passage', **row)
    passages[key] = row

scope, = [row for row in read(practices/'04-inventory.json')['cells']
          if (row['party_id'],row['topic_id'],row['research_kind']) == ('iyi','ulasim-iletisim','event')]
scope_id = scope['cell_id']
if not any(row['id'] == scope_id for row in records['practice_scope_v2']):
    add('practice_scope_v2',id=scope_id,
        **{key:scope[key] for key in ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')},
        boundary_reason='Havalimanı hakkındaki üç ayrı Meclis denetim girişimi incelendi. Dönem ve diğer kaynaklar açık.')
for key, source in sources.items():
    version = source['version']
    inspected = [value['section'] for value in passages.values() if value['version_id']==version] or [source['basis']]
    add('practice_scope_source',scope_id=scope_id,version_id=version,inspected_at=now,
        inspected_sections=json.dumps(inspected,ensure_ascii=False))
    attempt=f'{version}-reading'
    url=source['url']
    add('practice_attempt_v2',id=attempt,scope_id=scope_id,attempted_at=now,query=url,url=url,result='examined',
        reason='Esas numarası, işlem tarihi, imza veya resmî durum kaydı incelendi.',source_version_id=version)
    if not any(row['scope_id']==scope_id and row['url']==url for row in records['practice_lead']):
        add('practice_lead',id=f'lead-{attempt}',scope_id=scope_id,url=url,relevance_reason='Havalimanına ilişkin Meclis işleminin özgün belgesi.',
            state='examined',attempt_ids=json.dumps([attempt]))

for key, day, common, title, detail, evidence_basis, limit, evidence in (
    ('beyaz','2018-09-20','tbmm-27-1-7-3166-havalimani',
     'Ümit Beyaz’ın 7/3166 sayılı yazılı sorusu',
     'İstanbul üçüncü havalimanı inşaatındaki iş kazaları, ölümler ve yaptırımlar için Ümit Beyaz’ın yazılı sorusu. 25 Ekim listesinde süresinde cevaplandırılmayan sorular arasında.',
     'TBMM 7/3166 ayrıntı sayfası, imzalı önerge, 25 Ekim 2018 Gelen Kâğıtlar No. 16.',
     'Meclis sicili ve İYİ Parti grup kaşesi 20 Eylül 2018, imzalı metinde 17 Ekim 2018 yazıyor. Beyaz soruyu milletvekili sıfatıyla yöneltmiş. Dönem programıyla karşılaştırma ve fiilî denetim kayıtları araştırılıyor.',
     (('beyaz-id','initiative'),('beyaz-received','initiative'),('beyaz-mp','initiative'),('beyaz-list-date','result'),('beyaz-list-state','result'),('beyaz-list-id','result'))),
    ('ozdag','2018-11-02','tbmm-27-2-8-3-havalimani',
     'Havalimanı adı ve iş güvenliği için 8/3 sayılı genel görüşme önergesi',
     'Ümit Özdağ ve 20 İYİ Parti milletvekili havalimanının adı, inşaat sırasında yaşanan iş kazaları ve sosyal hak iddiaları hakkında genel görüşme istedi.',
     'TBMM 8/3 sicili, 21 imzacının parti kayıtları ve imzalı genel görüşme önergesi.',
     'İmzalı metin 31 Ekim, grup kaşesi ve sicile geliş 2 Kasım. 6 Kasım tutanağında 2 Kasım listesi içindeki satırda 2 Ekim yazıyor. Sicil dönem sonunda hükümsüzlük bildiriyor. Bu girişimin iş güvenliği uygulamasına etkisi açık.',
     (('ozdag-date','initiative'),('ozdag-sign','initiative'),('ozdag-occupational','initiative'),('ozdag-status','result'))),
    ('tatlioglu','2019-02-15','tbmm-27-2-10-970-havalimani',
     'Havalimanı ihalesi için 10/970 sayılı Meclis araştırması önergesi',
     'İsmail Tatlıoğlu ve 19 İYİ Parti milletvekili İstanbul Havalimanı ihalesi, yapımı, finansmanı ve ortaklık yapısının incelenmesini istedi.',
     'TBMM 10/970 sicili, 20 imzacının parti kayıtları ve imzalı Meclis araştırması önergesi.',
     'TBMM sicilinde dönem sonunda hükümsüzlük var. Gerekçedeki iddialar imzacıların araştırma gerekçesi. İhale ve sözleşme kayıtları ile uygulama sonucu için araştırma sürüyor.',
     (('tatlioglu-date','initiative'),('tatlioglu-file','initiative'),('tatlioglu-purpose','initiative'),('tatlioglu-status','result'))),
):
    event=f'{prefix}-{key}-event'
    add('practice_event',id=event,common_event_key=common,event_at=day,date_precision='day',date_unknown_reason=None,
        title=title,scope_context=detail,occurrence_basis=evidence_basis)
    for ref, stage in evidence:
        passage=passages[ref]
        add('practice_event_evidence',event_id=event,passage_id=passage['id'],stage=stage,supported_point=passage['section'],
            concrete_basis=passage['section'],limitation=limit,epistemic_type='claim')
        add('practice_evidence_assessment',event_id=event,passage_id=passage['id'],stage=stage,basis_kind='document')
    add('practice_candidate',id=f'{prefix}-{key}-unmatched',scope_id=scope_id,event_id=event,relation_id=None,
        state='unmatched',reason=limit,passage_ids=json.dumps([passages[ref]['id'] for ref,_ in evidence]))

snapshot=read(Path('data/releases')/package['base_release']/'records.json')
for item in entries:
    table=snapshot.setdefault(item['kind'],[])
    if item['values'] not in table:
        table.append(item['values'])
snapshot['practice_contract']=records['practice_contract']
for table, rows in records.items():
    saved=snapshot.setdefault(table,[])
    saved.extend(row for row in rows if row not in saved)
rules.validate_practices(snapshot)
targets=rules.practice_review_package_targets(snapshot,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='iyi')
reviews=review['practice_source_review']
existing={(row['subject_kind'],row['subject_id']) for row in reviews}
assert existing<=targets.keys()
lookup={value['id']:value for value in passages.values()}
for kind, identity in sorted(targets.keys()-existing):
    refs,_=targets[kind,identity]
    examined=[lookup[ref] for ref in sorted(refs)]
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,
        source_version_ids=json.dumps(sorted({row['version_id'] for row in examined})),passage_ids=json.dumps(sorted(refs)),
        inspected_sections=json.dumps([row['section'] for row in examined],ensure_ascii=False),
        supported_claim=' '.join(row['section'] for row in examined),
        limitations='Önerge metni, imzacı sıfatı, TBMM sicili ve usule ilişkin sonuçlar ayrı incelendi.',
        result='reviewed',reason=f'{identity} kaydının belge kimliği ve işlem aşaması incelendi.'))
rules.validate_practice_source_review(snapshot,reviews,party_id='iyi',target_keys=set(targets))
references=[{key:row[key] for key in ('subject_kind','subject_id')} for row in reviews]
assert [len(records[name]) for name in ('practice_event','practice_relation','practice_closure')]==[26,15,0]
for suffix, payload in (('',package),('-review',review)):
    payload['source_review_refs']=references
    path=output/f'iyi-airport{suffix}-draft.json'
    raw=(json.dumps(payload,ensure_ascii=False,indent=2)+'\n').encode()
    save(path,raw)
    print(digest(raw),path)
