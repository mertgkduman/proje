import json,hashlib
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); live=Path('data/practices/04-tip.json'); live_review=Path('data/practices/04-tip-review.json')
package=json.loads(live.read_text()); review=json.loads(live_review.read_text()); delta=json.loads((p/'union-slice-draft.json').read_text()); scopes=json.loads((p/'union-scope-delta.json').read_text()); added_review=json.loads((p/'union-review-checked-draft.json').read_text())
assert package['party_id']=='tip' and package['stage']=='partial'
event_scope=next(x['id'] for x in scopes['practice_records']['practice_scope_v2'] if x['research_kind']=='event')
for item in delta['practice_records']['practice_relation']: item['scope_id']=event_scope
package['entries'].extend(delta['entries'])
for group in (delta['practice_records'],scopes['practice_records']):
 for name,rows in group.items(): package['practice_records'].setdefault(name,[]).extend(rows)
review['practice_source_review'].extend(added_review['practice_source_review']);review['source_review_refs'].extend(added_review['source_review_refs'])
keys=[(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']]; assert len(keys)==len(set(keys))
(p/'union-append-draft.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n');(p/'union-append-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('DRAFT ONLY live sha',hashlib.sha256(live.read_bytes()).hexdigest(),'entries',len(package['entries']))
