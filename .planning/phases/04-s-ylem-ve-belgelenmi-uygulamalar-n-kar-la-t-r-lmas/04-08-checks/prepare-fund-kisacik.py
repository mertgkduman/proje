"""Record the named article 5 motion and the earlier investor protection demand."""

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
aux=read(here/'fund-kisacik-source-records.json')
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
        aid=f'fund-kisacik-reading-{lane}-{topic}-{vid}'
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
stem = '0408-yeni-yol-2026-kisacik-madde5'
report = '0408-fund-kisacik-report-'
context = ('Sadullah Kısacık, 14 Ekim’de 2/3939’un 5. maddesine bağlı ve hâkim şirketler için '
           'sorumluluk hükmü eklenmesini önerdi. Plan ve Bütçe Komisyonu önergeyi reddetti.')
limit = ('Önerge Kısacık’ın imzasını taşıyor. Komisyon önergeyi ve 5. maddeyi ayrı oyladı. '
         'İsimli oy, belirli şirket için Kurul tespiti ve fiilî tahsil araştırmaya açık.')
evidence = [
    (report+'date','initiative','document','Tutanak 14 Ekim 2026 komisyon toplantısına ait.'),
    (report+'signed','initiative','document','İmzalı ek cümle önergesi ve bunu açıklayan milletvekili Sadullah Kısacık.'),
    (report+'text','initiative','document','Önerge ana, hâkim ve bağlı şirketlerde fon zararına sebep olan işlem ve kararlara sorumluluk tespiti koşulu koyuyor.'),
    (report+'liable','initiative','document','Yazılı cümlede portföy yönetim şirketiyle birlikte müteselsil sorumluluk ifadesi bulunuyor.'),
    (report+'speech','action','document','Kısacık 5. madde oylaması öncesinde hâkim şirketler ve holdingler üzerine görüşünü açıkladı.'),
    (report+'reject','result','document','Komisyon Başkanı Kısacık’ın önergesinin kabul edilmediğini açıkladı.'),
    (report+'article','result','document','Sonraki ayrı oylamada 5. madde kabul edildi.'),
]
eid = event(stem,'2026-10-14','Kısacık’ın 2/3939 5. madde önergesinin reddi',context,evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-komisyon-5472-2-3939-madde5-kisacik',
    occurrence_basis='14 Ekim Plan ve Bütçe Komisyonu tutanağında imzalı önerge, açıklama ve ayrı oylama.')
refs = [row[0] for row in evidence]
membership = '0408-fund-4603-floor-role'
committee_membership = '0408-fund-kisacik-membership-statement'
law = ['0408-fund-kisacik-law-'+k for k in ('priority','condition')]
scope = readings(topic,'event',refs+[membership,committee_membership,report+'spk',*law])
actor, cid, role_finding = (stem+suffix for suffix in ('-actor','-contribution','-finding'))
actor_limit = ('8 Ekim’de Yeni Yol Grubu sıfatı, 13 Mart 2025’te komisyon üyeliği açıklaması görülüyor. '
               '14 Ekim önergesinde Kısacık tek imzacı.')
role = 'Adana Milletvekili Sadullah Kısacık 5. madde için imzalı değişiklik önergesi verip komisyonda açıkladı.'
new('actor',id=actor,kind='individual_mp',party_id=party,person_id='0408-yeni-yol-2026-4343-kisacik-person',
    authorization_passage_id=None)
finding(role_finding,role,[report+'signed',report+'speech',membership,committee_membership],actor_limit)
records['practice_contribution'].append(dict(id=cid,event_id=eid,party_id=party,actor_id=actor,
    contribution_kind='task',finding_id=role_finding,authority_passage_id=None,
    membership_passage_id=membership,responsibility_limit=actor_limit))
records['practice_actor_period'].append(dict(contribution_id=cid,valid_from='2026-10-14',
    valid_to='2026-10-14',identity_passage_id=report+'signed'))
task('practice_contribution',cid,role,actor_limit)
task('practice_contribution.finding_id',cid,role,actor_limit)

earlier = '0408-yeni-yol-2026-4343'
target = earlier+'-target'
statement = earlier+'-statement'
result, ex, rid = (stem+suffix for suffix in ('-result','-explanation','-relation'))
comparison = ('1 Temmuz önergesi küçük yatırımcıların korunması ve tazmin yolları için genel araştırma istedi. '
              '14 Ekim önergesi, sorumluluğu tespit edilen bağlantılı şirketlerin kapsanması için belirli bir hukuki yol sundu.')
outcome = ('Komisyon 14 Ekim’de Kısacık’ın önergesini reddetti ve 5. maddeyi sonraki ayrı oylamada kabul etti. '
           '22 Ekim’de kabul edilen 7596 sayılı Kanun, portföy yönetim şirketinin önceliğini ve tahsil koşuluna bağlı kişi sorumluluğunu düzenledi.')
finding(result,outcome,[report+'reject',report+'article',*law],
        'Komisyonun iki kararı ve sonraki kanunun 5. maddesi ayrı okundu.')
finding(ex,comparison+' '+outcome+' '+limit,refs+[
    '0408-fund-july-signed-concern','0408-fund-july-signed-objective',
    '0408-fund-4603-signed-purpose',membership,committee_membership,report+'spk',*law],limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,
    topic_id=topic,scope_id=scope,comparability_reason=comparison,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=ex,
    temporal_context='1 Temmuz 10/4343, 6 Ekim 10/4603, 14 Ekim komisyon önergesi ve 22 Ekim kabul metni.',
    authority_context='Kısacık komisyonda yazılı önergenin imzacısı. Komisyon ve sonraki Genel Kurul işlemleri ayrı.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=comparison,passage_ids=encoded(refs)))
goal = next(r['values']['text'] for r in entries if r['kind']=='finding' and r['values']['id']==target)
for kind,claim in (('practice_relation',comparison+' '+outcome),('practice_relation.target_finding_id',goal),
                   ('practice_relation.result_finding_id',outcome),('practice_relation.explanation_finding_id',comparison)):
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
for name,content in [('fund-kisacik-draft.json',package),('fund-kisacik-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
