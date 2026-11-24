"""Verify the two collective bargaining cases in the archive and report."""

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
case = 'izmir-tis'
stem = '0412-izmir-tis'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == 'eef53c468b7991faea8f26084307192ab849a59a034d6e8a2cc0a033a6842937'
assert harness.sha(review) == '9ff446ff497391537367ab3f9868fd0fb66be896cd4ec88c89ef5ac0e903d0a5'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']),
        len(records['practice_closure'])) == (33, 30, 0)
receipt = harness.main(package, review, case, stem + '-izelman-event', stem + '-izelman-relation',
                       None, expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
report = (folder / 'index.html').read_text()
labels = ('izelman', 'izenerji')
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identities in (
        ('practice_statement', (stem + '-statement',)),
        ('practice_event', tuple(f'{stem}-{label}-event' for label in labels)),
        ('practice_relation', tuple(f'{stem}-{label}-relation' for label in labels)),
    ):
        for identity in identities:
            row = next(row for row in records[table] if row['id'] == identity)
            assert row in export[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
        if table == 'practice_event':
            assert {row[0] for row in db.execute('SELECT event_at FROM practice_event WHERE id LIKE ?',
                                                 (stem + '-%',))} == {'2025-06-04'}
    relation_ids = {row[0] for row in db.execute('SELECT id FROM practice_relation WHERE statement_id=?',
                                                (stem + '-statement',))}
    assert relation_ids == {f'{stem}-{label}-relation' for label in labels}

for view in ('party', 'comparison'):
    for label, exact in (
        ('izelman', '1 ve 3 numaralı sendika şubeleriyle imza'),
        ('izenerji', 'yüzde 30 artış oranının kabul edildiğini 19 Haziran’da'),
    ):
        anchor = f'{view}-practice-{stem}-{label}-relation'
        start = f'id="{anchor}"'
        assert report.count(start) == 1 and f'href="#{anchor}"' in report
        card = report.split(start, 1)[1].split('</article>', 1)[0]
        assert escape(exact).casefold() in card.casefold(), (view, label)
print('DEMOCRAT_IZMIR_TIS_BOTH_VIEWS_OK', folder, flush=True)
