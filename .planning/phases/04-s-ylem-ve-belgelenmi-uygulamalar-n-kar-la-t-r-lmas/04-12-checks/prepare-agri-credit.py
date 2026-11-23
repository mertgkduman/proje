"""Compare two agricultural filings and a separate ministry notice with the archived program."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from uygulamalar import practice_review_package_targets, validate_practice_source_review, validate_practices

here=Path(sys.argv[1])
data=Path('data')
def read(path):
    return json.loads(path.read_bytes())
def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)
aux=read(here/'agri-credit-source-records.json')
party=aux['party_id']
package=read(here/'province-congress-draft.json')
review=read(here/'province-congress-review-draft.json')
snapshot=read(data/'releases'/package['base_release']/'records.json')
inventory=read(data/'practices/04-inventory.json')
entries=package['entries']; entries.extend(aux['entries'])
records=package['practice_records']
when=datetime.now(timezone.utc).isoformat()
passages={r['id']:r for r in snapshot['passage']}
passages.update({e['values']['id']:e['values'] for e in entries if e['kind']=='passage'})
versions={r['id']:r for r in snapshot['document_version']}
versions.update({e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'})
tasks={}
def new(table,**row):
    entries.append(dict(kind=table,values=row))
def finding(id,body,refs,reason,pair=None):
    new('finding',id=id,party_id=party,heading='Belgelenmiş uygulamalar',text=body,pair_id=pair or id,
        provenance='quote' if pair else 'summary',epistemic_type='claim')
    for pid in refs:
        new('finding_evidence',finding_id=id,passage_id=pid,role='support')
        new('verification',finding_id=id,passage_id=pid,checked_at=when,result='confirmed',reason=reason)
    new('review',id='review-'+id,kind='finding',subject_id=id,reviewer_kind='agent',
        reviewed_at=when,result='reviewed',reason=reason)
def task(kind,identity,body,limitation):
    tasks[(kind,identity)]=(body,limitation)
def scope_for(topic,lane):
    cell=next(row for row in inventory['cells']
              if (row['party_id'],row['topic_id'],row['research_kind'])==(party,topic,lane))
    sid=cell['cell_id']
    if not any(s['id']==sid for s in records['practice_scope_v2']):
        records['practice_scope_v2'].append(dict(id=sid,**{k:cell[k] for k in
            ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')},
            boundary_reason='Tarım finansmanı ve desteklerine ilişkin seçili kaynaklar okundu.'))
    return sid
def readings(topic,lane,refs):
    sid=scope_for(topic,lane)
    grouped={}
    for pid in refs:
        p=passages[pid]
        grouped.setdefault(p['version_id'],set()).add(p['section'])
    for vid,sections in grouped.items():
        existing=[r for r in records['practice_scope_source'] if (r['scope_id'],r['version_id'])==(sid,vid)]
        if existing and set(json.loads(existing[-1]['inspected_sections']))>=sections:
            continue
        if existing:
            sections.update(json.loads(existing[-1]['inspected_sections']))
            if existing[-1]['inspected_at']==when:
                existing[-1]['inspected_sections']=encoded(sorted(sections))
                continue
        url=versions[vid]['final_url']
        aid=f'agri-credit-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Tarım finansmanı veya destekleriyle ilgili program, teklif ya da kurum kaydı.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,key,day,title,context,basis,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=key,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis=basis))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'demokrat'
assert sha256((here/'province-congress-draft.json').read_bytes()).hexdigest() == '05e78901725c688c506b15b89aa918cb2e1cabdfd8053166d08883a7fa175bd0'
assert sha256((here/'province-congress-review-draft.json').read_bytes()).hexdigest() == '00e7019d2a2f6b114184b6efd8f1baae2f4105b7bd0b6702d5151b07438a92cf'
source = '0412-agri-credit-'
topic = 'tarim-hayvancilik'
program_version = '0210-demokrat-program-archive-v1'
program = source+'program-finance'
program_context = source+'program-support'
program_exact = ('Ziraat Bankası “Tarım Bankası”na dönüştürülecek, tarımsal ser-\n'
                 'maye yönetimi Tarımsal Planlama ve Destekleme Başkanlığı ile\n'
                 'eşgüdümlü olarak gerçekleştirilecektir.')
for pid,index,text,section in (
    (program,37,program_exact,'Tarımsal Kalkınma, tarımsal sermaye yönetimi'),
    (program_context,37,'teşvikler, kamu ve fon kaynaklarından sağlanacaktır.','Tarımsal Kalkınma, teşviklerin kaynakları'),
):
    new('passage',id=pid,version_id=program_version,exact=text,prefix=None,suffix=None,
        article=None,section=section,pdf_page_index=index,printed_page='44')
    passages[pid]=entries[-1]['values']
statement,target,quote=(source+suffix for suffix in ('statement','target','quote'))
goal=('Demokrat Parti’nin arşiv programı, Ziraat Bankasının tarım bankasına dönüşmesini, tarımsal sermaye '
      'yönetiminde eşgüdümü ve üreticiye kamu ve fon kaynaklarından destek verilmesini öngörüyor.')
program_limit=('29 Aralık 2021 arşiv yakalaması nüshanın o tarihteki varlığını gösteriyor. '
               'Programın kabul günü ve 2026 işlemlerindeki hukuki yürürlüğü açık.')
program_refs=[program,program_context]
finding(target,goal,program_refs,program_limit)
finding(quote,program_exact,[program],program_limit,pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at=None,date_precision='unknown',
    version_id=program_version,period_basis='Arşiv sürümünün yakalama günü 29 Aralık 2021.',
    uncertainty_reason=program_limit,comparison_row_id='04-03-v3-0313-demokrat-tarim-hayvancilik'))
readings(topic,'statement',program_refs)
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',program_exact)):
    task(kind,statement,claim,program_limit)

events=(
    ('3485','tbmm-28-4-2-3485-basvuru','2026-01-20','Altıntaş’ın 2/3485 tarımsal kredi teklifi',
     'Demokrat Parti İzmir Milletvekili Haydar Altıntaş’ın 2/3485 tarımsal kredi teklifi 20 Ocak 2026’da TBMM Başkanlığına ulaştı. Plan ve Bütçe ile Tarım, Orman ve Köyişleri komisyonlarına giriş 21 Ocak olarak kaydedildi.',
     'İmzalı teklif, işlem kutusu ve TBMM esas sicili.',
     'Teklifin erişilen sicildeki durumu Komisyonda. Belirtilen koşullar öneri aşamasında. Yasalaşma, bireysel kredi ve borç yeniden yapılandırması açık.',
     'Teklif, belirli çiftçiler için krediye erişimde borçsuzluk belgesinin aranmamasını, SGK ve vergi borcunun faizsiz uzun vadeye yayılmasını ve afet desteğini öneriyor.',
     'Arşiv programının tarımsal sermaye ve destek hedefi, 2/3485’in kredi, borç ve afet maddeleriyle karşılaştırıldı.',
     '20 Ocak başvuru ve 21 Ocak komisyon girişi. 17 Şubat Ardahan İl Müdürlüğü duyurusu ayrı işlem.',
     'Altıntaş ilk imza sahibi. Sevki ve gündemi TBMM yürütüyor.',(
        ('register-3485-id','initiative','Teklifin esas numarası 2/3485.'),
        ('register-3485-filed','initiative','Başkanlığa geliş 20 Ocak 2026.'),
        ('register-3485-membership','initiative','Altıntaş imza tablosunda Demokrat Parti milletvekili.'),
        ('signed-3485-id','action','İmzalı nüshada 21 Ocak komisyon işlem kutusu.'),
        ('signed-3485-clearance','initiative','2. madde belirli çiftçiler için krediye erişimde borcu yoktur belgesinin aranmamasını öneriyor.'),
        ('signed-3485-term','initiative','3. madde borçların faizsiz uzun vadeye yayılmasını öneriyor.'),
        ('signed-3485-disaster','initiative','4. madde afet desteği, zarar tespiti ve telafi mekanizması öneriyor.'),
        ('register-3485-referred','action','Her iki komisyona giriş 21 Ocak.'),
        ('register-3485-pending','action','Erişilen TBMM kaydındaki komisyon durumu açık.'),
    )),
    ('ministry','tob-ardahan-2026-02-17-hazine-kredi-duyurusu','2026-02-17','Ardahan İl Müdürlüğünün Hazine destekli kredi duyurusu',
     'Ardahan İl Tarım ve Orman Müdürlüğü 17 Şubat’ta, 15 Şubat Resmî Gazete yayımına bağladığı kredi koşullarını açıkladı.',
     'Ardahan İl Tarım ve Orman Müdürlüğünün günlü kamu duyurusu.',
     'Bilgiler İl Müdürlüğünün açıklamasına dayalı. Resmî Gazete PDF’sine erişilemedi. Bireysel hak sahipliği, mahsup ve fiilî kredi kullanımı açık. 2/3485 ile nedensel bağ için belge yok.',
     'Duyuru, borcu olmayanlar için belgenin 15 günlük süresini, bazı borçların kredinin azami yüzde 25’i ve yılda 300.000 TL ile sınırlı mahsubunu ve 400.000 TL’ye kadar belirli aynî krediler için yıl sonuna dek borçsuzluk şartı istisnasını açıklıyor.',
     'Programın genel tarımsal finansman hedefiyle aynı konuda olan kamu duyurusu daha dar koşullar bildiriyor. 2/3485 önerisinin yasama durumunu değiştiren işlem gösterilmedi.',
     'Duyuru 17 Şubat. Duyuru başlığı 15 Şubat Resmî Gazete yayımına atıf yapıyor.',
     'Açıklamayı Ardahan İl Müdürlüğü yaptı. Demokrat Parti’nin rolü ayrı yasama teklifinde belgeli.',(
        ('ministry-day','action','İl Müdürlüğü yayımı 17 Şubat 2026.'),
        ('ministry-publication','initiative','Başlık 15 Şubat Resmî Gazete yayımını anıyor.'),
        ('ministry-clearance','result','Duyuru borcu olmayanlar için 15 günlük belge süresi veriyor.'),
        ('ministry-offset','result','Duyuru yüzde 25 azami mahsup oranı veriyor.'),
        ('ministry-cap','result','Yıllık toplam mahsup için açıklanan üst sınır 300.000 TL.'),
        ('ministry-exemption','result','Belirli 400.000 TL’ye kadar aynî kredi istisnası 31 Aralık 2026’ya kadar açıklanıyor.'),
    )),
    ('3970','tbmm-28-5-2-3970-basvuru','2026-10-22','Altıntaş’ın 2/3970 tarımsal destek teklifi',
     'Haydar Altıntaş’ın hazırladığı 2/3970 sayılı tarımsal destek teklifi 22 Ekim 2026’da TBMM Başkanlığına ulaştı. Komisyon girişi 23 Ekim’de kayda geçti.',
     'TBMM esas sicili, imzalı teklifin kaşesi ve 23 Ekim Gelen Kâğıtlar listesi.',
     'Erişilen TBMM sicilinde durum Komisyonda. 5488’in tarihsel ilk metni ile teklif ayrı sürümler. Yasalaşma, ödenek, avans, vergi istisnası ve bireysel ödeme sonucu açık.',
     '2/3970, bütçe teklifindeki tarımsal destek için GSYİH’nin yüzde biri düzeyinde alt sınır koymayı, desteğin en az yarısını ekim veya dikimden önce avans ödemeyi, belirli motorin ve gübre teslimlerine vergi istisnası ve destek ödemelerine haciz koruması getirmeyi öneriyor.',
     'Programın kamu kaynaklarından tarımsal destek hedefi, bu teklifte bütçe desteği, ödeme takvimi ve girdi maliyetleri için önerilen araçlarla karşılaştırıldı.',
     '21 Ekim teklif imzası, 22 Ekim TBMM evrak kaydı ve 23 Ekim komisyon girişi ayrı.',
     'Altıntaş ilk imza sahibi. Ödenek, ödeme ve vergi uygulaması ayrı kurum işlemleri gerektirir.',(
        ('register-3970-id','initiative','Teklifin esas numarası 2/3970.'),
        ('register-3970-filed','initiative','TBMM Başkanlığına geliş günü 22 Ekim.'),
        ('register-3970-membership','initiative','İlk imza Demokrat Parti İzmir milletvekili Haydar Altıntaş.'),
        ('signed-3970-id','initiative','İmzalı yazı 21 Ekim 2026 tarihli.'),
        ('signed-3970-stamp','initiative','Evrak damgası 22 Ekim 2026 tarihli.'),
        ('signed-3970-floor','initiative','Madde 1 GSYİH’nin yüzde birini bütçe teklifi için alt sınır olarak öneriyor.'),
        ('signed-3970-advance','initiative','Madde 1 desteklerin en az yarısı için ekim ve dikim öncesi avans öneriyor.'),
        ('signed-3970-tax','initiative','Madde 2 belirli motorin ve gübre teslimleri için KDV ve ÖTV istisnası öneriyor.'),
        ('signed-3970-guard','initiative','Madde 2 tarımsal destek ödemeleri için haciz, devir, tedbir ve bloke sınırlarını öneriyor.'),
        ('agenda-3970-filed','action','23 Ekim Gelen Kâğıtlar iki komisyona sevki listeliyor.'),
        ('register-3970-referred','action','Her iki komisyona giriş 23 Ekim.'),
        ('register-3970-pending','action','Erişilen komisyon kaydı Komisyonda.'),
    )),
)
for label,key,day,title,context,basis,limit,explanation_text,compare,temporal,authority,evidence in events:
    stem=source+label
    refs=[(source+pid,stage,'document',point) for pid,stage,point in evidence]
    eid=event(stem,key,day,title,context,basis,refs,limit)
    pids=[row[0] for row in refs]
    if label=='3970':
        pids.append(source+'enacted-5488-floor')
        explanation_text+=(' 18 Nisan 2006’da kabul edilen ilk metnin 21. maddesi yüzde bir eşiğini '
                           'gayrisafi millî hasıla üzerinden ifade ediyor.')
    scope=readings(topic,'event',pids)
    rid=stem+'-relation'
    explanation=stem+'-explanation'
    finding(explanation,explanation_text,[*program_refs,*pids],limit)
    records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,
        topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=None,
        explanation_finding_id=explanation,temporal_context=temporal,authority_context=authority,uncertainty_reason=limit))
    records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
        state='eligible',reason=compare,passage_ids=encoded(pids)))
    for kind,claim in (('practice_relation',explanation_text),('practice_relation.target_finding_id',goal),
                       ('practice_relation.explanation_finding_id',explanation_text)):
        task(kind,rid,claim,limit)

for entry in entries:
    destination=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in destination:
        destination.append(entry['values'])
for table,rows in records.items():
    destination=snapshot.setdefault(table,[])
    destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot,records,
    [entry['values']['id'] for entry in entries if entry['kind']=='passage'],party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limitation,result='reviewed',
        reason=kind+' hedefinin kaynak, tarih ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('agri-credit-draft.json',package),('agri-credit-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
