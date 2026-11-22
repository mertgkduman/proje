import copy,hashlib,json,sqlite3
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); live=Path('data/practices/04-tip.json'); live_review=Path('data/practices/04-tip-review.json')
expected='1235d8eb304b6a7cbd92f36dd9fefa9fe87c21aa6ec9db771e870d502bb97f3d'; assert hashlib.sha256(live.read_bytes()).hexdigest()==expected, 'Live taban değişti; yeniden üretim gerekli.'
package=json.loads((p/'union-append-draft.json').read_text()); review=json.loads((p/'union-append-review-draft.json').read_text()); institution=json.loads((p/'institution-package-publication-day-draft.json').read_text()); inst_review=json.loads((p/'institution-review-checked-draft.json').read_text()); speech=json.loads((p/'policy-35h-statement-delta.json').read_text()); speech_review=json.loads((p/'policy-35h-review-delta.json').read_text()); inst_scope=json.loads((p/'institution-scope-delta.json').read_text()); speech_scope=json.loads((p/'policy-35h-scope-delta.json').read_text())
assert package['entries'][:len(json.loads(live.read_text())['entries'])]==json.loads(live.read_text())['entries']; assert review['practice_source_review'][:len(json.loads(live_review.read_text())['practice_source_review'])]==json.loads(live_review.read_text())['practice_source_review']
db=sqlite3.connect('file:data/releases/f67ca0a35e634035bf3aa83a46571f50/records.sqlite3?mode=ro',uri=True)
def ek(entry):
 name=entry['kind']; cols=sorted(((x[5],x[1]) for x in db.execute('pragma table_info("'+name+'")') if x[5])); assert cols,(name,entry); return (name,*(str(entry['values'].get(col)) for _,col in cols))
index={ek(e):e for e in package['entries']}
assert len(index)==len(package['entries'])
for origin in (institution['entries'],speech['entries']):
 for entry in origin:
  key=ek(entry)
  if key in index:
   old=index[key]['values']; new=entry['values']; diff={k for k in set(old)|set(new) if old.get(k)!=new.get(k)}
   allowed={'version_label'} if entry['kind']=='document_version' and new.get('id')=='0405-tip-pm-nisan-v1' else {'basis'} if entry['kind']=='source_attribution' and new.get('version_id')=='0405-tip-pm-nisan-v1' else set()
   assert diff<=allowed,(key,diff)
  else: package['entries'].append(copy.deepcopy(entry));index[key]=package['entries'][-1]
markers={'practice_contract','practice_variant_contract','practice_evidence_contract','practice_coverage_contract'}
def record_key(name,row):
 if 'id' in row:return ('id',row['id'])
 fields={'practice_event_evidence':('event_id','passage_id','stage'),'practice_evidence_assessment':('event_id','passage_id','stage'),'practice_scope_source':('scope_id','version_id','inspected_at'),'practice_dispute_evidence':('dispute_id','passage_id','point','role'),'practice_actor_period':('contribution_id',)}
 assert name in fields,(name,row);return tuple(row[x] for x in fields[name])
for records in (institution['practice_records'],speech['practice_records'],inst_scope['practice_records'],speech_scope['practice_records']):
 for name,rows in records.items():
  if name in markers:
   assert rows==package['practice_records'][name],name;continue
  dest=package['practice_records'].setdefault(name,[]); existing={record_key(name,x):x for x in dest}
  for raw in rows:
   row=copy.deepcopy(raw)
   if name=='practice_relation' and row['id']=='0405-tip-istifa-iliski':row['scope_id']=next(x['id'] for x in inst_scope['practice_records']['practice_scope_v2'] if x['research_kind']=='event')
   if name=='practice_relation' and row['id']=='0405-tip-pm35-iliski':row['scope_id']=next(x['id'] for x in package['practice_records']['practice_scope_v2'] if x['topic_id']=='calisma-sureleri' and x['research_kind']=='event')
   key=record_key(name,row)
   if key in existing:assert row==existing[key],(name,key)
   else:dest.append(row);existing[key]=row
for extra in (inst_review,speech_review):
 for key in ('practice_source_review','source_review_refs'):review[key].extend(copy.deepcopy(extra[key]))
for key in ('practice_source_review','source_review_refs'):
 ids=[(r['subject_kind'],r['subject_id']) for r in review[key]];assert len(ids)==len(set(ids)),key
assert not package['practice_records'].get('practice_closure'), 'Hiçbir kapsam kapatılmamalı.'
(p/'combined-append-draft.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n');(p/'combined-append-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('PREFLIGHT_OK',len(package['entries']),'entries',len(package['practice_records']['practice_event']),'events',len(review['practice_source_review']),'agent reviews; 0 closure')
