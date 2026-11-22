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
aux=read(here/'pension-floor-final-complete-source-records.json')
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
        aid=f'final-pension-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='İlgili politika söylemi, önerge veya kanun teklifi.',state='examined',attempt_ids=encoded([aid])))
    return sid
assert party == 'saadet'
topic = 'sosyal-guvenlik'
stem = '0411-saadet-2026-7573'
eid, rid = (stem+'-event', stem+'-relation')
session = '0411-floor-iyi-7573-50-'
ballot = '0411-floor-iyi-7573-ballot-'
event = next(row for row in records['practice_event'] if row['id']==eid)
assert event['common_event_key']=='tbmm-28-4-050-2-3464-7573'
detail = ('Genel Kurul tutanağında 247 kabul ve 179 ret açıklandı. Kesin cetvel 245 kabul, 179 ret ve '
          '2 mükerrer oy gösteriyor. Mahmut Arıkan teklifin tümü üzerindeki oylamada KATILMADI olarak kayıtlı.')
limit = ('Arıkan’ın 21 Ocak politika açıklaması ile 23 Ocak kişisel oy cetveli ayrı kayıtlar. '
         'Kanunlaşan teklif 2/3464. 2/3456’nın sonucu ve fiilî aylık ödemeleri ayrı araştırılıyor.')
sources = (
    (session+'tally','result','Tutanakta 247 kabul ve 179 ret açıklandı.'),
    (session+'accept','action','Birleşim Başkanı teklifin kabulünü açıkladı.'),
    (ballot+'tally','result','Kesin cetvelde 245 kabul ve 179 ret var.'),
    (ballot+'duplicates','result','Kesin cetvelde iki mükerrer oy ve 426 toplam var.'),
    (ballot+'arikan','action','Mahmut Arıkan kesin cetvelde KATILMADI olarak kayıtlı.'),
)
readings(topic,'event',[pid for pid,stage,point in sources])
for pid,stage,point in sources:
    records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
        supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind='document'))
    task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)

dispute = stem+'-roll-call-dispute'
summary = dispute+'-finding'
finding(summary,detail,[session+'tally',ballot+'tally',ballot+'duplicates',ballot+'arikan'],
        'Oturum duyurusu, kesin cetvel başlığı ve Arıkan satırı birlikte okundu.')
records['practice_dispute'].append(dict(id=dispute,event_id=eid,summary_finding_id=summary,
    supported_points='Toplam 426, ret 179. Teklif kabul edildi.',
    disputed_points='Birleşim tutanağı 247 kabul, kesin cetvel 245 kabul ve iki mükerrer oy gösteriyor.',
    unresolved_points='İki resmî kayıt sürecin farklı aşamalarını yansıtıyor. Cetvelde Arıkan katılmadı olarak kayıtlı.'))
task('practice_dispute',dispute,detail,limit)
task('practice_dispute.summary_finding_id',dispute,detail,limit)
for pid,role,point in (
    (session+'tally','conflict','Oturum duyurusu 247 kabul ve 179 ret.'),
    (ballot+'tally','support','Kesin cetvel 245 kabul ve 179 ret.'),
    (ballot+'duplicates','support','Kesin cetvelde 2 mükerrer oy ve 426 toplam.'),
):
    section=passages[pid]['section']
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,point=point,source_position=section,role=role))
    task('practice_dispute_evidence','|'.join((dispute,pid,point,role)),point,section)

for entry in entries:
    dest=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in dest:
        dest.append(entry['values'])
for table,rows in records.items():
    dest=snapshot.setdefault(table,[])
    dest.extend(row for row in rows if row not in dest)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot,records,[e['values']['id'] for e in entries if e['kind']=='passage'],party)
reviews=review['practice_source_review']
existing={(row['subject_kind'],row['subject_id']):idx for idx,row in enumerate(reviews)}
for key in (('practice_event',eid),('practice_relation',rid)):
    previous=reviews[existing[key]]
    tasks[key]=(previous['supported_claim']+' '+detail,previous['limitations']+' '+limit)
for (kind,identity),(claim,limitation) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    row=dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limitation,result='reviewed',
        reason=kind+' hedefi için karar ve kesin cetvel özgün kaynaklarda birlikte okundu. '+claim)
    if (kind,identity) in existing:
        index=existing[kind,identity]
        assert set(json.loads(reviews[index]['passage_ids'])) < pids
        reviews[index]=row
    else:
        reviews.append(row)
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('pension-floor-final-draft.json',package),('pension-floor-final-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:
        f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'added or extended review targets')
