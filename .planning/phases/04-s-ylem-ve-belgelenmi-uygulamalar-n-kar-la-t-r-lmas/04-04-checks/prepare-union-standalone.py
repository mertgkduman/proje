import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');pkg=json.loads((p/'package-istanbul-draft.json').read_text());review=json.loads((p/'istanbul-review-draft.json').read_text());slice=json.loads((p/'union-slice-draft.json').read_text());rs=json.loads((p/'union-review-slice-draft.json').read_text());pkg['entries']+=slice['entries']
for key,rows in slice['practice_records'].items():pkg['practice_records'][key]+=rows
review['practice_source_review']+=rs['practice_source_review'];review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
(p/'package-union-standalone-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n');(p/'union-standalone-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
