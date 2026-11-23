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
aux=read(here/'fund-commission-art5-source-records.json')
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
        aid=f'fund-commission-art5-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='TBMM Plan ve Bütçe Komisyonunun 14 Ekim tutanağı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'iyi'
topic = 'makroekonomik-politika'
stem = '0407-iyi-2026-commission-art5'
src = '0407-fund-commission-art5-'
limit = ('İmzalı metin Kurul görevlilerini, Usta’nın açıklaması şirketlerin yönetim kurulu ödemelerini ele aldı. '
         'Usta metindeki yazım hatasına işaret etti. İsimli oylar, kesinleşmiş sorumluluk ve fiilî tahsil açık.')
context = ('Plan ve Bütçe Komisyonu, Taş ve Usta’nın 2/3939’un 5. maddesine ilişkin ücretlerin '
           'faiziyle geri alınması önergesini 14 Ekim’de kabul etmedi.')
evidence = [
    (src+'written-officials','initiative','document','Yazılı önerge Kurulca ihmali veya görevi yerine getirmemesi tespit edilen Kurul görevlilerini kapsıyordu.'),
    (src+'written-payment','initiative','document','Yazılı hüküm çeşitli mali ödemelerin tamamının faiziyle iadesini öngörüyordu.'),
    (src+'signers','initiative','document','Tutanakta Taş ve Usta imzaları var.'),
    (src+'correction','action','document','Usta önergenin yazımında hata olduğunu söyledi.'),
    (src+'spoken','action','document','Usta huzur hakları ve ücretlerin alınmasına yönelik sözlü açıklama yaptı.'),
    (src+'rejection','result','document','Başkan Taş ve Usta’nın önergesinin kabul edilmediğini ilan etti.'),
]
eid = event(stem,'2026-10-14','Taş ve Usta’nın 5. madde tahsil önergesinin komisyonda reddi',context,evidence,limit)
records['practice_event'][-1]['common_event_key'] = 'tbmm-komisyon-5472-2-3939-madde5-tas-usta'
refs = [r[0] for r in evidence]
scope = readings(topic,'event',refs+[src+'article'])
reason = ('Önceden belgelendirilen emsal üstü fon kazancının iadesi 4. maddenin konusuydu. '
          '5. madde önergelerinde ele alınan görevli veya yönetim kurulu ödemeleri için ayrı tarihli söylem araştırmaya açık.')
records['practice_candidate'].append(dict(id=stem+'-unmatched',scope_id=scope,event_id=eid,relation_id=None,
    state='unmatched',reason=reason,passage_ids=encoded(refs)))
task('practice_candidate',stem+'-unmatched',reason,limit)

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
for name,content in [('fund-commission-art5-draft.json',package),('fund-commission-art5-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
