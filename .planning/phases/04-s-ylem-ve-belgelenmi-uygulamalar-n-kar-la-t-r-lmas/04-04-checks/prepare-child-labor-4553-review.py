import json
from datetime import datetime, timezone
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
old = json.loads((p/'child-labor-review-slice-draft.json').read_text())['practice_source_review']
reviews = []
for item in old:
    if item['subject_kind'].startswith('practice_statement'):
        continue
    x = dict(item)
    x['reviewed_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    for key in ('subject_id', 'source_version_ids', 'passage_ids', 'inspected_sections', 'reason'):
        x[key] = x[key].replace('4687', '4553')
    x['supported_claim'] = x['supported_claim'].replace('19 milletvekilini', '20 milletvekilini').replace('12 Ekimdir', '30 Eylüldür')
    reviews.append(x)
(p/'child-labor-4553-review-draft.json').write_text(json.dumps(dict(status='draft_unvalidated', practice_source_review=reviews), ensure_ascii=False, indent=2)+'\n')
