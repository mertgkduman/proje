"""Verify the olive-oil quota, trade restriction and separate fund decision."""

from html import escape
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
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'demokrat'
case = 'olive-oil'
stem = '0412-olive-oil'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == '607a85fdcfecbf97bdeb5556facf9a5bc3fba5cc0ee4ed8d0f83fdca4d58a351'
assert harness.sha(review) == '1a5d0ceec3d179f00e81f8f1ea3e71047981a54f4cd0a4acc71671c1d6d714c1'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']),
        len(records['practice_closure'])) == (41, 34, 0)
receipt = harness.main(package, review, case, stem + '-quota-event', stem + '-quota-relation',
                       None, expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
report = (folder / 'index.html').read_text()
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identities in (
        ('practice_statement', (stem + '-statement',)),
        ('practice_event', tuple(f'{stem}-{label}-event' for label in ('quota', 'removal', 'fund'))),
        ('practice_relation', tuple(f'{stem}-{label}-relation' for label in ('quota', 'removal'))),
        ('practice_candidate', (stem + '-fund-candidate',)),
    ):
        for identity in identities:
            row = next(row for row in records[table] if row['id'] == identity)
            assert row in export[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
    assert tuple(db.execute('SELECT state,relation_id FROM practice_candidate WHERE id=?',
                            (stem + '-fund-candidate',)).fetchone()) == ('unmatched', None)
    dates = db.execute('SELECT event_at FROM practice_event WHERE id LIKE ? ORDER BY event_at', (stem + '%',))
    assert [r[0] for r in dates] == ['2024-06-01', '2024-09-13', '2024-09-14']
    assert db.execute('SELECT count(*) FROM manual_passage WHERE passage_id LIKE ?', (stem + '%',)).fetchone()[0] == 4
for view in ('party', 'comparison'):
    for case_key, expected in (
        (f'practice-{stem}-quota-relation', ('50 bin ton', '1 Haziran', 'kota')),
        (f'practice-{stem}-removal-relation', ('13 Eylül', 'kısıtların', 'kaldırıldığını')),
        (f'unmatched-{stem}-fund-candidate', ('8957', '20 sent', '14 Eylül')),
    ):
        anchor = f'{view}-{case_key}'
        start = f'id="{anchor}"'
        assert report.count(start) == 1 and f'href="#{anchor}"' in report
        card = report.split(start, 1)[1].split('</article>', 1)[0]
        for phrase in expected:
            assert escape(phrase).casefold() in card.casefold(), (view, case_key, phrase)
print('DEMOCRAT_OLIVE_OIL_BOTH_VIEWS_OK', folder, flush=True)
