import json
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
pkg = json.loads((p/'package-istanbul-draft.json').read_text())
review = json.loads((p/'istanbul-review-draft.json').read_text())
for name in ('child-labor', 'child-labor-4553'):
    fragment = json.loads((p/(name+'-slice-draft.json')).read_text())
    pkg['entries'] += fragment['entries']
    for key, rows in fragment['practice_records'].items():
        pkg['practice_records'][key] += rows
    review['practice_source_review'] += json.loads((p/(name+'-review-slice-draft.json' if name == 'child-labor' else name+'-review-draft.json')).read_text())['practice_source_review']
review['source_review_refs'] = [dict(subject_kind=x['subject_kind'], subject_id=x['subject_id']) for x in review['practice_source_review']]
keys = [(r['subject_kind'], r['subject_id']) for r in review['practice_source_review']]
assert len(keys) == len(set(keys))
(p/'package-child-labor-standalone-draft.json').write_text(json.dumps(pkg, ensure_ascii=False, indent=2)+'\n')
(p/'child-labor-standalone-review-draft.json').write_text(json.dumps(review, ensure_ascii=False, indent=2)+'\n')
