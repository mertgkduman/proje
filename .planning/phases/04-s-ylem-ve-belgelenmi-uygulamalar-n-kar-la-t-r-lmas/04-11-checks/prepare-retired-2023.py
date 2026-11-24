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
aux=read(here/'retired-2023-source-records.json')
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
            boundary_reason='Emekli ödemesi hakkındaki konuşma, kanunlar ve SGK raporu okundu.'))
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
        aid=f'retired-2023-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Emekli ödemesinin kapsamı ve değişikliği.',state='examined',attempt_ids=encoded([aid])))
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
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='e273528bd5104b6556ea60bb028ccc95d61ac7d3a7376907eaf7334d31f580c2'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='d37c4bd2ecbaf6c82c856adcb9e9b20f706ff4d87d0be384ef463ea08d649d23'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(34,30,0)
topic='sosyal-guvenlik'
stem='0411-saadet-retired-2023'
src='0411-retired-2023-'
statement,target,quote=(stem+s for s in ('-statement','-target','-quote'))
goal='Saadet Partisi milletvekili Şerafettin Kılıç, tek seferlik 5.000 TL ödemeyi ve bunun çalışmayan emeklilerle sınırlanmasını eleştirdi. Emekli aylıklarında kalıcı iyileştirme istedi.'
limit='İlk kanunda ölüm geliri veya aylığı alanlar için ayrı istisna vardı. Kapsamın genişlemesi, tek seferlik ödeme tutarına ilişkin eleştirinin karşılandığı anlamına gelmez. SGK verisi toplu ödeme verisidir. Bu kaynaklar Saadet Partisinin değişikliğe neden olduğunu göstermez.'
sp=[src+'speech-quote',src+'speech-exclusion',src+'speech-speaker',src+'role-identity']
finding(target,goal,sp,'TBMM tutanağında konuşma ve dönemsel parti sıfatı ayrı okundu.')
finding(quote,passages[sp[0]]['exact'],[sp[0]],'Konuşmadaki kalıcı iyileştirme ifadesi.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2023-10-25',date_precision='day',version_id=passages[sp[0]]['version_id'],period_basis='Saadet Partili Antalya milletvekilinin Meclis konuşması.',uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-sosyal-guvenlik'))
readings(topic,'statement',sp)
for kind,claim in [('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',passages[sp[0]]['exact'])]: task(kind,statement,claim,limit)
ep=[(src+'law7491-repeal','action','document','7491 sayılı kanunun 54. maddesi bu istisna fıkrasını kaldırdı.'),(src+'registry-gazette','action','document','TBMM sicili 7491 sayılı kanunun 28 Aralık 2023 tarihinde yayımlandığını gösteriyor.'),(src+'sgk-expanded','result','document','SGK çalışan emeklilerin de ödemeden yararlandığını bildiriyor.'),(src+'sgk-paid','result','document','SGK daha önce çalışma nedeniyle ödenmeyen yaklaşık 4,7 milyon kişiye toplam 23,4 milyar TL ödeme yapıldığını bildiriyor.')]
context='2023 yılında emeklilere yapılan bir defalık 5.000 TL ödemenin çalışan emeklileri de kapsaması.'
eid=event(stem,'2023-12-27','Çalışan emeklilere bir defalık ödeme kapsamı',context,ep,limit)
records['practice_event'][-1].update(common_event_key='turkiye-2023-7491-retirement-bonus-working',occurrence_basis='7464 ve 7491 sayılı kanun metinleri, TBMM yayım sicili ve SGK faaliyet raporu.')
eids=[row[0] for row in ep]
scope=readings(topic,'event',eids)
rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
observed='7491 sayılı kanun çalışanlara ilişkin istisnayı kaldırdı. SGK, daha önce çalışma nedeniyle ödeme almayan yaklaşık 4,7 milyon kişiye toplam 23,4 milyar TL ödendiğini bildirdi.'
compare='Açıklama ve sonraki düzenleme aynı 5.000 TL ödemenin çalışma durumuna göre kapsamına ilişkindir.'
connection='Çalışma nedeniyle kapsam dışında kalanlar için yasal istisna kaldırıldı ve SGK toplu ödeme bildirdi. Ödeme 5.000 TL ve bir defalık kaldı. Görüşülen teklifin 55. maddesi kabul edilen kanunda 54. madde oldu.'
finding(result,observed,[src+'law7491-repeal',src+'registry-gazette',src+'sgk-paid'],'Kanun metni, yayım sicili ve SGK ödeme verisi ayrı okundu.')
finding(explanation,connection,sp+[src+'law7464-amount',src+'law7464-excluded',src+'law7464-exception',src+'law7491-repeal',src+'debate-article',src+'sgk-paid'],'Tutar, kapsam ve gerçekleşen ödeme ayrı değerlendirildi.')
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='Ekim 2023 açıklaması, ilk kanun ve Aralık değişikliği ayrı tarihlerdir.',authority_context='Kılıç konuşmasını Saadet Partisi milletvekili olarak yaptı. Kanunu TBMM kabul etti ve ödemeyi SGK bildirdi.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(eids)))
for kind,claim in [('practice_relation',compare),('practice_relation.target_finding_id',goal),('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',connection)]: task(kind,rid,claim,limit)
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
for name,content in [('retired-2023-draft.json',package),('retired-2023-review-draft.json',review)]:
 path=here/name
 with path.open('x') as output: output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
 print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
