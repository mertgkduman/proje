import json,hashlib
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); live=Path('data/practices/04-tip.json'); review_path=Path('data/practices/04-tip-review.json')
package=json.loads(live.read_text()); review=json.loads(review_path.read_text()); delta=json.loads((p/'policy-35h-statement-delta.json').read_text()); new_review=json.loads((p/'policy-35h-review-delta.json').read_text())
assert package['party_id']=='tip' and package['stage']=='partial'
package['entries'].extend(delta['entries'])
for name,rows in delta['practice_records'].items():package['practice_records'].setdefault(name,[]).extend(rows)
review['practice_source_review'].extend(new_review['practice_source_review']);review['source_review_refs'].extend(new_review['source_review_refs'])
keys=[(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']];assert len(keys)==len(set(keys))
(p/'policy-35h-append-draft.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n');(p/'policy-35h-append-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('DRAFT ONLY live sha',hashlib.sha256(live.read_bytes()).hexdigest(),'entries',len(package['entries']))
