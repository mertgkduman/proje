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
aux=read(here/'pension-floor-source-records.json')
party=aux['party_id']
package=read(data/f'practices/04-{party}.json')
review=read(data/f'practices/04-{party}-review.json')
snapshot=read(data/'releases'/package['base_release']/'records.json')
inventory=read(data/'practices/04-inventory.json')
entries=package['entries']; entries.extend(aux['entries'])
entries.extend(read(here/'pension-floor-final-source-records.json')['entries'])
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
        aid=f'pension-floor-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='İlgili politika söylemi, önerge veya kanun teklifi.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='İmzalı teklif veya önerge, TBMM kayıt sayfası ve tutanak.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'iyi'
topic = 'sosyal-guvenlik'
stem = '0407-iyi-2026-7573'
p = '0407-floor-'
before = p+'iyi-7573-49-'
vote = p+'iyi-7573-50-'
ballot = p+'iyi-7573-ballot-'
commission = p+'iyi-7573-commission-'
bill = p+'pension-bill-23464-'
law = p+'pension-law-7573-'
text = p+'pension-text-7573-'
st = stem+'-statement'
target = stem+'-target'
quote = stem+'-quote'
goal = ('Erhan Usta, İYİ Parti Grubu adına en düşük emekli aylığının asgari ücret düzeyinde olmasını parti politikası olarak açıkladı.')
limit = ('Komisyonun 5. maddesi, Genel Kurulun 7. maddesi ve teklifin tümü üzerindeki açık oy ayrı. '
         'Komisyon önergesi için kişi bazında oy sayısı ve aylıkların fiilî ödeme kayıtları açık.')
finding(target,goal,[before+'usta',before+'quote'],'49. Birleşimde temsil sıfatı ve alt aylık eşiği aynı konuşmada kontrol edildi.')
finding(quote,passages[before+'quote']['exact'],[before+'quote'],
    'Tutanakta yer alan kısa birebir politika ifadesi.',pair=target)
records['practice_statement'].append(dict(id=st,party_id=party,topic_id=topic,taxonomy_version=4,
   summary_finding_id=target,quote_finding_id=quote,statement_at='2026-01-21',date_precision='day',
   version_id=passages[before+'quote']['version_id'],period_basis='21 Ocak tarihli 49. Birleşimde İYİ Parti Grubu adına konuşma.',
   uncertainty_reason=None,comparison_row_id='04-03-v3-0306-iyi-program-sosyal-guvenlik-row'))
readings(topic,'statement',[before+'usta',before+'quote',before+'committee',commission+'amendment'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[before+'quote']['exact'])):
    task(kind,st,claim,'Genel Kurulda Usta’nın, Komisyonda Türkeş Taş’ın İYİ Parti adına açıkladığı aylık eşiği.')
evidence = [
    (bill+'id','initiative','document','2/3464 esas numaralı teklif TBMM kaydında.'),
    (commission+'amendment','initiative','document','15 Ocak Komisyonda Usta ve Türkeş Taş 5. madde için 25.000 TL önerdi. Komisyon kabul etmedi.'),
    (before+'amendment','initiative','document','49. Birleşimde 20.000 TL yerine 25.000 TL yazılması önerildi.'),
    (before+'signers','initiative','document','Bu Genel Kurul önergesinde altı milletvekilinin adı var.'),
    (vote+'accept','action','document','50. Birleşim Başkanı teklifin tümü üzerinde kabulü açıkladı.'),
    (vote+'tally','result','document','Tutanakta 426 oyun 247’si kabul ve 179’u ret olarak açıklandı.'),
    (ballot+'tally','result','document','Kesin cetvelde 245 kabul ve 179 ret var.'),
    (ballot+'duplicates','result','document','Kesin cetvelde iki mükerrer oy ve 426 toplam var.'),
    (ballot+'usta','action','document','Erhan Usta kesin cetvelde KATILMADI olarak kayıtlı.'),
    (ballot+'turkes','action','document','Ayyüce Türkeş Taş kesin cetvelde ret oyu kullanmış görünüyor.'),
    (ballot+'fakibaba','action','document','Ahmet Eşref Fakıbaba kesin cetvelde pusulayla ret oyu kullanmış görünüyor.'),
    (law+'day','result','document','TBMM kanun kaydında kabul günü 23 Ocak 2026.'),
    (bill+'law','result','document','2/3464 yasama kaydı 7573 sayılı kanuna bağlı.'),
    (text+'floor','result','document','7573 sayılı kanunun 7. maddesi 16.881 TL yerine 20.000 TL belirliyor.'),
    (text+'effect','result','document','7. madde Ocak 2026 ödeme döneminden itibaren uygulanmak üzere düzenlendi.'),
]
eid = event(stem,'2026-01-23','2/3464’ten çıkan 7573 sayılı kanunda en düşük emekli aylığı',
    'TBMM 2/3464 teklifini kabul etti. 7573 sayılı kanunun 7. maddesinde 20.000 TL tutarı yer aldı.',evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-4-050-2-3464-7573',
    occurrence_basis='50. Birleşim tutanağı ve kesin cetvel, 2/3464 yasama kaydı ve 7573 sayılı kanun metni.')
refs = [row[0] for row in evidence]
scope = readings(topic,'event',[*refs,before+'defense',before+'rejection',vote+'close',law+'session'])
rid = stem+'-relation'
result = stem+'-result'
exp = stem+'-explanation'
compare = 'İYİ Parti beyanı, 25.000 TL değişiklik önerisi ve 7573 sayılı kanunun 7. maddesi aynı aylık ödeme alt sınırına ilişkin.'
outcome = ('TBMM 23 Ocak 2026’da teklifi kabul etti. Genel Kurulda 247 kabul ve 179 ret açıklandı. '
           'Kesin cetvel 245 kabul, 179 ret ve 2 mükerrer oy gösteriyor. 7. madde, 20.000 TL tutarını '
           'Ocak 2026 ödeme döneminden itibaren geçerli olacak şekilde düzenledi.')
explanation = ('Erhan Usta en düşük emekli aylığının asgari ücret düzeyinde olmasını parti politikası olarak açıkladı. '
               'Komisyon 15 Ocak’ta Usta ve Ayyüce Türkeş Taş’ın 25.000 TL önergesini reddetti. '
               'Genel Kurul 21 Ocak’ta altı milletvekilinin ayrı 25.000 TL önergesini kabul etmedi. '
               'Teklifin tümü için kesin cetvelde Usta KATILMADI, Türkeş Taş RET ve Fakıbaba pusulayla RET olarak kayıtlı. '
               '7573 sayılı kanunun 7. maddesi 20.000 TL belirledi.')
finding(result,outcome,[vote+'tally',vote+'accept',ballot+'tally',ballot+'duplicates',law+'day',text+'floor',text+'effect'],
    'Oturumda açıklanan toplam ile kesin açık oy cetvelini, kanun kimliğini ve yürürlük hükmünü özgün kayıtlarda okuduk.')
finding(exp,explanation,[before+'quote',commission+'amendment',before+'amendment',before+'signers',before+'rejection',
    ballot+'usta',ballot+'turkes',ballot+'fakibaba',text+'floor'],
    'Politika beyanı, komisyon ve Genel Kurul önergeleri, adla kayıtlı oy ve kabul edilen hüküm birlikte okundu.')
records['practice_relation'].append(dict(id=rid,statement_id=st,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,
    comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=exp,
    temporal_context='15 Ocak komisyon ve 21 Ocak Genel Kurul önergesi, 23 Ocak teklifin tümü üzerindeki oylama.',
    authority_context='Usta İYİ Parti Grubu adına konuştu. Komisyon ve Genel Kurul önergelerinin imzacıları ayrı. Cetveldeki oylar kişilere ait.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',explanation),('practice_relation.target_finding_id',goal),
                   ('practice_relation.result_finding_id',outcome),('practice_relation.explanation_finding_id',explanation)):
    task(kind,rid,claim,limit)
dispute = stem+'-roll-call-dispute'
summary = dispute+'-finding'
detail = ('Genel Kurul tutanağı 247 kabul ve 179 ret açıkladı. Kesin cetvel 245 kabul, 179 ret ve 2 mükerrer oy '
          'gösteriyor. İki kayıtta da toplam 426 ve teklifin kabulü aynı.')
finding(summary,detail,[vote+'tally',ballot+'tally',ballot+'duplicates'],
    'Tutanak ve kesin cetveldeki toplamlar ayrı ayrı okundu.')
records['practice_dispute'].append(dict(id=dispute,event_id=eid,summary_finding_id=summary,
    supported_points='Toplam 426, ret 179 ve teklif kabul edildi.',
    disputed_points='Oturum tutanağında 247 kabul. Kesin cetvelde 245 kabul ve iki mükerrer oy.',
    unresolved_points='Tutanak ve kesin sonuç cetvelinde kabul sayısının farklı basamakta kaydedildiği görülüyor.'))
task('practice_dispute',dispute,detail,'Kesin cetvelde iki pusula mükerrer olarak işaretlendi.')
task('practice_dispute.summary_finding_id',dispute,detail,'Her iki resmî kayıt yan yana gösteriliyor.')
for pid,role,point in (
    (vote+'tally','conflict','Oturum duyurusu 247 kabul ve 179 ret.'),
    (ballot+'tally','support','Kesin cetvel 245 kabul ve 179 ret.'),
    (ballot+'duplicates','support','Kesin cetvelde 2 mükerrer oy ve 426 toplam.'),
):
    pos=passages[pid]['section']
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,point=point,source_position=pos,role=role))
    task('practice_dispute_evidence','|'.join((dispute,pid,point,role)),point,pos)

for entry in entries:
    dest=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in dest: dest.append(entry['values'])
for table,rows in records.items():
    dest=snapshot.setdefault(table,[])
    dest.extend(row for row in rows if row not in dest)
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
        reason=kind+' hedefinin asıl kaynakları, tarihi ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('pension-floor-final-draft.json',package),('pension-floor-final-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
