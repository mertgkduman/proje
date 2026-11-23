"""Verify the Yeni Yol group contribution to the 24 June agenda item."""

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
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'yeni-yol'
case = 'teacher-4314'
stem = '0408-yeni-yol-teacher-4314'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == 'c765a66c68be8962a5dcdca1866ec8fa2477d09f9a305f2ae0e5a72ecdb81769'
assert harness.sha(review) == '3193204d75d30eaf0a371a1ce2de360c5e4fb74810ce7d6f0ef82dfc9db1dd58'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (19, 11, 0)
receipt = harness.main(package, review, case, stem + '-event', '0408-chair-rotation-relation',
                       None, expected_party='yeni-yol', namespace='gsd-0408')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identity in (
        ('practice_event', stem + '-event'),
        ('practice_candidate', stem + '-candidate'),
        ('practice_contribution', stem + '-contribution'),
    ):
        row = next(row for row in records[table] if row['id'] == identity)
        assert row in export[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?', (stem + '-event',)).fetchone()
    assert db.execute('SELECT common_event_key FROM practice_event WHERE id=?', (stem + '-event',)).fetchone()[0] == 'tbmm-28-4-106-10-4314-gundem'
    assert db.execute('SELECT contribution_kind FROM practice_contribution WHERE id=?',
                      (stem + '-contribution',)).fetchone()[0] == 'task'
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-unmatched-{stem}-candidate'
    tag = f'id="{anchor}"'
    assert report.count(tag) == 1 and f'href="#{anchor}"' in report, tag
    card = report.split(tag, 1)[1].split('</article>', 1)[0]
    for term in ('10/4314', 'Mehmet Karaman', 'taban maaş', 'Gündemde', 'gündem talebinin kabul edilmediğini'):
        assert term.casefold() in card.casefold(), (view, term)
print('YENI_YOL_TEACHER_4314_BOTH_VIEWS_OK', folder, flush=True)
