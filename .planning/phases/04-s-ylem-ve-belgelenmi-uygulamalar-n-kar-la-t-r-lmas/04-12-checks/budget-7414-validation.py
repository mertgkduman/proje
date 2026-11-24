"""Check the 2022 budget comparison and the separate 7490 accounts."""

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', checks.parent / '04-04-checks' / 'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'demokrat'
case = 'budget-7414'
base = f'0412-{case}'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']),
        len(records['practice_closure'])) == (60, 47, 0)
receipt = harness.main(package, review, case, f'{base}-adoption-event', f'{base}-adoption-relation',
                       None, expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
report = (folder / 'index.html').read_text()
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, suffixes in (
        ('practice_statement', ('statement',)),
        ('practice_event', ('filing-event', 'adoption-event', 'accounts-event')),
        ('practice_candidate', ('filing-candidate', 'adoption-candidate', 'accounts-candidate')),
        ('practice_relation', ('adoption-relation',)),
    ):
        for suffix in suffixes:
            ident = f'{base}-{suffix}'
            expected = next(row for row in records[table] if row['id'] == ident)
            actual = db.execute(f'SELECT * FROM {table} WHERE id=?', (ident,)).fetchone()
            assert expected in export[table] and expected == dict(actual), ident
    votes = dict(db.execute('SELECT passage_id, supported_point FROM practice_event_evidence WHERE event_id=?',
                            (f'{base}-adoption-event',)))
    for suffix, text in (('debate-chair', '266'), ('roll-accept', '265'), ('roll-reject', '117'),
                         ('roll-duplicate', 'iki mükerrer'), ('roll-uysal', 'KATILMADI'),
                         ('roll-enginyurt', 'KATILMADI')):
        assert text in votes[f'{base}-{suffix}-p'], suffix
for view in ('party', 'comparison'):
    cards = {
        f'{view}-practice-{base}-adoption-relation': ('7414', '7 Temmuz', '20,2', 'KATILMADI'),
        f'{view}-unmatched-{base}-filing-candidate': ('1/284', '20 Haziran 2022'),
        f'{view}-unmatched-{base}-accounts-candidate': ('7490', '25 Aralık 2023'),
    }
    for anchor, phrases in cards.items():
        start = f'id="{anchor}"'
        assert report.count(start) == 1 and f'href="#{anchor}"' in report
        card = report.split(start, 1)[1].split('</article>', 1)[0]
        for phrase in phrases:
            assert phrase in card, (view, anchor, phrase)
print('DEMOCRAT_BUDGET_7414_BOTH_VIEWS_OK', folder, flush=True)
