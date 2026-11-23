"""3 Kasım DEM katkısı için kaynak hedefleri ve özgün pasajları denetler."""
import hashlib, json
from pathlib import Path
from arsiv import html_source_text, pdf_page_text
from uygulamalar import practice_review_targets, validate_practice_source_review
c = Path(__file__).resolve().parent
root = c.parents[3]
p, r = c/'teacher-4314-dem-draft.json', c/'teacher-4314-dem-review-draft.json'
assert hashlib.sha256(p.read_bytes()).hexdigest() == 'af249fce72f3d37a197b087d725a2a8094ef3bf6ef9c94c5c6c8c4b5574d652d'
assert hashlib.sha256(r.read_bytes()).hexdigest() == '8888877de623335b07f47d6b6be109cdddb54ed7c88a0bf155a3b5496c534bce'
payload, review = json.loads(p.read_text()), json.loads(r.read_text())
data = dict(payload['practice_records'])
for x in payload['entries']: data.setdefault(x['kind'], []).append(x['values'])
for kind in ('practice_event','practice_candidate','practice_attempt_v2','document','document_version','passage','practice_scope_source'):
    keys = [(x['scope_id'],x['version_id']) if kind == 'practice_scope_source' else x['id'] for x in data.get(kind,[])]
    assert len(keys) == len(set(keys)), kind
prefix = '0406-dem-teacher-4314-'
names = ('practice_event', 'practice_event_evidence', 'practice_contribution', 'practice_candidate')
sel = {k:[x for x in data.get(k, []) if str(x.get('id', x.get('event_id', ''))).startswith(prefix)] for k in names}
targets = practice_review_targets(data, sel)
rows = {(x['subject_kind'], x['subject_id']): x for x in review['practice_source_review']}
assert len(targets) == 12
for key, (refs, _) in targets.items(): assert key in rows and set(json.loads(rows[key]['passage_ids'])) == refs, key
validate_practice_source_review(data, [rows[key] for key in targets], selection=sel)
versions = {x['id']: x for x in data['document_version']}
for passage in (x for x in data['passage'] if x['id'].startswith(prefix)):
    version = versions[passage['version_id']]
    path = root / 'data/practices/sources/dem' / version['original_path']
    text = pdf_page_text(path, passage['pdf_page_index']) if version['mime'] == 'application/pdf' else html_source_text(path.read_bytes())
    assert passage['exact'] in text or (not text.strip() and any(m['passage_id'] == passage['id'] for m in data.get('manual_passage', []))), passage['id']
print('TEACHER_4314_TARGETS_12_AND_PASSAGES_OK')
