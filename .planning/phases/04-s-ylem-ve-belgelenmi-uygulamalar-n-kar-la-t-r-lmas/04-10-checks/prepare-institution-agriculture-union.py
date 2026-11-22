import copy,datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent;read=lambda p:json.loads(Path(p).read_text())
live=read('data/practices/04-emep.json');live_review=read('data/practices/04-emep-review.json')
assert len(live['practice_records']['practice_event'])==23
assert hashlib.sha256(Path('data/practices/04-emep.json').read_bytes()).hexdigest()=='d8e191f5edd4000a47d1e48f41ff7a1629c84852bb5aad5a8ef65c28713d8076'
base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
specs=[('izmit-congress-union-draft.json','izmit-account-union-v2-draft.json','izmit-account-union-v2-review-draft.json'),('izmit-congress-union-draft.json','luleburgaz-congress-branch-draft.json','luleburgaz-congress-branch-review-draft.json'),('mandate-3761-source-faithful-v2-draft.json','seasonal-agriculture-branch-draft.json','seasonal-agriculture-branch-review-draft.json')]
package=copy.deepcopy(live);entries=package['entries'];records=package['practice_records'];review_candidates={};details=[]
for oldname,newname,reviewname in specs:
 old=read(D/oldname);new=read(D/newname);review=read(D/reviewname)
 added_entries=[x for x in new['entries'] if x not in old['entries']]
 for e in added_entries:
  if e not in entries:entries.append(e)
 added_records={}
 for table,rows in new['practice_records'].items():
  delta=[x for x in rows if x not in old['practice_records'][table]]
  for row in delta:
   if row not in records[table]:records[table].append(row)
  if delta:added_records[table]=len(delta)
 for r in review['practice_source_review']:review_candidates[(r['subject_kind'],r['subject_id'])]=r
 details.append(dict(base=oldname,branch=newname,added_entries=len(added_entries),added_records=added_records))
data=copy.deepcopy(base)
for entry in entries:
 if entry['values'] not in data.setdefault(entry['kind'],[]):data[entry['kind']].append(entry['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
new_passages={x['passage_id'] for x in records['practice_event_evidence']}
targets=rules.practice_review_package_targets(data,records,new_passages,party_id='emep');passages={x['id']:x for x in data['passage']}
old={(r['subject_kind'],r['subject_id']):r for r in live_review['practice_source_review']};reviews=[];updated=[]
allowed={('practice_event','0410-izmit-2020-congress-event'),('practice_relation','0410-izmit-2020-congress-relation')}
for key,(pids,parties) in sorted(targets.items()):
 r=copy.deepcopy(old.get(key) or review_candidates[key]);old_pids=set(json.loads(r['passage_ids']))
 if old_pids!=pids:
  assert key in allowed and old_pids<=pids
  r['passage_ids']=json.dumps(sorted(pids));r['source_version_ids']=json.dumps(sorted({passages[x]['version_id'] for x in pids}));r['inspected_sections']=json.dumps(sorted({passages[x]['section'] for x in pids}),ensure_ascii=False)
  r['supported_claim']+=' Aynı İzmit haberinde mali raporun kongrede okunduğu da bildiriliyor.'
  r['limitations']+=' Okunma, mali raporun kabul edildiğini veya hesapların doğruluğunu göstermez.'
  r['reason']+=' Ek mali rapor pasajı yeniden okundu.'
  updated.append(dict(subject=key,old_passages=sorted(old_pids),new_passages=sorted(pids)))
 reviews.append(r)
assert {tuple(x['subject']) for x in updated}==allowed
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets))
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
assert all(v in entries for v in live['entries'])
assert all(all(v in records[k] for v in rows) for k,rows in live['practice_records'].items())
for key,r in old.items():
 if key not in allowed:assert r in reviews
assert len(records['practice_event'])==26 and len(records['practice_relation'])==27 and not records['practice_closure']
for n,obj in [('institution-agriculture-union-draft.json',package),('institution-agriculture-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs)),('institution-agriculture-union-notes.json',dict(base_live_sha256='d8e191f5edd4000a47d1e48f41ff7a1629c84852bb5aad5a8ef65c28713d8076',branches=details,updated_live_reviews=updated,prior_review_subset=True,limits='İzmit mali raporun okunması, kabul veya doğruluk anlamına gelmez; Kocaeli ve Gebze için dönemdeki ara tüzük değişikliği bilinmiyor. TBMM yanıtı sorunların giderildiğini kanıtlamaz.',closures=0))]:
 with (D/n).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('UNION_PACKAGE_TARGET_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
