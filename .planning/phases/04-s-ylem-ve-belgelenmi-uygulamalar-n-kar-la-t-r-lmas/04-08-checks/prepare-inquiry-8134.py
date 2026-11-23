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
aux=read(here/'inquiry-8134-v2-source-records.json')
party=aux['party_id']
package=read(data/'practices/04-yeni-yol.json')
review=read(data/'practices/04-yeni-yol-review.json')
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
            boundary_reason='Emekli aylığının asgari ücret düzeyi, genel görüşme önergesi ve esas kaydı okundu.'))
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
        aid=f'inquiry-8134-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Emekli aylığı tabanı ve hesap yöntemiyle ilgili TBMM kaydı.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='TBMM imzalı evrakı, sicili ve gelen kâğıtlar eki.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='yeni-yol'
assert sha256((data/'practices/04-yeni-yol.json').read_bytes()).hexdigest()=='c765a66c68be8962a5dcdca1866ec8fa2477d09f9a305f2ae0e5a72ecdb81769'
assert sha256((data/'practices/04-yeni-yol-review.json').read_bytes()).hexdigest()=='3193204d75d30eaf0a371a1ce2de360c5e4fb74810ce7d6f0ef82dfc9db1dd58'
topic='sosyal-guvenlik'
stem='0408-inquiry-8134'
src=stem+'-'
statement='0408-yeni-yol-2026-7573-statement'
target='0408-yeni-yol-2026-7573-target'
goal=next(e['values']['text'] for e in entries if e['kind']=='finding' and e['values']['id']==target)
context='Bülent Kaya ile 19 milletvekilinin emekli aylıklarının hesaplanması için genel görüşme talebi 17 Haziran 2026’da 8/134 numarasıyla TBMM’ye sunuldu.'
limit=('Gelen kâğıtlar eki 1 Temmuz’da evrakı listeliyor. 23 Kasım erişiminde esas kaydı Gündemde. '
       '8/134’ün ön görüşme oyu, esasa ilişkin işlemi ve önerilen değişikliklerin yürürlüğe girmesi açık.')
refs=[
    ('register-number','initiative','TBMM 8/134 esas numarasını verdi.'),
    ('register-day','action','Başkanlığa 17 Haziran 2026’da sunuldu.'),
    ('register-party','action','TBMM ilk imza sahibini Yeni Yol Partisi İstanbul Milletvekili Bülent Kaya olarak gösteriyor.'),
    ('signed-number','initiative','İmzalı metnin ilk sayfasında 8/134 yazıyor.'),
    ('signed-request','action','İmzalı önergenin gerekçesi aylık hesabı ve yasal tedbirler için genel görüşme talep ediyor.'),
    ('signed-lower-bound','action','Gerekçe, en düşük emekli aylığının asgari ücretin altında kalmaması için yasal güvence istiyor.'),
    ('signed-adjustment','action','Gerekçe ayrıca bir intibak yasasını görüşme kapsamına alıyor.'),
    ('signed-signatories','action','İmzalar sayfasında Bülent Kaya ve 19 milletvekili var.'),
    ('incoming-listed','result','1 Temmuz gelen kâğıtlar listesinde 8/134 yer alıyor.'),
    ('appendix-listed','result','108. Birleşim basılı tutanağının 931. sayfasındaki ekte 8/134 listeleniyor.'),
    ('register-pending','result','Esas sicili 23 Kasım erişiminde Gündemde gösteriyor.'),
]
evidence=[(src+pid,stage,'document',claim) for pid,stage,claim in refs]
eid=event(stem,'2026-06-17','8/134 emekli aylığı hesabı genel görüşme önergesinin sunulması',context,evidence,limit)
basis='İmzalı 8/134 önergesi, TBMM esas kaydı ve 1 Temmuz 108. Birleşim gelen kâğıtlar eki.'
records['practice_event'][-1].update(common_event_key='tbmm-28-4-8-134-basvuru',occurrence_basis=basis)
pids=[row[0] for row in evidence]
scope=readings(topic,'event',pids)
rid,result,explanation=(stem+suffix for suffix in ('-relation','-result','-explanation'))
observed=('8/134, 17 Haziran’da sunuldu ve 1 Temmuz gelen kâğıtlar ekinde yer aldı. '
          'İmzalı gerekçe en düşük emekli aylığı için asgari ücret alt sınırı ve bir intibak düzenlemesi öneriyor.')
compare=('13 Ocak’ta Yeni Yol Grubu adına savunulan asgari ücret düzeyi, 17 Haziran imzalı önergenin gerekçesinde '
         'asgari ücretin altında kalmama hükmü olarak ele alındı. 8/134 hesap yöntemi ve intibakı da görüşmeye açmayı istiyor.')
prior_pids=[e['values']['passage_id'] for e in entries if e['kind']=='finding_evidence' and e['values']['finding_id']==target]
finding(result,observed,pids,basis)
finding(explanation,compare+' '+limit,prior_pids+pids,limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,
    topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,
    result_finding_id=result,explanation_finding_id=explanation,
    temporal_context='13 Ocak sözlü tutum. 17 Haziran imzalı başvuru. 1 Temmuz gelen kâğıtlar eki. 23 Kasım sicil gözlemi.',
    authority_context='İlk imza Bülent Kaya’ya, 20 imzalı önerge gruptaki milletvekillerine ve evrakın işleme alınması TBMM’ye ait.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,
    relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(pids)))
for kind,claim in (
    ('practice_relation',compare),('practice_relation.target_finding_id',goal),
    ('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare),
):
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
for name,content in [('inquiry-8134-v2-draft.json',package),('inquiry-8134-v2-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
