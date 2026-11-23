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
aux=read(here/'nov03-genelgorusme-source-records.json')
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
        aid=f'nov03-genelgorusme-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='TBMM birleşim tutanağı ve ilgili işlem belgeleri.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
def contribution(stem, eid, day, name, authority, references, claim, limit, kind):
    person, actor, cid, fid = (stem+tail for tail in ('-person','-actor','-contribution','-finding'))
    new('person',id=person,name=name)
    new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,
        authorization_passage_id=authority)
    finding(fid,claim,[authority,*references],limit)
    records['practice_contribution'].append(dict(id=cid,event_id=eid,party_id=party,actor_id=actor,
        contribution_kind=kind,finding_id=fid,authority_passage_id=authority,membership_passage_id=None,
        responsibility_limit=limit))
    records['practice_actor_period'].append(dict(contribution_id=cid,valid_from=day,valid_to=day,
        identity_passage_id=authority))
    for k in ('practice_contribution','practice_contribution.finding_id'):
        task(k,cid,claim,limit)


assert party in ('iyi','yeni-yol')
topic = 'makroekonomik-politika'
stem = ('0407' if party=='iyi' else '0408')+'-nov03-genelgorusme'
day = '2026-11-03'
limit = ('8/153 TBMM sicilinde Gündemde. 3 Kasım ret kararı o birleşimde ön görüşme istemine ait. '
         'Tutanakta isimli oylama sonucu bulunmuyor. Konuşmadaki mali iddialar ve fiilî ödemeler ayrıca araştırılıyor.')
context = ('Yeni Yol Grubu, 3 Kasım 2026’da verdiği fonların ekonomik etkileri konulu genel görüşme önergesinin '
           'ön görüşmesinin aynı birleşimde yapılmasını istedi. Genel Kurul bu gündem talebini reddetti.')
if party=='iyi':
    speaker = 'Hasan Toktaş'
    claim = 'Hasan Toktaş, ön görüşme talebine İYİ Parti Grubu adına destek açıkladı.'
else:
    speaker = 'Sadullah Kısacık'
    claim = 'Sadullah Kısacık, Yeni Yol Grubu adına yatırımcılara ödeme yapılmasını ve ödeme bilgisi verilmesini istedi.'
evidence = [
    ('signed-number','initiative','document','İmzalı 3 Kasım genel görüşme önergesinin esas numarası 8/153.'),
    ('signed-date','initiative','document','Ekmen’in imzaladığı genel görüşme önergesinin tarihi 3 Kasım 2026.'),
    ('signed-scope','initiative','document','Yazılı önerge fon olayının sanayi, yatırım ve istihdam dahil ekonomik etkilerinin değerlendirilmesini istiyor.'),
    ('register-date','action','document','TBMM esas kaydı geliş gününü 3 Kasım 2026 olarak gösteriyor.'),
    ('floor-call','action','document','Ekmen imzalı grup önerisi 3 Kasım’da ön görüşme yapılmasını istedi.'),
    ('floor-role','action','document',speaker+' tutanakta kendi grubu adına söz aldı.'),
    ('floor-position','action','document',claim),
    ('floor-vote','result','document','Başkan ön görüşme gündem talebinin kabul edilmediğini açıkladı.'),
    ('summary-vote','result','document','Birleşim özeti aynı gün ön görüşme önerilerinin reddini kaydediyor.'),
    ('register-status','result','document','8/153 esas dosyasının erişimde görülen durumu Gündemde.'),
]
if party=='yeni-yol':
    evidence.append(('floor-transparency','action','document','Kısacık yatırımcıların neyi ne zaman alacağını öğrenebilmesini istedi.'))
evidence = [(f'{stem}-{key}',stage,basis,point) for key,stage,basis,point in evidence]
eid = event(stem,day,'Fonların ekonomik etkileri için genel görüşme ön görüşme talebinin reddi',context,evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-5-012-yeni-yol-genel-gorusme-fon-gundem',
    occurrence_basis='TBMM 28. Dönem 5. Yasama Yılı 12. Birleşim ham tutanağındaki grup önerisi, görüşmeler ve başkanın oylama sonucu.')
pids = [row[0] for row in evidence]
scope = readings(topic,'event',pids+[f'{stem}-{key}' for key in ('summary-call','register-number','signed-role','signed-loss')])
extra = [stem+'-floor-transparency'] if party=='yeni-yol' else []
contribution(stem,eid,day,speaker.upper(),stem+'-floor-role',[stem+'-floor-position',*extra],claim,limit,
    'support')
candidate = stem+'-unmatched'
reason = ('Aynı genel görüşme aracına ve fon olayının ekonomi geneline etkileri kapsamına ilişkin önceki tarihli grup açıklaması araştırılıyor. '
          '10/4603 ve 10/4826 Meclis araştırmaları ayrı işlemler.')
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,
    relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(pids)))
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
for name,content in [('nov03-genelgorusme-draft.json',package),('nov03-genelgorusme-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
