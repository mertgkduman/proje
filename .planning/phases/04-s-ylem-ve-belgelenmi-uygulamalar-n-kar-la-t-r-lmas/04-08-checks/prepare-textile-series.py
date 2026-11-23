"""Add the retrospective export series evidence without altering the original dispute."""

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
aux=read(here/'textile-series-source-records.json')
party=aux['party_id']
package=read(here/'textile-2881-draft.json')
review=read(here/'textile-2881-review-draft.json')
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
        aid=f'textile-series-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='İlgili politika söylemi, önerge veya kanun teklifi.',state='examined',attempt_ids=encoded([aid])))
    return sid
assert party=='yeni-yol'
assert sha256((here/'textile-2881-draft.json').read_bytes()).hexdigest()=='157bb81f42eacf833157aaad22e678302924288a6b8a3820a1b4015f67c89fff'
assert sha256((here/'textile-2881-review-draft.json').read_bytes()).hexdigest()=='fe6419877162c9d2cfb75cc56c58fee38bb3847728a85fe734450c5bb3b7bc02'
assert 19_316_151*1000-19_242_984*1000 == 73_167_000
limit=('İki rapor farklı baskılarda aynı dönem ve sektör için farklı değer veriyor. '
       'Önerge yazarlarının kullandığı baskı ve iki tablonun farkının teknik nedeni açık.')
dispute='0408-textile-2881-export-dispute'
refs=[]
for year,role,point in (
    (2023,'support','İHKİB 2023 raporunun 2023 sütununda 19.316.151 bin dolar yazıyor. Bu tutar bir ondalık basamakta 19,3 milyar dolara yuvarlanıyor.'),
    (2024,'conflict','İHKİB 2024 raporunun 2023 sütununda 19.242.984 bin dolar yazıyor. Bu tutar bir ondalık basamakta 19,2 milyar dolara yuvarlanıyor. İki baskının aritmetik farkı 73.167.000 dolar.'),
):
    stem=f'0408-textile-series-{year}'
    pid=stem+'-value'
    section=passages[pid]['section']
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,point=point,source_position=section,role=role))
    task('practice_dispute_evidence','|'.join((dispute,pid,point,role)),point,limit)
    refs.extend((pid,stem+'-unit'))
readings('sanayi-politikasi','event',refs)

for entry in entries:
 destination=snapshot.setdefault(entry['kind'],[])
 if entry['values'] not in destination:destination.append(entry['values'])
for table,rows in records.items():
 destination=snapshot.setdefault(table,[]);destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot,records,[entry['values']['id'] for entry in entries if entry['kind']=='passage'],party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
 pids,owners=targets[(kind,identity)];assert party in owners
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),supported_claim=claim,limitations=limitation,result='reviewed',reason=kind+' kaynak metni, tarih ve kapsam sınırları okundu. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews];package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('textile-series-draft.json',package),('textile-series-review-draft.json',review)]:
 path=here/name
 with path.open('x') as output:output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
 print(name,sha256(path.read_bytes()).hexdigest())
print('YENI_YOL_TEXTILE_SERIES_SEMANTIC_PASS',len(tasks))
