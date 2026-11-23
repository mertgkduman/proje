"""Verify two agenda actions and dated IYI program evidence."""

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
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'iyi'
case = 'agenda-104-historic'
stem = '0407-agenda-104-'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == '5814587049d6af3f55d273eb8d2057af2cf2a22ae2ea3bc2051aac2453c148b1'
assert harness.sha(review) == '7eba5cdfb8a96ddd885d57450a06e01a64db5f27c991401c7dcea24d695fa028'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (19, 12, 0)
receipt = harness.main(package, review, case, stem + '2881-event', stem + '2881-relation',
                       None, expected_party='iyi', namespace='gsd-0407')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    row_ids = {f'practice_{kind}': tuple(stem + n + '-' + kind for n in ('2881', '2882'))
               for kind in ('event', 'relation', 'statement', 'contribution', 'candidate')}
    row_ids['practice_dispute'] = (stem + '2882-count-dispute',)
    for table, identities in row_ids.items():
        for identity in identities:
            want = next(row for row in records[table] if row['id'] == identity)
            assert want in export[table]
            row = db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone()
            assert dict(row) == want
    for n in ('2881', '2882'):
        row = db.execute('SELECT authority_passage_id FROM practice_contribution WHERE id=?',
                         (stem + n + '-contribution',)).fetchone()
        assert row[0] == stem + 'floor-authority-' + n
        row = db.execute('SELECT version_id,period_basis FROM practice_statement WHERE id=?',
                         (stem + n + '-statement',)).fetchone()
        assert row[0] == '0407-iyi-program-2019-v1' and '3 Mart 2019' in row[1]
    dispute = db.execute('SELECT role FROM practice_dispute_evidence WHERE dispute_id=?',
                         (stem + '2882-count-dispute',)).fetchall()
    assert sorted(row[0] for row in dispute) == ['conflict', 'support', 'support', 'support']
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    for n, terms in (
        ('2881', ('10/2881', 'Yasin Öztürk', 'markalaşma', '3 Mart 2019', '11 Kasım 2026')),
        ('2882', ('10/2882', 'Mehmet Akalın', '19 milletvekili', '20 milletvekili', 'Gündemde', '3 Mart 2019')),
    ):
        anchor = f'{view}-practice-{stem}{n}-relation'
        tag = f'id="{anchor}"'
        assert report.count(tag) == 1 and f'href="#{anchor}"' in report, anchor
        card = report.split(tag, 1)[1].split('</article>', 1)[0]
        for phrase in terms:
            assert phrase.casefold() in card.casefold(), (view, n, phrase)
print('IYI_AGENDA_104_HISTORIC_BOTH_VIEWS_OK', folder, flush=True)
