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
aux=read(here/'budget-1280-source-records.json')
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
            boundary_reason='Partiler arası temas duyurusu ve iki görüşmenin tarihli açıklamaları okundu.'))
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
        aid=f'budget-1280-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Ocak 2026 partiler arası temas duyurusu veya tarihli görüşme kaydı.',state='examined',attempt_ids=encoded([aid])))
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
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='fbf24ce685c3e9c01523f432fe5c6034c2485be2a3dd96643243e51335272e94'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='b7a1afe9463201f44a21cba18905c1789f1de74df1ffb28c9e7f1fe9d86e8633'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(26,22,0)
topic='makroekonomik-politika'; stem='0411-saadet-budget-1280'; src='0411-budget-1280-'
statement,target,quote=(stem+s for s in ('-statement','-target','-quote'))
goal='Mahmut Arıkan 8 Aralık 2025te 2026 bütçe teklifinin önceliklerini ve arkasındaki zihniyeti reddetti.'
limit=('Arıkanın parti yayınıyla TBMM tutanağının kapanışı birebir aynı değildir. Arıkan 21 Aralık açık oylamasına katılmadı; ona ret oyu atfedilemez. Bülent Kaya Yeni Yol Grubu adına konuştu ve kendi ret oyu kaydedildi; bir kişinin oyu bütün parti veya grubun oyunu temsil etmez.')
sp=[src+'speech-authority',src+'speech-stance',src+'speech-proposal']; finding(target,goal,sp,'8 Aralık TBMM tutanağında konuşma ve grup süresi okundu.')
finding(quote,passages[sp[1]]['exact'],[sp[1]],'8 Aralık konuşmasından birebir pasaj.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2025-12-08',date_precision='day',version_id=passages[sp[1]]['version_id'],period_basis='TBMM 26. birleşim 8 Aralık 2025.',uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-makroekonomik-politika'))
readings(topic,'statement',sp)
for kind,claim in [('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',passages[sp[1]]['exact'])]: task(kind,statement,claim,limit)
ep=[(src+'vote-kaya-speech','initiative','document','Bülent Kaya 21 Aralıkta Yeni Yol Grubu adına bütçeye ret tutumunu açıkladı.'),(src+'vote-kaya-vote','action','document','Kesin oy tablosunda Bülent Kayanın bütçe oyu ret.'),(src+'vote-arikan-vote','action','document','Kesin oy tablosunda Mahmut Arıkan bütçe oylamasına katılmadı.'),(src+'vote-totals','result','document','226 sıra sayılı bütçe için kesin sonuç tablosu 316 kabul 247 ret ve 6 mükerrer oyu gösteriyor.'),(src+'law-number','result','document','Kabul edilen bütçe kanununun numarası 7567.'),(src+'law-adopt','result','document','TBMM sicilinde 7567 kabul tarihi 21 Aralık 2025.')]
eid=event(stem,'2025-12-21','1/280 2026 bütçesinin kesin oylaması','2026 bütçe teklifi açık oylamada kabul edildi. Bülent Kaya ret verdi; Mahmut Arıkan katılmadı.',ep,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-4-39-1-280-budget-final-vote',occurrence_basis='TBMM 39. birleşim kesin oy tablosu ve 7567 sicili.')
eids=[r[0] for r in ep]; scope=readings(topic,'event',eids+[src+'law-gazette']); rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
observed='21 Aralıkta 1/280 bütçe teklifi kesin 316 kabul ve 247 ret ile kabul edildi; Arıkan katılmadı, Bülent Kaya ret verdi. Kanun 7567 numarasını aldı.'
compare='Arıkanın eleştirdiği 2026 bütçe teklifi ile 21 Aralıkta oylanan 1/280 aynı bütçedir.'
finding(result,observed,eids,'Kesin tablo ve kanun sicili; ilk anons mükerrer oylar nedeniyle ayrı.')
finding(explanation,compare+' '+limit,sp+eids,limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='8 Aralık bütçe konuşması ile 21 Aralık nihai oy ayrı; 7567 sicilinde 31 Aralık Resmî Gazete kaydı ayrıca yer alır.',authority_context='Arıkan Saadet Genel Başkanı ve milletvekili olarak Yeni Yol Grubu süresinden konuştu; 21 Aralık Kaya grup adına konuştu ve kendi oyunu verdi. Arıkan katılmadı.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(eids)))
for kind,claim in [('practice_relation',compare),('practice_relation.target_finding_id',goal),('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare)]: task(kind,rid,claim,limit)
for entry in entries:
 destination=snapshot.setdefault(entry['kind'],[])
 if entry['values'] not in destination: destination.append(entry['values'])
for table,rows in records.items():
 destination=snapshot.setdefault(table,[]); destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot,records,[entry['values']['id'] for entry in entries if entry['kind']=='passage'],party); reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
 pids,owners=targets[(kind,identity)]; assert party in owners
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),supported_claim=claim,limitations=limitation,result='reviewed',reason=kind+' için kaynak ve sınırlar incelendi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]; package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('budget-1280-draft.json',package),('budget-1280-review-draft.json',review)]:
 path=here/name
 with path.open('x') as output: output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
 print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
