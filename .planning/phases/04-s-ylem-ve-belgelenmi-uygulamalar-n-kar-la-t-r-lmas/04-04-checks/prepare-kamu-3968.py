"""Prepare the 2/3968 filing and scoped party contribution."""

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
aux=read(here/'kamu-3968-source-records.json')
party=aux['party_id']
package=read(data/'practices/04-yeni-parti.json')
review=read(data/'practices/04-yeni-parti-review.json')
snapshot=read(data/'releases'/package['base_release']/'records.json')
inventory=read(data/'practices/04-inventory.json')
entries=package['entries']
entries.extend(aux['entries'])
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
            boundary_reason='2/3968 ve görev sonrası yapılan ödemelere ilişkin kaynaklar incelendi.'))
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
        aid=f'kamu-3968-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='2/3968 için başvuru ve komisyon kaydı.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='TBMM’nin imzalı teklif, başvuru ve komisyon sevki belgeleri.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'yeni-parti'
topic = 'mali-butce'
stem = '0404-yeni-parti-2026-2-3968'
source = '0404-kamu-3968-'
day = '2026-10-21'
limit = ('2/3968’in 21 Ekim sevki ve erişilen «Komisyonda» durumu kayıtlı. '
         'Yasalaşma, ödemelerin değişmesi ve bütçe etkisi açık. '
         'Kapsam, imzalı teklifte tek tek sayılan ödeme ve tazminat hükümleriyle sınırlı.')
context = ('Yeni Parti Grup Başkanvekili Gökhan Günaydın’ın 2/3968 sayılı kanun teklifi, '
           'belirli kamu yöneticilerine görev sonrası yapılan ödemelerde değişiklik öneriyor.')
authority=source+'signed-signature'
evidence = [
    (source+'signed-file','initiative','document','Taramanın üst yazısında 2/3968 ve Plan ve Bütçe Komisyonu yazıyor.'),
    (authority,'initiative','document','İmza bloğu Günaydın’ı İstanbul milletvekili ve Yeni Parti Grup Başkanvekili olarak gösteriyor.'),
    (source+'signed-stamp','initiative','document','TBMM Genel Evrak kaşesi 21 Ekim 2026.'),
    (source+'signed-series','initiative','document','Madde 4, Sermaye Piyasası Kanunu’nun 132. maddesindeki üç cümleyi kaldırmayı öneriyor.'),
    (source+'signed-compensation-text','initiative','document','Madde 5, belirli tazminatta hizmet yılı başına azami emeklilik ikramiyesi sınırı öneriyor.'),
    (source+'agenda-id','action','document','Gelen Kâğıtlar 15, teklifi Plan ve Bütçe Komisyonuna gönderilenler arasında listeliyor.'),
    (source+'detail-pending','action','document','Erişilen teklif dosyası işlem alanında Komisyonda yazıyor.'),
]
eid = event(stem,day,'2/3968 görev sonrası kamu ödemeleri teklifi',context,evidence,limit)
records['practice_event'][-1]['common_event_key']='tbmm-28-5-2-3968-basvuru'
refs=[row[0] for row in evidence]
scope=readings(topic,'event',refs+[source+tail for tail in ('signed-goal','signed-pay','signed-compensation',
    'detail-id','detail-arrival','detail-signer','press-date','press-scope')])
reason='21 Ekim basın açıklaması teklif ile aynı gün. Daha erken tarihli, aynı kapsamdaki parti söylemi araştırılıyor.'
candidate=stem+'-unmatched'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,relation_id=None,
    state='unmatched',reason=reason,passage_ids=encoded(refs)))
task('practice_candidate',candidate,reason,limit)
statement_scope=scope_for(topic,'statement')
press=versions[passages[source+'press-scope']['version_id']]['final_url']
records['practice_attempt_v2'].append(dict(id=stem+'-statement-search',scope_id=statement_scope,
    attempted_at=when,query='Yeni Parti Gökhan Günaydın görevden alınan bürokratlar maaş kesilmesi 21 Ekim',url=press,
    result='inconclusive',reason='TBMM haberi teklif ile aynı tarihe ait. Erken tarihli aynı kapsam söylemi için tarama açık.',
    source_version_id=passages[source+'press-scope']['version_id']))

person,actor,cid,fid=(stem+suffix for suffix in ('-person','-actor','-contribution','-finding'))
new('person',id=person,name='Gökhan GÜNAYDIN')
new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,authorization_passage_id=authority)
contribution_limit='Belgelendirilen katkı, grup başkanvekili sıfatıyla imzalı teklif sunumuyla sınırlı.'
finding(fid,context,[authority,source+'signed-file',source+'detail-signer'],contribution_limit)
records['practice_contribution'].append(dict(id=cid,event_id=eid,party_id=party,actor_id=actor,
    contribution_kind='task',finding_id=fid,authority_passage_id=authority,membership_passage_id=None,responsibility_limit=contribution_limit))
records['practice_actor_period'].append(dict(contribution_id=cid,valid_from=day,valid_to=day,identity_passage_id=authority))
for kind in ('practice_contribution','practice_contribution.finding_id'):
    task(kind,cid,context,contribution_limit)

for entry in entries:
    destination=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in destination:
        destination.append(entry['values'])
for table,rows in records.items():
    destination=snapshot.setdefault(table,[])
    destination.extend(row for row in rows if row not in destination)
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
        reason=kind+' hedefinin kaynak, tarih ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [(f'kamu-3968-draft.json',package),(f'kamu-3968-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
