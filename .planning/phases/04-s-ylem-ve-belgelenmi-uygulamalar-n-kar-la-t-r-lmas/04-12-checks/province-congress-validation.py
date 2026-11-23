"""Verify two provincial results and one open count in both report views."""

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
case = 'province-congress'
stem = '0412-province-congress'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == '05e78901725c688c506b15b89aa918cb2e1cabdfd8053166d08883a7fa175bd0'
assert harness.sha(review) == '00e7019d2a2f6b114184b6efd8f1baae2f4105b7bd0b6702d5151b07438a92cf'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (28, 25, 0)
receipt = harness.main(package, review, case, stem + '-afyon-event', stem + '-afyon-relation',
                       None, expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identities in (
        ('practice_statement', (stem + '-statement',)),
        ('practice_event', tuple(f'{stem}-{label}-event' for label in ('afyon', 'tokat', 'konya'))),
        ('practice_relation', tuple(f'{stem}-{label}-relation' for label in ('afyon', 'konya'))),
        ('practice_candidate', (stem + '-tokat-candidate',)),
    ):
        for identity in identities:
            row = next(row for row in records[table] if row['id'] == identity)
            assert row in export[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?', (stem + '-tokat-event',)).fetchone()
    assert not db.execute("SELECT 1 FROM practice_event_evidence WHERE event_id=? AND stage='result'",
                          (stem + '-tokat-event',)).fetchone()
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    for kind, terms in (
        (f'practice-{stem}-afyon-relation', ('Hikmet Bülbül', 'Adnan Demirel', 'tek liste')),
        (f'practice-{stem}-konya-relation', ('Mehmet Ali Yavuz', '20 asıl yönetim üyesi', 'disiplin kurulu')),
        (f'unmatched-{stem}-tokat-candidate', ('Seyfettin Yüksekkaya', 'oylamanın başladığı', 'sayım')),
    ):
        anchor = f'{view}-{kind}'
        tag = f'id="{anchor}"'
        assert report.count(tag) == 1 and f'href="#{anchor}"' in report, tag
        card = report.split(tag, 1)[1].split('</article>', 1)[0]
        for term in terms:
            assert term.casefold() in card.casefold(), (view, kind, term)
print('DEMOKRAT_PROVINCE_CONGRESS_BOTH_VIEWS_OK', folder, flush=True)
