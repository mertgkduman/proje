"""Verify both January meetings and their earlier public announcement."""

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
case = 'january-visits'
stem = '0411-jan-visits'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == 'b09e94b74966a785d2cc84ec2c6934979ddc96532e84c8946c980bf9fa49eb8a'
assert harness.sha(review) == 'b4e37bb765995d44b48f691747d717f399088c6a364cd9098fa22256d3966dfa'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (25, 21, 0)
labels = ('dem', 'iyi')
receipt = harness.main(package, review, case, stem + '-dem-event', stem + '-dem-relation',
                       None, expected_party='saadet', namespace='gsd-0411')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
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
    matched = db.execute('SELECT id FROM practice_relation WHERE statement_id=?', (stem + '-statement',))
    assert {row[0] for row in matched} == {f'{stem}-{label}-relation' for label in labels}
    dates = db.execute('SELECT event_at FROM practice_event WHERE id LIKE ? ORDER BY event_at', (stem + '-%',))
    assert [row[0] for row in dates] == ['2026-01-29', '2026-01-30']
report = (folder / 'index.html').read_text()

for view in ('party', 'comparison'):
    for label, terms in (
        ('dem', ('Mahmut Arıkan', 'Tuncer Bakırhan', 'ortak basın açıklaması', 'rapor yayımlaması açık')),
        ('iyi', ('Müsavat Dervişoğlu', 'nezaket ziyareti', 'bildirilen haftadan önce')),
    ):
        anchor = f'{view}-practice-{stem}-{label}-relation'
        tag = f'id="{anchor}"'
        assert report.count(tag) == 1 and f'href="#{anchor}"' in report, tag
        card = report.split(tag, 1)[1].split('</article>', 1)[0]
        for term in terms:
            assert term.casefold() in card.casefold(), (view, label, term)
print('SAADET_JANUARY_VISITS_BOTH_VIEWS_OK', folder, flush=True)
