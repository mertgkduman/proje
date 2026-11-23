"""3 Kasım DEM katkısı için kaynak hedefleri ve özgün pasajları denetler."""
import hashlib, json
from pathlib import Path
from arsiv import html_source_text, pdf_page_text
from uygulamalar import practice_review_targets
c = Path(__file__).resolve().parent
root = c.parents[3]
p, r = c/'nov03-dem-draft.json', c/'nov03-dem-review-draft.json'
assert hashlib.sha256(p.read_bytes()).hexdigest() == '8eda3f1baafa3f6c5f0b8cf8c6d0074e15faccf5e1fd7094ab83bfd8ed6aa7ee'
assert hashlib.sha256(r.read_bytes()).hexdigest() == '7455297c72c70d2093de684ab3473ca0434065b1b2f175d45ad2c06a2b74fdc9'
payload, review = json.loads(p.read_text()), json.loads(r.read_text())
data = dict(payload['practice_records'])
for x in payload['entries']: data.setdefault(x['kind'], []).append(x['values'])
prefix = '0406-nov03-genelgorusme-'
names = ('practice_event', 'practice_event_evidence', 'practice_contribution', 'practice_candidate')
sel = {k:[x for x in data.get(k, []) if str(x.get('id', x.get('event_id', ''))).startswith(prefix)] for k in names}
targets = practice_review_targets(data, sel)
rows = {(x['subject_kind'], x['subject_id']): x for x in review['practice_source_review']}
assert len(targets) == 12
for key, (refs, _) in targets.items(): assert key in rows and set(json.loads(rows[key]['passage_ids'])) == refs, key
versions = {x['id']: x for x in data['document_version']}
for passage in (x for x in data['passage'] if x['id'].startswith(prefix)):
    version = versions[passage['version_id']]
    path = root / 'data/practices/sources/dem' / version['original_path']
    text = pdf_page_text(path, passage['pdf_page_index']) if version['mime'] == 'application/pdf' else html_source_text(path.read_bytes())
    assert passage['exact'] in text, passage['id']
print('NOV03_TARGETS_12_AND_EIGHT_EXACT_PASSAGES_OK')
