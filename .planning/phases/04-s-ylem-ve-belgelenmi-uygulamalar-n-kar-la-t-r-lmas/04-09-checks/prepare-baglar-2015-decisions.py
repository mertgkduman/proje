"""Record six individually dated Bağlar municipal proceedings."""

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
aux=read(here/'baglar-2015-decisions-source-records.json')
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
        aid=f'baglar-2015-decisions-reading-{lane}-{topic}-{vid}'
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
src = '0409-baglar-2015-'
electoral_context = ['0409-siginak-ysk-district-name','0409-siginak-ysk-district-party']
context_limits = ('YSK kaydı yönetimin 2014 seçim bağlamını veriyor. '
                  'İşlem belediye meclisine ait. Parti adına bağımsız bir karar veya kişisel oy açık.')
events = (
 ('1','2015-01-06','yerel-hesap-denetimi','Bağlar Denetim Komisyonunun 2015 seçimi',
  'Bağlar Belediye Meclisi 2015/1 sayılı kararla Denetim Komisyonunun beş üyesini gizli oyla seçti.',
  'Tutanak 35 oy ve bir boş oyu kaydediyor. Dört seçilen üye 34’er ve bir üye 33 oy aldı. Denetim raporu ayrı.',
  'Seçim öncesinde bu komisyona ilişkin tarihli parti hedefi ve komisyonun sonraki raporu açık.',
  (('audit-file','initiative','6 Ocak tarihli 2015/1 kararı Denetim Komisyonu seçimine ilişkin.'),
   ('audit-ballot','action','Karar, gizli oy ve bir boş oy dahil kullanılan toplam 35 oyu kaydediyor.'),
   ('audit-result','result','Dört aday 34’er, bir aday 33 oyla Denetim Komisyonuna seçildi.'))),
 ('20','2015-01-08','sosyal-hizmet','Bağlar’da kadın konuk evi hizmetleri hakkında rapor kabulü',
  'Bağlar Belediye Meclisi 2015/20 sayılı kararla kadın konuk evi hizmetlerini de ele alan Kültür Komisyonu raporunu kabul etti.',
  'Rapor 2014 Aralık incelemesine dayanıyor. Kadın Konuk Evi ile Kardelen danışmanlığını ayrı birimler olarak anlatıyor. Açılış ve toplam kullanıcı sayısı açık.',
  'Belediye raporu hizmet anlatımı ve kabul aşamasını gösteriyor. Daha erken aynı kapsamda tarihli parti taahhüdü araştırmaya açık.',
  (('shelter-file','initiative','8 Ocak tarihli işlem 2015/20 numaralı Kültür Komisyonu raporuna ilişkin.'),
   ('shelter-prior','action','Komisyon Aralık 2014 incelemesi sonrasında rapor hazırladı.'),
   ('shelter-services','action','Rapor konuk evinde destek ve danışmanlık verildiğini aktarıyor.'),
   ('shelter-approved','result','Meclis 8 Ocak’ta hazır bulunanların oybirliğiyle raporu kabul etti.'))),
 ('49','2015-02-06','mali-butce','Bağlar Belediyesinin 6 Şubat kredi yetkisi',
  'Bağlar Belediye Meclisi, 2015/49 sayılı kararla Belediye Başkanı Birsen Kaya Akat’a faiz hariç 3,5 milyon TL kredi alma yetkisi verdi.',
  'Yetki yatırım harcamaları ve cari borç ödemeleri için. Kullanılan kredi tutarı, faiz ve Ağustos kararıyla ilişkisi açık.',
  'Şubat kararı için çekim ve banka sözleşmesi, ayrıca tarihli parti mali taahhüdü araştırılıyor.',
  (('feb-loan-file','initiative','2015/49, 6 Şubat’taki kredi yetkisi işlemi.'),
   ('feb-loan-amount','action','Yatırım ve cari borçlar için faiz hariç 3,5 milyon TL kredi yetkisi görüşüldü.'),
   ('feb-loan-approved','result','Meclis Şubat’taki kredi yetkisini oybirliğiyle kabul etti.'))),
 ('99','2015-05-05','yerel-hesap-denetimi','Bağlar’ın 2014 temizlik bütçesi raporunun kabulü',
  'Bağlar Belediye Meclisi 2015/99 sayılı kararla Temizlik İşleri Müdürlüğünün 2014 bütçe harcamaları hakkındaki raporu kabul etti.',
  'Komisyon 24.720.000 TL ödenek, 23.025.318,56 TL harcama ve 1.694.681,44 TL iade bildirdi. '
  'Sayfadaki 25 harcama satırının basit toplamı 25.397.402,56 TL. Satırların sınıflaması ve dayanak muhasebe açık.',
  'Meclis raporu kabulü kayıtlı. Harcama satırlarının toplam farkı, muhasebe dayanağı ve önceki parti söylemi araştırılıyor.',
  (('spending-file','initiative','2015/99, Plan ve Bütçe Komisyonu temizlik harcaması raporunun işlem numarası.'),
   ('spending-budget','action','Komisyon yıllık temizlik bütçesini 24.720.000 TL olarak bildirdi.'),
   ('spending-total','action','Komisyon yazılı sonuçta 23.025.318,56 TL harcama ve 1.694.681,44 TL iade aktardı.'),
   ('spending-items','action','Hizmet alımı satırı aynı sayfadaki tek tek harcama kalemlerinden biri.'),
   ('spending-approved','result','Meclis 5 Mayıs’ta temizlik bütçesi raporunu oybirliğiyle kabul etti.'))),
 ('161','2015-08-07','mali-butce','Bağlar Belediyesinin 7 Ağustos kredi yetkisi',
  'Bağlar Belediye Meclisi 2015/161 sayılı kararla Belediye Başkanı Birsen Kaya Akat’a faiz hariç 3,5 milyon TL kredi alma yetkisi verdi.',
  'Ağustos yetkisi Şubat’taki yetkiden ayrı kayıtta. İki yetkinin tek krediye veya ayrı işlemlere ilişkin olup olmadığı açık.',
  'Ağustos kararının önceki yetki ve fiilî krediyle ilişkisi ile tarihli parti mali hedefi araştırılıyor.',
  (('aug-loan-file','initiative','2015/161, 7 Ağustos’taki ayrı kredi yetkisi işlemi.'),
   ('aug-loan-amount','action','Ağustos kararı faiz hariç 3,5 milyon TL kredi yetkisi öngördü.'),
   ('aug-loan-approved','result','Meclis Ağustos’taki kredi yetkisini oybirliğiyle kabul etti.'))),
 ('214','2015-11-04','sosyal-hizmet','Bağlar’da Kardelen kursları hakkında rapor kabulü',
  'Bağlar Belediye Meclisi 2015/214 sayılı kararla Kardelen-1’deki eğitsel faaliyetler hakkındaki komisyon raporunu kabul etti.',
  '2015/187 araştırma sevki ayrı karar. Rapor protokolün sona ermesinden sonra eylül itibarıyla kursların tekrar açılamadığını '
  've önceki yıllık protokol döneminde 97 kadının yararlandığını bildiriyor. Yeni kurs ve protokol belgesi açık.',
  'Kursların kapsamı raporda, süre sonunda yeniden açılma durumu ve karşılaştırılabilir önceki parti söylemi araştırmaya açık.',
  (('courses-referral','initiative','2015/187 ile eğitsel faaliyetler incelemesi 11 Eylül’de komisyona sevk edildi.'),
   ('courses-file','action','4 Kasım’da aynı konu 2015/214 sayılı komisyon raporu olarak görüşüldü.'),
   ('courses-expiry','action','Raporda protokol süresi dolduktan sonra kursların yeniden açılamadığı bildirildi.'),
   ('courses-total','action','Rapor önceki protokol dönemi için 97 yararlanıcı bildirdi.'),
   ('courses-approved','result','Meclis 4 Kasım’da Kardelen eğitim raporunu oybirliğiyle kabul etti.'))),
)
for number,day,topic,title,context,limit,reason,points in events:
    stem = src+number
    limit=limit+' '+context_limits
    evidence=[(src+key,stage,'document',claim) for key,stage,claim in points]
    eid=event(stem,day,title,context,evidence,limit)
    records['practice_event'][-1]['common_event_key']='baglar-meclis-2015-'+number
    evidence_ids=[row[0] for row in evidence]
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
for name,content in [('baglar-2015-decisions-draft.json',package),('baglar-2015-decisions-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
