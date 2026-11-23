"""Verify both stages of the tax deferral comparison in an isolated report."""

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
case = 'tax-deferral'
stem = '0412-tax-deferral-2026'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == 'a867606f16ddf3fabf19146bc7c42e0b6dd69adb515c88cd7245d42cabc46dae'
assert harness.sha(review) == 'b940d12643fbeb31d705c96aace5bb00b2d95ea8699be62fd113513fe54f8b54'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (20, 18, 0)
law, teblig = stem + '-law', stem + '-teblig'
receipt = harness.main(package, review, case, law + '-event', law + '-relation',
                       None, expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identities in (
        ('practice_statement', (stem + '-statement',)),
        ('practice_event', (law + '-event', teblig + '-event')),
        ('practice_relation', (law + '-relation', teblig + '-relation')),
    ):
        for identity in identities:
            row = next(row for row in records[table] if row['id'] == identity)
            assert row in export[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
    assert {row[0] for row in db.execute('SELECT id FROM practice_relation WHERE statement_id=?',
                                        (stem + '-statement',))} == {law + '-relation', teblig + '-relation'}
    dates = db.execute('SELECT event_at FROM practice_event WHERE id IN (?,?) ORDER BY event_at',
                       (law + '-event', teblig + '-event')).fetchall()
    assert [row[0] for row in dates] == ['2026-05-21', '2026-06-16']
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    for identity, terms in (
        (law, ('36 aydan 72 aya', '50.000 TL', '1 milyon TL', '4 Haziran')),
        (teblig, ('yüzde 39 yerine yüzde 29', '31 Ağustos', 'Özel tüketim vergisi', 'yüzde 44’e yakın maliyet')),
    ):
        anchor = f'{view}-practice-{identity}-relation'
        tag = f'id="{anchor}"'
        assert report.count(tag) == 1 and f'href="#{anchor}"' in report, tag
        card = report.split(tag, 1)[1].split('</article>', 1)[0]
        for term in terms:
            assert term.casefold() in card.casefold(), (view, identity, term)
print('DEMOKRAT_TAX_DEFERRAL_BOTH_VIEWS_OK', folder, flush=True)
