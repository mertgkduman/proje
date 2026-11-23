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
aux=read(here/'fund-july-source-records.json')
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
        aid=f'fund-july-reading-{lane}-{topic}-{vid}'
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
assert party == 'iyi'
topic = 'makroekonomik-politika'
stem = '0407-iyi-2026-4343'
floor,detail,summary = ['0407-fund-july-'+key+'-' for key in ('floor','detail','summary')]
scope_limit = ('Oylama aynı gün ön görüşme önerisi hakkındaydı. İsimli oy bulunmuyor. '
    'Erişilen esas kaydı Gündemde. Araştırma komisyonunun kurulmasına ilişkin ayrı sonuç açık.')
july_context = 'Yeni Yol Grubu 10/4343’ün 1 Temmuz birleşiminde görüşülmesini önerdi. Genel Kurul öneriyi kabul etmedi.'
evidence = [
    (detail+'id','initiative','document','TBMM esas numarası 10/4343.'),
    (floor+'agenda','action','document','Yeni Yol grubu aynı gün ön görüşme istedi.'),
    (floor+'iyi-role','action','document','Ayyüce Türkeş Taş İYİ Parti Grubu adına konuştu.'),
    (floor+'iyi-support','action','document','Taş önergeye sözlü destek açıkladı.'),
    (floor+'quorum1','action','document','3. oturumdaki ilk elektronik oylamada karar yeter sayısı bulunamadı.'),
    (floor+'quorum2','action','document','4. oturumdaki ikinci elektronik oylamada karar yeter sayısı bulunamadı.'),
    (floor+'decision','result','document','5. oturumdaki üçüncü elektronik oylamada öneri kabul edilmedi.'),
    (summary+'result','result','document','Birleşim özeti aynı gün görüşme önerisinin kabul edilmediğini kaydediyor.'),
]
event_id=event(stem,'2026-07-01','10/4343 araştırma önergesinin aynı gün görüşülmesi',july_context,evidence,scope_limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-4-108-10-4343-gundem',
    occurrence_basis='TBMM önergesi, birleşim tutanağı ve ilgili işlem belgeleri.')
refs=[row[0] for row in evidence]
scope=readings(topic,'event',refs+[detail+'filed',detail+'pending'])
candidate=stem+'-unmatched'
reason='1 Temmuz öncesinde İYİ Parti’nin bu araştırmaya ilişkin doğrudan söylemi için araştırma açık.'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=event_id,relation_id=None,
    state='unmatched',reason=reason,passage_ids=encoded(refs)))
task('practice_candidate',candidate,reason,scope_limit)
authority=floor+'iyi-role'
support=floor+'iyi-support'
person,actor,cid,fid=(stem+tail for tail in ('-person','-actor','-contribution','-finding'))
goal = ('Ayyüce Türkeş Taş, İYİ Parti Grubu adına küçük yatırımcıların korunmasına ve piyasa denetimine ilişkin '
        '10/4343 araştırma önergesini desteklediğini açıkladı.')
new('person',id=person,name='AYYÜCE TÜRKEŞ TAŞ')
new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,authorization_passage_id=authority)
finding(fid,goal,[authority,support],scope_limit)
records['practice_contribution'].append(dict(id=cid,event_id=event_id,party_id=party,actor_id=actor,
    contribution_kind='support',finding_id=fid,authority_passage_id=authority,membership_passage_id=None, responsibility_limit=scope_limit))
records['practice_actor_period'].append(dict(contribution_id=cid,valid_from='2026-07-01',
    valid_to='2026-07-01',identity_passage_id=authority))
for kind in ('practice_contribution','practice_contribution.finding_id'):
    task(kind,cid,goal,scope_limit)

statement,target,quote=(stem+tail for tail in ('-statement','-target','-quote'))
statement_refs=[authority,support,detail+'id']
finding(target,goal,statement_refs,'Taş’ın grup sıfatı, destek ifadesi ve esas kaydı özgün belgede okundu.')
finding(quote,passages[support]['exact'],[support],'Grup adına kısa destek ifadesi.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-07-01',date_precision='day',
    version_id=passages[support]['version_id'],period_basis='108. Birleşim 3. oturum, Yeni Yol gündem önergesi görüşmesi.',
    uncertainty_reason=None,comparison_row_id='04-03-v3-0306-iyi-program-makroekonomik-politika-row'))
readings(topic,'statement',statement_refs)
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
    ('practice_statement.quote_finding_id',passages[support]['exact'])):
    task(kind,statement,claim,scope_limit)

october='0407-iyi-2026-fund-1007'
oct_event=october+'-event'
rid=october+'-relation'
old=next(row for row in records['practice_candidate'] if row['id']==october+'-unmatched')
oct_refs=json.loads(old['passage_ids'])
explanation_id=october+'-explanation'
reason = ('1 Temmuz’daki destek sermaye piyasası ve küçük yatırımcıların korunmasına ilişkin araştırma içindi. '
    '7 Ekim’de Usta ile Dalgın, belirli fon olayında Meclis araştırma komisyonu kurulmasını istedi.')
limit = ('7 Ekim bir bilgilendirme ve siyasi grup görüşmesi. Araştırma komisyonunun kurulması, '
    'fiilî fon ödemeleri ve ilgili oylardaki kişi tercihleri açık.')
finding(explanation_id,goal+' '+reason,[*statement_refs,
    '0407-fund-oct07-usta-plan','0407-fund-oct07-dalgin-plan'],limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=oct_event,party_id=party,
    topic_id=topic,scope_id=old['scope_id'],comparability_reason=reason,target_finding_id=target,
    result_finding_id=None,explanation_finding_id=explanation_id,temporal_context='1 Temmuz destek konuşması, 7 Ekim grup çağrıları.',
    authority_context='Taş, Usta ve Dalgın kendi birleşimlerinde İYİ Parti Grubu adına konuştu.',uncertainty_reason=limit))
records['practice_candidate_revision'].append(dict(id=october+'-reviewed-match',candidate_id=old['id'],
    recorded_at=when,event_id=oct_event,relation_id=rid,state='eligible',reason=reason,passage_ids=encoded(oct_refs)))
for kind,claim in (('practice_relation',reason),('practice_relation.target_finding_id',goal),
    ('practice_relation.explanation_finding_id',reason)):
    task(kind,rid,claim,limit)

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
for name,content in [('fund-july-draft.json',package),('fund-july-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
