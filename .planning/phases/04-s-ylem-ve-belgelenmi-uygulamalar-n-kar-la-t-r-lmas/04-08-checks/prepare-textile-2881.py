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
aux=read(here/'textile-2881-source-records.json')
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
            boundary_reason='İlgili politika söylemi ve TBMM işlem zinciri dar kapsamda incelendi.'))
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
        aid=f'textile-2881-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='İlgili politika söylemi, önerge veya kanun teklifi.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,key,day,title,context,basis_text,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=key,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis=basis_text))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid

assert party=='yeni-yol'
assert sha256((data/'practices/04-yeni-yol.json').read_bytes()).hexdigest()=='bfac1eb8536806f1e620581c42cf3d7621e7a817fc9043899bae7155dea94073'
assert sha256((data/'practices/04-yeni-yol-review.json').read_bytes()).hexdigest()=='c63d39dd1b93653e7e7fa8de8580e349b86a6f752f0564e0d75be6aa4c212416'
stem='0408-textile-2881'
prefix=stem+'-'
topic='sanayi-politikasi'
authority=prefix+'floor-role'
limit=('Gündem önerisinin reddi 2 Temmuz 104. Birleşime ait. Esas kaydı 23 Kasım erişiminde Gündemde. '
       'Tek tek üyelerin oyu ve araştırmanın açılış kararı açık.')
points=(
    ('register-number','initiative','TBMM esas numarası 10/2881.'),
    ('register-day','initiative','Araştırma önergesi 2 Temmuz 2025 günü Başkanlığa ulaştı.'),
    ('register-sponsor','initiative','Esas sicili Mehmet Emin Ekmen ve 21 milletvekili kaydediyor.'),
    ('signed-number','initiative','İmzalı dosyanın ilk sayfasında 10/2881 yer alıyor.'),
    ('signed-scope','initiative','İmzalı gerekçe finansman, ihracat kaybı, istihdam ve iç göç etkilerinin incelenmesini istiyor.'),
    ('signed-signer','initiative','Son tarama sayfasının imza tablosunda Ekmen’in Mersin satırı var.'),
    ('floor-agenda','action','Yeni Yol Grubu aynı gün ön görüşme talep etti.'),
    ('floor-role','action','Başkan Yeni Yol Grubu adına Mehmet Emin Ekmen’e söz verdi.'),
    ('floor-vote','result','Başkan gündem talebinin kabul edilmediğini açıkladı.'),
    ('register-pending','result','TBMM esas sicili erişim gününde Gündemde gösteriyor.'),
    ('collected-filed','result','9 Temmuz Gelen Kâğıtlarda önerge 26. sırada ve geliş tarihi 2 Temmuz.'),
)
evidence=[(prefix+pid,stage,'document',claim) for pid,stage,claim in points]
context=('Yeni Yol Grubu, Mehmet Emin Ekmen ve 21 milletvekilinin tekstil sektörüne ilişkin 10/2881 araştırma önergesinin ön görüşmesinin 2 Temmuz 2025 birleşiminde yapılmasını istedi. Genel Kurul bu gündem talebini reddetti.')
eid=event(stem,'tbmm-28-3-104-10-2881-gundem','2025-07-02','10/2881 tekstil araştırmasının ön görüşme talebinin reddi',context,
    'TBMM 28. Dönem 3. Yasama Yılı 104. Birleşim tam tutanağı, imzalı 10/2881 önergesi ve TBMM esas kaydı.',evidence,limit)
refs=[row[0] for row in evidence]
numbers=[prefix+name for name in ('signed-first-value','signed-rationale-value','floor-export')]
scope=readings(topic,'event',refs+numbers)
person,actor,contribution,fid=(prefix+suffix for suffix in ('person','actor','contribution','finding'))
new('person',id=person,name='Mehmet Emin Ekmen')
new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,authorization_passage_id=authority)
body=('Mehmet Emin Ekmen 2 Temmuz’da Yeni Yol Grubu adına tekstil araştırmasının ön görüşülmesi talebini açıkladı. '
      'Finansmana erişim, hazır giyim ihracatı ve istihdam konularını ele aldı. Başkan gündem talebinin reddini duyurdu.')
finding(fid,body,refs,'İlk gündem önerisi, başkanın grup adına söz vermesi ve oylama sonucu birlikte okundu.')
records['practice_contribution'].append(dict(id=contribution,event_id=eid,party_id=party,actor_id=actor,
    contribution_kind='task',finding_id=fid,authority_passage_id=authority,membership_passage_id=None,
    responsibility_limit='Temsil görevi 104. Birleşimin birinci grup gündem önerisine ait. Kişisel oy ve araştırmanın yürütülmesi açık.'))
records['practice_actor_period'].append(dict(contribution_id=contribution,valid_from='2025-07-02',valid_to='2025-07-02',identity_passage_id=authority))
task('practice_contribution',contribution,body,limit)
task('practice_contribution.finding_id',contribution,body,limit)

dispute=prefix+'export-dispute'
dispute_finding=prefix+'export-dispute-finding'
detail=('2023 hazır giyim ihracatı önergenin ön yazısında ve Ekmen’in birleşimdeki sözünde 19,3 milyar dolar, '
        'aynı imzalı belgenin özet gerekçesinde 19,2 milyar dolar. Farkın tanım veya yuvarlamadan kaynaklanıp kaynaklanmadığı açık.')
finding(dispute_finding,detail,numbers,'Aynı yıl ve sektör için optik değerler ve sözlü açıklama ayrı kontrol edildi.')
records['practice_dispute'].append(dict(id=dispute,event_id=eid,summary_finding_id=dispute_finding,
    supported_points='Ön yazı ve Genel Kurul konuşmasında 2023 hazır giyim ihracatı 19,3 milyar dolar olarak verildi.',
    disputed_points='Özet gerekçede aynı yıl için 19,2 milyar dolar yer alıyor.',
    unresolved_points='Özgün seri, tanım ve yuvarlama kuralı açık. İhracat ölçümünün kesin değeri için ayrı veri kaynağı gerekli.'))
task('practice_dispute',dispute,detail,limit)
task('practice_dispute.summary_finding_id',dispute,detail,limit)
for pid,role,point in (
    (numbers[0],'support','Ön yazı 2023 hazır giyim ihracatını 19,3 milyar dolar olarak veriyor.'),
    (numbers[1],'conflict','Özet gerekçe 2023 hazır giyim ihracatını 19,2 milyar dolar olarak veriyor.'),
    (numbers[2],'support','Ekmen aynı birleşimde 19,3 milyar doları ifade ediyor.'),
):
    section=passages[pid]['section']
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,point=point,source_position=section,role=role))
    task('practice_dispute_evidence','|'.join((dispute,pid,point,role)),point,limit)

reason='10/2881 gündem önerisinin reddi kayıtlı. Önceki tarihli ve Yeni Yol Grubu adına ayrı bir tekstil söylemi açık.'
candidate=prefix+'candidate'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,relation_id=None,state='unmatched',
    reason=reason,passage_ids=encoded(refs)))
task('practice_candidate',candidate,reason,limit)

reply_limit=('7/29149 Ekmen’in imzalı bireysel yazılı sorusu. Yazılı belgede Mersin milletvekilliği ve DEVA sıfatı var. '
             'Ticaret Bakanlığı cevabı genel destek ve dış ticaret uygulamalarını bildiriyor. İstenen il ve sektör kırılımları ile '
             'firma ya da çalışan bazında ödeme açık. 10/2881 araştırma dosyası ayrı.')
reply_points=(
    ('question-register-number','initiative','Soru esas numarası 7/29149.'),
    ('question-register-filed','initiative','Soru 4 Haziran 2025’te TBMM’ye ulaştı.'),
    ('question-request','initiative','Ekmen 4 Haziran tarihli imzasıyla Ticaret Bakanından yazılı cevap istedi.'),
    ('question-role','initiative','Belgede Mersin milletvekilliği ve DEVA Partisi genel başkan yardımcılığı ibareleri var.'),
    ('question-counts','initiative','Konkordato sayısı ve il dağılımı istendi.'),
    ('question-financing','initiative','Yürütülen ve planlanan destek programları soruldu.'),
    ('question-debt','initiative','Onuncu soru borç yapılandırması güçlüklerini ele alıyor.'),
    ('reply-number','action','Ticaret Bakanlığı imzalı cevabı 7/29149 sayısını taşıyor.'),
    ('question-register-day','action','TBMM cevap bildirilişini 9 Temmuz 2025 olarak kaydetti.'),
    ('question-register-late','result','TBMM, Süresi Geçtikten Sonra Cevaplandı durumunu gösteriyor.'),
    ('reply-tariff','result','Bakanlık hazır giyim ithalatında yaklaşık yüzde 51 gümrük vergisi uygulamasını açıkladı.'),
    ('reply-aggregate','result','2024 mal ihracatı için bildirilen 17,6 milyar TL genel destek tutarı.'),
    ('reply-kosgeb','result','Bakanlık belirtilen koşulları sağlayan emek yoğun sektör KOBİ’lerinde çalışan başına aylık 2.500 TL destek bildirdi.'),
    ('reply-bankruptcy','result','Ticaret Bakanlığı konkordato başvuru kaydının kendisinde bulunmadığını söyledi.'),
    ('reply-sector','result','Cevapta MERSİS verilerinde sektör kırılımı tutulmadığı yazıyor.'),
)
reply_refs=[(prefix+pid,stage,'document',claim) for pid,stage,claim in reply_points]
reply_context=('Ticaret Bakanlığının Mehmet Emin Ekmen’in 4 Haziran tarihli 7/29149 sorusuna verdiği yanıt '
               '9 Temmuz 2025’te TBMM siciline süre geçtikten sonra bildirildi. Bakanlık gümrük ve ihracat desteklerini, '
               'belirli KOBİ’lerde çalışan başına aylık 2.500 TL desteği ve konkordato kayıtlarının kapsamını açıkladı.')
reply_event=event(prefix+'29149','tbmm-28-3-7-29149-tekstil-cevap','2025-07-09','7/29149 tekstil sorusuna bildirilen Bakanlık cevabı',reply_context,
    'TBMM soru sicili, Ekmen imzalı on soru ve beş sayfalık Ticaret Bakanlığı cevabı.',reply_refs,reply_limit)
reply_pids=[row[0] for row in reply_refs]
reply_scope=readings(topic,'event',reply_pids)
reply_candidate=prefix+'29149-candidate'
reply_reason=('Bireysel 7/29149 sorusu ile süre dışı Ticaret Bakanlığı cevabı eşleşiyor. '
              'Bakana sunulan sorular için şirket, il ve çalışan dağılımı ile önceki ayrı grup söylemi açık.')
records['practice_candidate'].append(dict(id=reply_candidate,scope_id=reply_scope,event_id=reply_event,relation_id=None,state='unmatched',
    reason=reply_reason,passage_ids=encoded(reply_pids)))
task('practice_candidate',reply_candidate,reply_reason,reply_limit)

for entry in entries:
 destination=snapshot.setdefault(entry['kind'],[])
 if entry['values'] not in destination:destination.append(entry['values'])
for table,rows in records.items():
 destination=snapshot.setdefault(table,[]);destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot,records,[entry['values']['id'] for entry in entries if entry['kind']=='passage'],party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
 pids,owners=targets[(kind,identity)];assert party in owners
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),supported_claim=claim,limitations=limitation,result='reviewed',reason=kind+' kaynak metni, tarih ve kapsam sınırları okundu. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews];package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('textile-2881-draft.json',package),('textile-2881-review-draft.json',review)]:
 path=here/name
 with path.open('x') as output:output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
 print(name,sha256(path.read_bytes()).hexdigest())
print('YENI_YOL_TEXTILE_SEMANTIC_PASS',len(tasks))
