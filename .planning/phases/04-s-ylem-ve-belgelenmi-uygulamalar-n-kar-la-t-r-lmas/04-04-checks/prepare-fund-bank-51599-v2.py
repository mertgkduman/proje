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
aux=read(here/'fund-bank-51599-source-records.json')
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
            boundary_reason='Banka izinleri, fiilî başlangıç ve fon ödemeleri hakkında yazılı denetim kaydı incelendi.'))
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
        aid=f'fund-bank-51599-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='TBMM esas kaydı, imzalı yazılı soru ve tarihli Gelen Kâğıtlar.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'yeni-parti'
topic = 'makroekonomik-politika'
stem = '0404-yeni-parti-2026-bank-51599'
src = '0404-bank-51599-'
limit = ('Soru 19 Ekim tarihli, TBMM’ye geliş 20 Ekim ve Gelen Kâğıtlar yayımı 5 Kasım. '
         'Kapsam kesiminde cevaba ve son durum ilanının gününe ilişkin tarihli belge açık. '
         'Önerge dört bankanın işlemlerini ve fon ödemelerini soruyor. Sorulardaki iddia ve tutarlar ayrı kaynak gerektiriyor.')
context = ('Mustafa Sezgin Tanrıkulu, 7/51599 ile Hazine ve Maliye Bakanı’na kuruluş ve faaliyet izinlerini, '
           'fiilî faaliyete geçişi ve fon yatırımcılarının zararlarına ilişkin finansman ve denetimi sordu.')
evidence = [
    (src+'signed-group','initiative','document','19 Ekim tarihli imzalı metin Yeni Parti grup başlığını taşıyor.'),
    (src+'signed-permit','initiative','document','Soru metni 11424 sayılı faaliyet iznini ve 4 Mart yayımını anıyor.'),
    (src+'signed-risk','initiative','document','Soru 9 fiilî faaliyete geçilmesi ve risk bildirim tarihlerini soruyor.'),
    (src+'signed-payments','initiative','document','Soru 18 beklenen aktarım, tahsil ve ödeme tutarlarını ayrı istiyor.'),
    (src+'register-filed','action','document','TBMM 7/51599’un Başkanlığa geliş gününü 20 Ekim olarak kaydetti.'),
    (src+'register-ministry','action','document','Soru Hazine ve Maliye Bakanına yöneltildi.'),
    (src+'gelen-question','result','document','5 Kasım Gelen Kâğıtları 7/51599’u 69. soru olarak yayımladı.'),
]
eid = event(stem,'2026-10-20','7/51599 banka izinleri ve fon ödemeleri yazılı sorusu',context,evidence,limit)
records['practice_event'][-1]['common_event_key'] = 'tbmm-28-5-7-51599-filing'
refs = [r[0] for r in evidence]
scope = readings(topic,'event',refs+[
    src+'register-id',src+'gelen-date',src+'gelen-other',src+'signed-public',
    src+'bd-summary-permit',src+'bd-summary-declined',src+'bd-summary-transfer',
])
reason = ('7/51538 farklı muhatapla TLY’nin işlemlerini soruyor. 7/51599 banka izinleri ve finansmana odaklanıyor. '
          'Bu özel soru için daha erken tarihli karşılaştırılabilir parti söylemi araştırmaya açık.')
records['practice_candidate'].append(dict(id=stem+'-unmatched',scope_id=scope,event_id=eid,relation_id=None,
    state='unmatched',reason=reason,passage_ids=encoded(refs)))
task('practice_candidate',stem+'-unmatched',reason,limit)

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
for name,content in [('fund-bank-51599-v2-draft.json',package),('fund-bank-51599-v2-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
