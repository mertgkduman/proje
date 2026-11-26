"""Stage three separately sourced 2018 labour and expression records."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
import uygulamalar as rules

checks = Path(__file__).resolve().parent
asset_root = Path('data/practices/sources/emep')
out = Path(sys.argv[1])
now = datetime.now(timezone.utc).isoformat()
prefix = '0410-emep-2018-disk-adana'


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def token(suffix):
    return f'{prefix}-{suffix}'


cases = [Path('data/practices')/f'04-emep{suffix}.json' for suffix in ('','-review')]
assert [digest(p) for p in cases] == [
    '772056d54ef6d2e8d2f8bd4cb48b4eca9f20b14648131fcea899dbfaa9cfd274',
    '3a4b1092567102c003d0ffb8143e23cf74f063079b96e05f1952456e85f88ba6',
]
package, review = map(read, cases)
entries, records = package['entries'], package['practice_records']
assert [len(records[table]) for table in ('practice_event','practice_relation','practice_closure')] == [88,82,0]
proof = read(checks/'adana-disk-2018-source-reading.json')
captures = {row['id']:row for row in proof['captures']}


def entry(table, **values):
    entries.append({'kind':table,'values':values})


def add(table, **values):
    records[table].append(values)


def store(path, raw):
    dest=asset_root/path
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        assert dest.read_bytes()==raw, path
    else:
        dest.write_bytes(raw)


sources = {}
for key, title, date, document_kind, source_kind, publisher, author in (
    ('disk-visit','EMEP’ten DİSK’e ziyaret','2018-10-09','official','official','DİSK',None),
    ('emep-visit','Partimizden DİSK’e ziyaret','2018-10-09','party','party_publication','Emek Partisi',None),
    ('evrensel-detention','Adana’da parti bülteni dağıtan 5 EMEP’li gözaltına alındı','2018-10-19','journalism','journalism','Evrensel','Volkan Pekal'),
    ('evrensel-statement','Sevil Aracı: Sermayenin krizi karşısında emekçilerin yanındayız','2018-10-21','journalism','journalism','Evrensel','Volkan Pekal'),
    ('evrensel-nonprosecution','Sözde kriz pazarı yakıyor','2018-12-05','journalism','journalism','Evrensel','Volkan Pekal'),
    ('spk-2018-law','13 Ağustos 2018 tarihli SPK basın açıklaması','2018-08-13','official','official','Sermaye Piyasası Kurulu',None),
):
    capture=captures[key]
    path=Path(capture['path']); url=capture['final_url']; raw=path.read_bytes()
    assert capture['status']==200 and digest(path)==capture['sha256']
    identity=token(key); version=f'{identity}-v1'
    obj=Path('objects')/capture['sha256']; original=obj/'original.html.bin'; readable=obj/'readable.html'
    store(original,raw)
    store(readable,readable_bytes(raw,'html',legacy=False))
    entry('document',id=identity,party_id='emep',title=title,source_kind=document_kind)
    entry('document_version',id=version,document_id=identity,original_url=capture['url'],final_url=url,
          document_date=date,date_precision='day',date_unknown_reason=None,version_label=title,
          accessed_at=capture['retrieved_at'],verified_at=now,mime='text/html',sha256=capture['sha256'],
          original_path=str(original),readable_path=str(readable))
    entry('source_attribution',version_id=version,kind=source_kind,publisher=publisher,author=author,
          social_handle=None,published_at=date,date_precision='day',public_url=url,
          basis='Yayın tarihi, görünen yayıncı ve metinde belirtilen yazar özgün sayfada incelendi.')
    view=build_view(raw,url,asset_root,fetch_assets=False)
    validate_view(asset_root,view)
    entry('archive_view',**view,version_id=version)
    sources[key] = (version,url,html_source_text(raw))

passages={}
for key, source, exact, section in (
    ('disk-action','disk-visit','Ekonomik kriz üzerine görüş alışverişinde bulununan ziyarette',
     'DİSK, Selma Gürkan, Levent Tüzel ve Güven Gerçek’in katıldığı 9 Ekim 2018 görüşmesini ve kriz gündemini aktarır.'),
    ('emep-action','emep-visit','Ekonomik kriz üzerine görüş alışverişinde bulundu.',
     'EMEP 9 Ekim 2018 görüşmesini ve ev sahibi Arzu Çerkezoğlu’nun değerlendirmelerini bildirir.'),
    ('adana-detention','evrensel-detention','5 kişi polis tarafından g&ouml;zaltına alındı.',
     'Volkan Pekal’ın 19 Ekim Adana Organize Sanayi Bölgesi haberi beş gözaltı bildirir.'),
    ('adana-release','evrensel-detention','İfadelerinin ardından serbest bırakıldı.',
     '19 Ekim haberi, beş kişinin ifadelerinden sonra serbest bırakıldığını bildirir.'),
    ('adana-reaction','evrensel-statement','6362 sayılı Sermaye piyasası kanunu 107/2',
     '21 Ekim Volkan Pekal haberi, 6362/107(2) suçlama atfı ve EMEP il başkanı Sevil Aracı’nın tepkisi.'),
    ('adana-decision','evrensel-nonprosecution','takipsizlik kararı verildi. Bildiriler ise dosyada delil olarak saklanıyor.',
     '5 Aralık Volkan Pekal haberi, savcılığın takipsizlik kararı verdiğini ve bildirilerin dosyada tutulduğunu bildiriyor.'),
    ('adana-law','spk-2018-law','menfaat sağlayanlar hakkında iki yıldan beş yıla kadar',
     '13 Ağustos 2018 SPK açıklaması, o dönemde 6362/107(2) hükmünün aradığı menfaat unsurunu ve yaptırımı aktarır.'),
):
    version,url,content=sources[source]
    assert exact in content, (key, exact)
    item=dict(id=token(key),version_id=version,exact=exact,prefix=None,suffix=None,article=None,
              section=section,pdf_page_index=None,printed_page=None)
    entry('passage',**item)
    passages[key]=(item,url)

inventory=read(Path('data/practices/04-inventory.json'))
scopes={r['topic_id']:r for r in inventory['cells'] if r['party_id']=='emep' and r['research_kind']=='event'}
examined={}
series=(
 ('disk','sendika-grev','2018-10-09','disk-emep-2018-10-09-ekonomik-kriz-gorusmesi',
  '9 Ekim 2018 EMEP heyetinin DİSK ziyareti',
  'DİSK Başkanı Arzu Çerkezoğlu’nun ağırladığı EMEP heyetiyle ekonomik kriz üzerine görüş alışverişi.',
  'DİSK ve EMEP’in aynı tarihli kendi yayınları katılımcıları ve görüşmeyi bildiriyor.',
  'Ortak karar, görev dağılımı ve uygulanmış bir ekonomik önlem için araştırma sürüyor.',
  (('disk-action','action','document'),),('emep-action',)),
 ('adana','demokrasi-katilim','2018-10-19','adana-osb-2018-10-19-emegeseslenis-gozalti',
  '19 Ekim 2018 Adana OSB’de Emeğe Sesleniş dağıtımı ve gözaltı',
  'Beş EMEP üye ve yöneticisinin bildiri dağıtımı sırasında gözaltına alınması ve ifade sonrası salıverilmesi.',
  'Volkan Pekal’ın aynı gün yayımlanan Adana haberi, dağıtım, gözaltı ve salıverilme işlemlerini aktarıyor.',
  'Beş kişi ve salıverilme haber kaydına dayanıyor. Emniyet tutanağı ve asıl bildiri açık. 19 Ekim haberindeki 6352 sayısı, 21 Ekim haberi ve dönemin SPK belgesindeki 6362/107(2) atfıyla uyuşmuyor.',
  (('adana-detention','action','independent_report'),('adana-release','result','independent_report')),('adana-reaction','adana-law')),
 ('decision','demokrasi-katilim','2018-12-05','adana-osb-2018-12-05-takipsizlik-haberi',
  'Adana OSB bildiri dosyasındaki takipsizliğin 5 Aralık 2018’de bildirilmesi',
  'Evrensel, 19 Ekim gözaltılarıyla ilgili takipsizliğin verildiğini ve bildirilerin dosyada tutulduğunu aktarıyor.',
  'Volkan Pekal’ın 5 Aralık 2018 tarihli haberi adli sonucu ve il başkanının açıklamasını yayımladı.',
  '5 Aralık haberin yayım günü. İmzalı takipsizlik, karar tarihi ve dosya numarası açık. Bildirilerin iadesiyle ilgili girişim ve kolluk hakkındaki şikâyet ayrı.',
  (('adana-decision','result','independent_report'),),()),
)
for key,topic,day,common,title,context,occurrence,limit,evidence,supplementary in series:
    scope=scopes[topic]; scope_id=scope['cell_id']
    if not any(r['id']==scope_id for r in records['practice_scope_v2']):
        add('practice_scope_v2',id=scope_id,**{k:scope[k] for k in ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')},
            boundary_reason='Dönem olay kaynakları incelendi. Kapsam araştırması sürüyor.')
    event=token(f'{key}-event')
    add('practice_event',id=event,common_event_key=common,event_at=day,date_precision='day',date_unknown_reason=None,
        title=title,scope_context=context,occurrence_basis=occurrence)
    for ref in (*[ref for ref,_,_ in evidence],*supplementary):
        passage,url=passages[ref]
        examined.setdefault((scope_id,passage['version_id'],url),set()).add(passage['section'])
    for ref,stage,basis in evidence:
        passage,_=passages[ref]
        add('practice_event_evidence',event_id=event,passage_id=passage['id'],stage=stage,
            supported_point=passage['section'],concrete_basis=passage['section'],limitation=limit,epistemic_type='claim')
        add('practice_evidence_assessment',event_id=event,passage_id=passage['id'],stage=stage,basis_kind=basis)
    add('practice_candidate',id=token(f'{key}-unmatched'),scope_id=scope_id,event_id=event,relation_id=None,state='unmatched',
        reason=limit,passage_ids=json.dumps([passages[ref][0]['id'] for ref,_,_ in evidence]))
for (scope_id,version,url),sections in examined.items():
    add('practice_scope_source',scope_id=scope_id,version_id=version,inspected_at=now,
        inspected_sections=json.dumps(sorted(sections),ensure_ascii=False))
    attempt=f'{version}-reading'
    add('practice_attempt_v2',id=attempt,scope_id=scope_id,attempted_at=now,query=url,url=url,result='examined',
        reason='Yayın tarihi, kurum atfı ve aktörün rolü incelendi.',source_version_id=version)
    if not any(r['scope_id']==scope_id and r['url']==url for r in records['practice_lead']):
        add('practice_lead',id=f'lead-{attempt}',scope_id=scope_id,url=url,relevance_reason='Olay veya aynı dönem hukuk metni.',
            state='examined',attempt_ids=json.dumps([attempt]))

snapshot=read(Path('data/releases')/package['base_release']/'records.json')
for item in entries:
    target=snapshot.setdefault(item['kind'],[])
    if item['values'] not in target:
        target.append(item['values'])
snapshot['practice_contract']=records['practice_contract']
for table,rows in records.items():
    saved=snapshot.setdefault(table,[])
    saved.extend(row for row in rows if row not in saved)
rules.validate_practices(snapshot)
targets=rules.practice_review_package_targets(snapshot,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep')
reviews=review['practice_source_review']
existing={(r['subject_kind'],r['subject_id']) for r in reviews}
assert existing<=targets.keys()
by_id={v['id']:v for v,_ in passages.values()}
for kind,identity in sorted(targets.keys()-existing):
    refs,_=targets[kind,identity]
    rows=[by_id[ref] for ref in sorted(refs)]
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,
        source_version_ids=json.dumps(sorted({r['version_id'] for r in rows})),passage_ids=json.dumps(sorted(refs)),
        inspected_sections=json.dumps([r['section'] for r in rows],ensure_ascii=False),
        supported_claim=' '.join(r['section'] for r in rows),
        limitations='Olay günü ile haber günü ve parti eylemi ile adli işlem ayrı incelendi.',
        result='reviewed',reason={
            'practice_event':'Olayın tarih ve oluş dayanağı kendi kronolojisinde doğrulandı.',
            'practice_event_evidence':'Pasajın ilgili olay aşaması, yayın günü ve kapsamı denetlendi.',
            'practice_candidate':'Eşleşmemiş adayın araştırmaya açık bağlantıları ve kaynak kapsamı denetlendi.',
        }.get(kind, f'{kind} kapsamı ve {identity} kaydının kaynak pasajı denetlendi.')))
rules.validate_practice_source_review(snapshot,reviews,party_id='emep',target_keys=set(targets))
assert [len(records[t]) for t in ('practice_event','practice_relation','practice_closure')]==[91,82,0]
references=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]
for suffix,payload in (('',package),('-review',review)):
    payload['source_review_refs']=references
    path=out/f'emep-2018-disk-adana{suffix}-draft.json'
    with path.open('x') as stream:
        stream.write(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    print(digest(path),path)
