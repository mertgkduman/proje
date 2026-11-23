"""Verify the teacher workshop and follow-up in the isolated party preview."""

import importlib.util
import json
from pathlib import Path
import sqlite3

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', checks.parent / '04-04-checks' / 'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'saadet'
case = 'private-teacher-meetings'
draft_path = checks / f'{case}-draft.json'
review_path = checks / f'{case}-review-draft.json'
assert harness.sha(draft_path) == '2ce22377ec3adf36a67503c8374388619fb4f7f447a95244bf1a0ff352f3a057'
assert harness.sha(review_path) == '39c9c16243e3b3f7f16356e2771ca0546717721028381e8a62f505b6abcce54d'
records = json.loads(draft_path.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (18, 14, 0)
first = '0411-private-teachers-2026-07-30'
second = '0411-private-teachers-2026-08-12'
receipt = harness.main(draft_path, review_path, case, first + '-event', first + '-relation',
                       None, expected_party='saadet', namespace='gsd-0411')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identities in (
        ('practice_event', (first + '-event', second + '-event')),
        ('practice_relation', (first + '-relation',)),
        ('practice_candidate', (first + '-candidate', second + '-unmatched')),
    ):
        for identity in identities:
            row = next(row for row in records[table] if row['id'] == identity)
            assert row in export[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
    assert db.execute('SELECT state FROM practice_candidate WHERE id=?', (second + '-unmatched',)).fetchone()[0] == 'unmatched'
    assert db.execute('SELECT count(*) FROM practice_event WHERE event_at LIKE ? AND common_event_key LIKE ?',
                      ('2026-08-%', 'csgb-ozel-okul-ogretmenleri-%')).fetchone()[0] == 1
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    for kind, identity, terms in (
        ('practice', first + '-relation', ('30 Temmuz', 'kalıcı düzenlemenin yürürlüğe', 'teknik çalışma')),
        ('unmatched', second + '-unmatched', ('12 Ağustos', 'üçüncü', 'taban ücret')),
    ):
        anchor = f'{view}-{kind}-{identity}'
        tag = f'id="{anchor}"'
        assert report.count(tag) == 1 and f'href="#{anchor}"' in report, tag
        card = report.split(tag, 1)[1].split('</article>', 1)[0]
        for term in terms:
            assert term.casefold() in card.casefold(), (view, identity, term)
print('SAADET_PRIVATE_TEACHER_MEETINGS_BOTH_VIEWS_OK', folder, flush=True)
