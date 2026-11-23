"""Verify the grain-price agenda and dated TMO payment reports in both views."""

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
case = 'hububat'
stem = '0411-hububat-2026'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == '7562311c3900a059cdb70ca42a9283ff63acdde72059672db17824747625bc97'
assert harness.sha(review) == 'fc30cbd8d1121c7137b62a28b2cc9de1dbbc761ec1601e7498d801bb334a3b7c'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (23, 19, 0)
labels = ('agenda', 'payment', 'july', 'august')
receipt = harness.main(package, review, case, stem + '-agenda-event', stem + '-agenda-relation',
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
    assert [row[0] for row in dates] == ['2026-06-10', '2026-06-25', '2026-07-27', '2026-08-17']
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    for label, terms in (
        ('agenda', ('10/4251', 'Şerafettin Kılıç', 'gündem talebinin kabul edilmediğini', 'Gündemde')),
        ('payment', ('45 gün', '21’inci günden itibaren', '16.500', '12.750', 'ilk ödemelerin')),
        ('july', ('176 bin üretici', '8,3 milyon ton', '34,3 milyar TL')),
        ('august', ('11,5 milyon ton', '120 milyar TL', 'kümülatif')),
    ):
        anchor = f'{view}-practice-{stem}-{label}-relation'
        tag = f'id="{anchor}"'
        assert report.count(tag) == 1 and f'href="#{anchor}"' in report, tag
        card = report.split(tag, 1)[1].split('</article>', 1)[0]
        for term in terms:
            assert term.casefold() in card.casefold(), (view, label, term)
print('SAADET_HUBUBAT_BOTH_VIEWS_OK', folder, flush=True)
