"""Doğrulanmış beş olaylı canlı çifte sonuç açığını koruyarak Silopi adayını ekle."""
import hashlib,json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks');data=Path('data/practices');base=(data/'04-dem.json').read_bytes();review_bytes=(data/'04-dem-review.json').read_bytes()
assert hashlib.sha256(base).hexdigest()=='855757908a084e2799acebacaa4c6c5934d2dba4a71124059228c55c04f3f37a'
assert hashlib.sha256(review_bytes).hexdigest()=='1a1552293b992d2488066e2bbcd6121b31e77c7ac23414ff9fbcbc0560baf6a1'
package=json.loads(base);review=json.loads(review_bytes);part=json.loads((p/'silopi-event-fragment-draft.json').read_text());r=json.loads((p/'silopi-event-review-draft.json').read_text());package['entries']+=part['entries']
for k,rows in part['practice_records'].items():package['practice_records'].setdefault(k,[]).extend(rows)
review['practice_source_review']+=r['practice_source_review'];review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]; keys=[(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']];assert len(keys)==len(set(keys))
(p/'silopi-combined-draft.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n');(p/'silopi-combined-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n');print('SILOPI_COMBINED_DRAFT',len(package['entries']),len(keys))
