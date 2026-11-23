"""Record the 10/4826 agenda vote and its preceding research demand."""

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
aux=read(here/'fund-4826-source-records.json')
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
        aid=f'fund-4826-reading-{lane}-{topic}-{vid}'
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
assert party == 'yeni-yol'
topic = 'makroekonomik-politika'
stem = '0408-yeni-yol-2026-4826'
detail, signed, floor, summary = ('0408-fund-4826-'+key+'-' for key in ('detail', 'signed', 'floor', 'summary'))
context = ('Yeni Yol Grubu 10/4826’nın 21 Ekim birleşiminde görüşülmesini önerdi. '
           'Genel Kurul öneriyi kabul etmedi.')
limit = ('Oylama araştırma önergesinin o gün ön görüşmeye alınmasına ilişkindi. 10/4826 esas dosyasında '
         'durum Gündemde. İsimli oylar ve araştırma komisyonu kurulmasına ilişkin ayrı sonuç araştırılıyor.')
evidence = [
    (detail+'id', 'initiative', 'document', 'TBMM araştırma önergesini 10/4826 olarak kaydetti.'),
    (detail+'filed', 'initiative', 'document', 'Geliş günü 21 Ekim 2026 olarak kayda geçti.'),
    (signed+'purpose', 'initiative', 'document', 'Gerekçe kamu kurumları arasındaki koordinasyonun incelenmesini istiyor.'),
    (floor+'agenda', 'action', 'document', 'Yeni Yol Grubu aynı gün ön görüşme istedi.'),
    (floor+'role', 'action', 'document', 'Mehmet Atmaca Yeni Yol Grubu adına konuştu.'),
    (floor+'aim', 'action', 'document', 'Atmaca Mecliste araştırma komisyonu kurulmasını istedi.'),
    (floor+'first', 'action', 'document', 'İlk elektronik oylamada karar yeter sayısı bulunamadı.'),
    (floor+'second', 'action', 'document', 'İkinci elektronik oylamada da karar yeter sayısı bulunamadı.'),
    (floor+'decision', 'result', 'document', 'Üçüncü oturumda karar yeter sayısı bulundu ve grup önerisi kabul edilmedi.'),
    (summary+'result', 'result', 'document', 'Birleşim özeti aynı gün görüşme önerilerinin reddini kaydetti.'),
]
eid = event(stem, '2026-10-21', '10/4826 araştırma önergesinin aynı gün görüşülmesi', context, evidence, limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-5-009-10-4826-gundem',
    occurrence_basis='TBMM önergesi, birleşim tutanağı ve ilgili işlem belgeleri.')
refs = [row[0] for row in evidence]
scope = readings(topic, 'event', refs+[detail+'status',detail+'owner',detail+'party',
                                      signed+'id',signed+'signature',summary+'motion'])

person, actor, contribution, finding_id = (stem+tail for tail in ('-person','-actor','-contribution','-finding'))
authority = floor+'role'
claim = ('Araştırma önergesinin ilk imzacısı Mehmet Atmaca, 9. Birleşimde Yeni Yol Grubu adına '
         'fon krizinin Meclis araştırma komisyonuna götürülmesini istedi.')
new('person', id=person, name='MEHMET ATMACA')
new('actor', id=actor, kind='authorized_representative', party_id=party, person_id=person, authorization_passage_id=authority)
finding(finding_id, claim, [authority, floor+'aim', detail+'owner', signed+'signature'], limit)
records['practice_contribution'].append(dict(id=contribution, event_id=eid, party_id=party, actor_id=actor,
    contribution_kind='support', finding_id=finding_id, authority_passage_id=authority, membership_passage_id=None,
    responsibility_limit='TBMM tutanağı bu görev için Yeni Yol Grup sıfatını gösteriyor. '+limit))
records['practice_actor_period'].append(dict(contribution_id=contribution, valid_from='2026-10-21',
    valid_to='2026-10-21', identity_passage_id=authority))
task('practice_contribution', contribution, claim, limit)
task('practice_contribution.finding_id', contribution, claim, limit)

previous = '0408-yeni-yol-2026-4343-statement'
target = '0408-yeni-yol-2026-4343-target'
prior_refs = ['0408-fund-july-signed-objective','0408-fund-july-floor-authority',
              '0408-fund-july-floor-goal','0408-fund-july-oct07-role','0408-fund-july-oct07-plan']
result, explanation, rid = (stem+tail for tail in ('-result','-explanation','-relation'))
outcome = (context+' İlk iki elektronik oylamada karar yeter sayısı bulunamadı. '
           'Üçüncü oturumda yeter sayı bulundu ve ön görüşme önerisi reddedildi.')
comparison = ('1 Temmuz talebi küçük yatırımcıyı ve genel piyasa denetimini konu alıyordu. '
              '7 Ekim komisyon çağrısı ve 21 Ekim’deki 10/4826 önergesi belirli fon krizine odaklandı.')
finding(result, outcome, refs, '9. Birleşim tutanağındaki üç oturum ve birleşim özeti birlikte okundu.')
finding(explanation, comparison+' '+outcome+' '+limit, prior_refs+refs, limit)
records['practice_relation'].append(dict(id=rid, statement_id=previous, event_id=eid, party_id=party, topic_id=topic,
    scope_id=scope, comparability_reason=comparison, target_finding_id=target, result_finding_id=result,
    explanation_finding_id=explanation, temporal_context='1 Temmuz araştırma çağrısı, 7 Ekim grup açıklaması ve 21 Ekim gündem oylaması.',
    authority_context='Temmuz önergesini Kısacık ve diğer imzacılar sundu. Kaya ve Atmaca kendi birleşimlerinde Yeni Yol Grubu adına konuştu.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate', scope_id=scope, event_id=eid, relation_id=rid,
    state='eligible', reason=comparison, passage_ids=encoded(refs)))
goal = next(row['values']['text'] for row in entries if row['kind']=='finding' and row['values']['id']==target)
for kind, claim in (('practice_relation', comparison+' '+outcome), ('practice_relation.target_finding_id', goal),
                    ('practice_relation.result_finding_id', outcome), ('practice_relation.explanation_finding_id', comparison)):
    task(kind, rid, claim, limit)

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
for name,content in [('fund-4826-draft.json',package),('fund-4826-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
