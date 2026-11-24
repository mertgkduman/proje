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
aux=read(here/'village-2691-source-records.json')
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
            boundary_reason='2/2691 Genel Kurul konuşması ve oylaması özgün TBMM belgelerinden incelendi.'))
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
        aid=f'village-2691-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='2/2691 teklifinin Genel Kurul konuşması ve oylamasına ilişkin TBMM kaydı.',state='examined',attempt_ids=encoded([aid])))
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
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='2c72b61440ad6eb2f550c2f1fd8b1f85862292d42db5cebf6bcde1b67424bed4'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='faf1c5af22630fb665fd9ba16c75e62eafe15e3eec77a21e74da4c288ad16038'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(31,27,0)
topic='sehircilik'; stem='0411-saadet-village-2691'; src='0411-village-2691-'
statement,target,quote=(stem+s for s in ('-statement','-target','-quote'))
goal='Mehmet Atmaca 26 Kasım 2024te Saadet Partisi Grubu adına 2/2691 köy ve yapı denetimi kanun değişikliğine ret oyu vereceklerini söyledi.'
limit='Atmaca dönemin TBMM tutanağında Saadet Partisi Grubu adına konuşur; grupta Gelecek Partili milletvekilleri de vardı. Erişilen basılı oy cetvelindeki Yeni Yol sütununun neden öyle göründüğü bilinmediğinden 2024 parti sıfatına kanıt yapılmadı. Ret sadece Atmacanın kendi oyudur. Başkanın birleşim sonucu 320 oy, 247 kabul ve 73 ret; basılı kesin sonuç cetveli 321 toplam, 242 kabul, 74 ret ve 5 mükerrer gösterir. Farkın nedeni belirlenmedi. 27. birleşim 4 Aralıkta açıldı, 7534 kanunun kabul tarihi 5 Aralıktır.'
sp=[src+'speech-identity',src+'speech-authority',src+'speech-stance']; finding(target,goal,sp,'26 Kasım TBMM 23. birleşimde grup adına konuşma ve ret sözü.')
finding(quote,passages[sp[2]]['exact'],[sp[2]],'Aynı grup konuşmasının teklifin tümüne ilişkin ret ifadesi.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2024-11-26',date_precision='day',version_id=passages[sp[2]]['version_id'],period_basis='TBMM 23. birleşim grup konuşması.',uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-sehircilik'))
readings(topic,'statement',sp)
for kind,claim in [('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',passages[sp[2]]['exact'])]: task(kind,statement,claim,limit)
ep=[(src+'vote-atmaca','action','document','174 sıra sayılı teklifin açık oy cetvelinde Atmaca ret verdi.'),(src+'vote-totals','result','document','Kesin sonuç cetveli 242 kabul, 74 ret, 5 mükerrer ve 321 toplam gösterir.'),(src+'session-totals','result','document','Birleşimde açıklanan sonuç 320 oy, 247 kabul ve 73 rettir.'),(src+'law-number','result','document','Teklif 7534 sayılı kanun oldu.'),(src+'law-adopt','result','document','7534 sayılı kanun 5 Aralık 2024te kabul edildi.')]
eid=event(stem,'2024-12-05','2/2691 köy ve yapı denetimi teklifinin açık oylaması','2/2691 teklifi kabul edilip 7534 sayılı kanun oldu; Atmaca ret verdi.',ep,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-3-27-2-2691-village-law-final-vote',occurrence_basis='27. birleşim basılı açık oy cetveli ve 7534 sayılı kanun kabul günü.')
eids=[r[0] for r in ep]; scope=readings(topic,'event',eids); rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
observed='5 Aralıkta 2/2691 kabul edilerek 7534 sayılı kanun oldu; Atmaca açık oylamada ret verdi. Birleşim ile kesin sonuç cetveli oy toplamlarını farklı gösteriyor.'
compare='Atmacanın 26 Kasımda ret yönünde konuştuğu 2/2691 teklifi ile 5 Aralıkta oylanan 174 sıra sayılı teklif aynı yasama dosyasıdır.'
finding(result,observed,eids,'TBMM basılı oylama cetveli, birleşim ve 7534 numaralı kanun.')
finding(explanation,compare+' '+limit,sp+eids,limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='26 Kasım grup konuşması ve 4 Aralıkta başlayıp 5 Aralıkta tamamlanan 27. birleşimde nihai oy.',authority_context='Atmaca Saadet Partisi Grubu adına konuştu; cetveldeki ret yalnız kendi oyudur. Aynı grup Gelecek Partili milletvekillerini de içeriyordu.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(eids)))
for kind,claim in [('practice_relation',compare),('practice_relation.target_finding_id',goal),('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare)]: task(kind,rid,claim,limit)
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
for name,content in [('village-2691-draft.json',package),('village-2691-review-draft.json',review)]:
 path=here/name
 with path.open('x') as output: output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
 print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
