"""Hakkâri adayının üstüne 10/1831 adayını ekler; canlı pakete yazmaz."""
import hashlib,json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
def read(name):return json.loads((p/name).read_text())
base_name='hakkari-combined-draft.json';base=read(base_name);part=read('101831-event-fragment-draft.json');base['entries']+=part['entries']
for kind,rows in part['practice_records'].items():base['practice_records'][kind]+=rows
review=read('hakkari-combined-review-draft.json');review['practice_source_review']+=read('101831-event-review-draft.json')['practice_source_review'];review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
keys=[(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']];assert len(set(keys))==len(keys)
(p/'101831-combined-draft.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n');(p/'101831-combined-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('COMMISSION_COMBINED_DRAFT',len(base['entries']),len(keys),'hakkari_sha256',hashlib.sha256((p/base_name).read_bytes()).hexdigest())
