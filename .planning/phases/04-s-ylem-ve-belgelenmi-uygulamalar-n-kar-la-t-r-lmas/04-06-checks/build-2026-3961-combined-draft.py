"""Doğrulanmış canlı DEM çiftine 2026 adayını ekler; canlı dosyaları yazmaz."""
import hashlib,json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks'); data=Path('data/practices')
base=(data/'04-dem.json').read_bytes(); review_bytes=(data/'04-dem-review.json').read_bytes()
assert hashlib.sha256(base).hexdigest()=='92a52df42a1d28842fdc501c679fa5a7451e988d017e750b2764968a2e12f49b'
assert hashlib.sha256(review_bytes).hexdigest()=='95aeb8cd644741e37067d2219f7396f8463318a98702c7271a2addc88ca6a477'
package=json.loads(base);review=json.loads(review_bytes);part=json.loads((p/'2026-3961-event-fragment-draft.json').read_text()); r=json.loads((p/'2026-3961-event-review-draft.json').read_text())
package['entries']+=part['entries']
for k,rows in part['practice_records'].items(): package['practice_records'].setdefault(k,[]).extend(rows)
review['practice_source_review']+=r['practice_source_review'];review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
keys=[(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']];assert len(keys)==len(set(keys))
(p/'2026-3961-combined-draft.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n')
(p/'2026-3961-combined-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('3961_COMBINED_DRAFT',len(package['entries']),len(keys))
