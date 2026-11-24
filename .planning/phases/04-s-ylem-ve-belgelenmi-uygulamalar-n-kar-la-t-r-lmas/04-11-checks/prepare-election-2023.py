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
aux=read(here/'election-2023-source-records.json')
party=aux['party_id']
package=read(data/'practices/04-saadet.json')
review=read(data/'practices/04-saadet-review.json')
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
            boundary_reason='Parti çağrısı, seçim kararı ve TBMM tutanağı incelendi.'))
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
        aid=f'election-2023-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Seçim çağrısı ve sonraki seçim işlemleri.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='Birden fazla yayımlanmış açıklamada toplantı ve tarih doğrulandı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='saadet'
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='4dc52f051576cdc4f2eab0bec4361569eb3e172572757e655c5c852f86b6e74f'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='cd17be98c22acb24f1ed778e3d4869a31bd661c96524ef6a4718a80fbcb15f31'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(37,33,0)
topic='secim-siyasi-partiler'; stem='0411-saadet-election-2023'; src='0411-election-2023-'
statement,target,quote=(stem+s for s in ('-statement','-target','-quote'))
goal='Saadet Partisi Genel Başkanı Temel Karamollaoğlu, 18 Ocak 2023’te seçim kararının o gün alınmasını ve en geç iki ay içinde seçime gidilmesini istedi.'
limit='18 Ocak’tan iki takvim ayı sonrası 18 Mart’tır. Yenileme kararı çağrıdan 51 gün sonra, oy verme ise 116 gün sonra gerçekleşti. 10 Mart kararından 14 Mayıs oy verme gününe 65 gün geçti. Cumhurbaşkanının yenileme kararı ve YSK’nın gün belirleme yetkisi ayrıdır. Çağrının karar üzerinde etkisi gösterilmiyor.'
sp=[src+'statement-call'];finding(target,goal,sp,'Parti yayımındaki genel başkan açıklaması.');finding(quote,passages[sp[0]]['exact'],sp,'Karamollaoğlunun seçim çağrısı.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2023-01-18',date_precision='day',version_id=passages[sp[0]]['version_id'],period_basis='Parti API yayım damgasının Türkiye yerel günü 18 Ocak 2023.',uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-secim-siyasi-partiler'))
readings(topic,'statement',sp)
for kind,claim in [('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',passages[sp[0]]['exact'])]: task(kind,statement,claim,limit)
ep=[(src+'ysk-renew','initiative','document','Cumhurbaşkanı 10 Mart’ta seçimlerin yenilenmesine karar verdi.'),(src+'ysk-day','action','document','YSK 10 Mart’ta oy verme gününü 14 Mayıs olarak belirledi.'),(src+'floor-parliament','result','document','TBMM tutanağı milletvekili seçiminin 14 Mayıs’ta yapıldığını kaydediyor.'),(src+'floor-president','result','document','TBMM tutanağı cumhurbaşkanı seçiminin ilk turunun 14 Mayıs’ta yapıldığını kaydediyor.')]
context='10 Mart 2023 seçim yenileme kararı, YSK’nın oy verme günü kararı ve 14 Mayıs 2023 seçimleri.'
eid=event(stem,'2023-03-10','2023 seçimlerinin yenilenmesi ve oy verme günü',context,ep,limit)
records['practice_event'][-1].update(common_event_key='turkiye-2023-03-10-secim-yenileme',occurrence_basis='10 Mart YSK kararı seçim yenileme ve oy verme gününü, TBMM ilk birleşim tutanağı 14 Mayıs seçimlerini belgeliyor.')
eids=[r[0] for r in ep];scope=readings(topic,'event',eids);rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
observed='Cumhurbaşkanı seçimleri 10 Mart’ta yeniledi. YSK oy verme gününü 14 Mayıs olarak belirledi ve seçimler o gün yapıldı.'
compare='18 Ocak çağrısında aynı gün karar ve iki ay içinde seçim istendi. Yenileme kararı 10 Mart’ta, oy verme 14 Mayıs’ta gerçekleşti.'
finding(result,observed,eids,'10 Mart YSK kararı ve TBMM ilk birleşim tutanağı.');finding(explanation,compare+' '+limit,sp+eids,limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='18 Ocak çağrısı, 10 Mart yenileme kararı ve 14 Mayıs ilk oy verme günü.',authority_context='Çağrı Saadet Genel Başkanına, yenileme kararı Cumhurbaşkanına ve oy verme gününün belirlenmesi YSK’ya aittir.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(eids)))
for kind,claim in [('practice_relation',compare),('practice_relation.target_finding_id',goal),('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare)]:task(kind,rid,claim,limit)
for entry in entries:
 destination=snapshot.setdefault(entry['kind'],[])
 if entry['values'] not in destination: destination.append(entry['values'])
for table,rows in records.items():
 destination=snapshot.setdefault(table,[]); destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot,records,[entry['values']['id'] for entry in entries if entry['kind']=='passage'],party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
 pids,owners=targets[(kind,identity)]; assert party in owners
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),supported_claim=claim,limitations=limitation,result='reviewed',reason=kind+' için kaynak ve sınırlar incelendi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]; package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('election-2023-draft.json',package),('election-2023-review-draft.json',review)]:
 path=here/name
 with path.open('x') as output: output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
 print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
