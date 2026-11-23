"""Record seven local employment, social, education and sports decisions."""

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
aux=read(here/'baglar-services-source-records.json')
party=aux['party_id']
package=read(data/f'practices/04-{party}.json')
review=read(data/f'practices/04-{party}-review.json')
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
def task(kind,identity,body,limitation):
    tasks[(kind,identity)]=(body,limitation)
def scope_for(topic,lane):
    cell=next(row for row in inventory['cells']
              if (row['party_id'],row['topic_id'],row['research_kind'])==(party,topic,lane))
    sid=cell['cell_id']
    if not any(s['id']==sid for s in records['practice_scope_v2']):
        records['practice_scope_v2'].append(dict(id=sid,**{k:cell[k] for k in
            ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')},
            boundary_reason='Bağlar Belediye Meclisi kararının ilgili bölümü özgün derlemede okundu.'))
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
        aid=f'baglar-services-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Bağlar Belediye Meclisi kararı veya yerel seçim dönem kaydı.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='Bağlar Belediyesi 2015 Meclis karar derlemesindeki tarihli karar.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'dbp'
electoral_context = ['0409-siginak-ysk-district-name','0409-siginak-ysk-district-party']
context_limits = ('YSK kaydı yönetimin 2014 seçim bağlamını veriyor. '
                  'İşlem belediye meclisine ait. Parti adına bağımsız bir karar veya kişisel oy açık.')
events = (
 ('11','2015-01-06','guvencesiz-istihdam','Bağlar’ın 2015 geçici işçi vizesi',
  'Bağlar Belediye Meclisi, geçici işçi statüsünde kalan sekiz çalışan için 2015 çalışma vizesi kabul etti.',
  'Ek cetvel Fen İşleri için 84, Temizlik İşleri için 12 ve toplam 96 kişi-ay öngörüyor. Bordro, fiilî çalışma ve sonraki statü açık.',
  'Geçici iş vizesinin fiilî sonuçları ve daha önce aynı kapsamda açıklanmış tarihli parti hedefi araştırılıyor.',
  (('positions','action','Meclis yazısı geçici statüde kalan çalışanlar için yıllık vize gereğini açıklıyor.'),
   ('table','action','Fen İşleri ve Temizlik İşleri eki toplam 96 kişi-ay gösteriyor.'),
   ('approved','result','6 Ocak’ta meclis geçici işçi vizesini oybirliğiyle kabul etti.'))),
 ('15','2015-01-07','sosyal-hizmet','Bağlar’da 2014 nakit yardım raporunun kabulü',
  '7 Ocak’ta Bağlar Belediye Meclisi, Kültür ve Sosyal İşler Müdürlüğünün 2014 nakit yardımları hakkındaki Plan ve Bütçe Komisyonu raporunu kabul etti.',
  'Komisyon 367 kişiye toplam 125.050 TL nakit yardım verildiğini bildirdi. Ödeme belgeleri ve tekil uygunluk kararları açık.',
  'Rapor kabulü ve komisyon sayıları var. Yardımlar için önceki tarihli parti hedefi ile gerçekleşme kayıtları araştırılıyor.',
  (('people','action','Komisyonun 2014 yardım raporunda 367 kişi yer alıyor.'),
   ('amount','action','Komisyon 125.050 TL nakit yardım yapıldığını bildirdi.'),
   ('approved','result','7 Ocak toplantısında nakdi yardım raporu meclisçe kabul edildi.'))),
 ('17','2015-01-08','toplumsal-cinsiyet','Şeyhşamil kadın sorunları raporunun kabulü',
  '8 Ocak’ta Bağlar Belediye Meclisi, Şeyhşamil’deki sorunlara ilişkin Kadın Sorunlarını Araştırma Komisyonu raporunu kabul etti.',
  'Aralık 2014 muhtarlık görüşmesinden yardım ve park güvenliği talepleri aktarıldı. Taleplerin hangi hizmetlere dönüştüğü açık.',
  'Muhtarlık görüşmesi kaydı ve rapor kabulü var. Uygulama belgeleri ile önceki aynı kapsamlı parti söylemi araştırılıyor.',
  (('review','action','Komisyon Şeyhşamil Mahallesi muhtarıyla görüştüğünü bildirdi.'),
   ('needs','action','Raporda nakit, yakacak ve güvenlik talepleri aktarılıyor.'),
   ('approved','result','Meclis 8 Ocak’ta kadın sorunları konulu raporu kabul etti.'))),
 ('18','2015-01-08','toplumsal-cinsiyet','Nevroz Parkı eşitlik raporunun kabulü',
  'Bağlar Belediye Meclisi, Kadın Erkek Eşitlik Komisyonunun Nevroz Parkı hakkındaki raporunu 8 Ocak’ta kabul etti.',
  'Raporda parkın tuvalet temizliği, güvenlik, emzirme odası, mescit ve kanal güvenliği hakkında kullanıcı görüşleri var. Fiziki uygulama açık.',
  'Parka ilişkin komisyon bulgularıyla önceki eşitlik hedefini bağlayan tarihli parti kaydı ve sonraki çalışma araştırılıyor.',
  (('review','action','Komisyon Bağcılar’daki Nevroz Parkı’nın eşit kullanımını inceledi.'),
   ('needs','action','Raporda kadın kullanıcıların güvenlik ve emzirme odasına ilişkin görüşleri yer aldı.'),
   ('channel','action','Komisyon kullanıcıların mescit ve park kanalında güvenlik tedbiri önerilerini kaydetti.'),
   ('approved','result','Meclis 8 Ocak’ta Nevroz Parkı raporunu kabul etti.'))),
 ('19','2015-01-08','egitime-erisim','Bağlar Eğitim Destek Evi ihtiyaç raporunun kabulü',
  'Bağlar Belediye Meclisi 8 Ocak’ta Eğitim Destek Evi’nin yeni dönem ihtiyaçlarına ilişkin raporu kabul etti.',
  'Raporda test ve deneme sınavı alımları için 11.000 TL ve Kobanili 100 çocuk için kırtasiye ihtiyacı belirtiliyor. Satın alma ve teslim kayıtları açık.',
  'İhtiyaç raporu ile önceki tarihli parti eğitim hedefi ve yeni dönem teslimi arasında kaynak zinciri araştırılıyor.',
  (('purpose','action','Eğitim ve Araştırma Komisyonu Eğitim Destek Evi ihtiyaçlarını değerlendirdi.'),
   ('amount','action','Raporda sınav alımları 11.000 TL ve 100 çocuk için kırtasiye ihtiyacı olarak yazıldı.'),
   ('approved','result','8 Ocak’ta meclis Eğitim Destek Evi ihtiyaç raporunu kabul etti.'))),
 ('21','2015-01-08','yerel-demokrasi','Şeyhşamil sakinlerinin sokak bakım talepleri',
  'Bağlar Belediye Meclisi, Şeyhşamil sakinlerinin sorunlarıyla ilgili Halkla İlişkiler Komisyonu raporunu 8 Ocak’ta kabul etti.',
  'Rapor on iki sokakta asfalt ve kaldırım onarımı öngörüyor. Belediye iş emri, ihale ve tamamlanma kaydı açık.',
  'Sakinlerin sorunları ve meclis raporu kaynaklandı. Doğrudan tarihli önceki parti taahhüdü ve işin sonucu araştırılıyor.',
  (('purpose','action','Komisyonun görevi Şeyhşamil sakinlerinin mahalle sorunlarını dinlemekti.'),
   ('repairs','action','Raporda belirtilen sokaklarda asfalt ve kaldırım onarımı yapılması öngörüldü.'),
   ('approved','result','8 Ocak’ta meclis sokak onarımlarını öngören raporu kabul etti.'))),
 ('232','2015-11-06','spor','Bağlar kadın basketbol takımı araştırmasının komisyona sevki',
  'Bağlar Belediye Meclisi 6 Kasım’da ikinci lig kadın basketbol takımının faaliyetlerine ilişkin araştırmayı Gençlik ve Spor Komisyonuna sevk etti.',
  'Sevk kararı araştırma ve raporlama aşaması. Takip raporu, bütçe ve sporcu sonuçları açık.',
  'Takımın çalışmaları hakkında tarihli parti hedefi ve komisyona sevkten sonraki dosya araştırılıyor.',
  (('subject','action','Önergede belediyenin ikinci lig kadın basketbol takımının faaliyetlerinin incelenmesi istendi.'),
   ('committee','action','Araştırmanın Gençlik ve Spor Komisyonuna havalesi ile rapor sonrası meclis görüşmesi öngörüldü.'),
   ('approved','result','6 Kasım’da takımın faaliyetlerinin araştırılması için komisyon sevki kabul edildi.'))),
)
for number,day,topic,title,context,detail,reason,anchors in events:
    stem='0409-baglar-services-'+number
    limit=detail+' '+context_limits
    evidence = [(stem+'-file','initiative','document',f'2015/{number} sayılı meclis işlemi {title.lower()} hakkında.'),
                (stem+'-day','initiative','document',f'2015/{number} kararının yazılı tarihi {day}.')]
    evidence.extend((stem+'-'+suffix,stage,'document',claim) for suffix,stage,claim in anchors)
    eid=event(stem,day,title,context,evidence,limit)
    records['practice_event'][-1]['common_event_key']='baglar-belediye-meclisi-2015-'+number
    evidence_ids=[item[0] for item in evidence]
    scope=readings(topic,'event',evidence_ids+electoral_context)
    candidate=stem+'-unmatched'
    records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,
        relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(evidence_ids)))
    task('practice_candidate',candidate,reason,limit)

for entry in entries:
    destination=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in destination:
        destination.append(entry['values'])
for table,rows in records.items():
    destination=snapshot.setdefault(table,[])
    destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot, records, [entry['values']['id'] for entry in entries if entry['kind']=='passage'], party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limitation,result='reviewed',
        reason=kind+' hedefinin kaynak metni, tarihi ve iddia sınırları okundu. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('baglar-services-draft.json',package),('baglar-services-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
