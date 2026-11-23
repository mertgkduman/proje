"""Verify the July pension floor and wage comparison in both report views."""

from decimal import Decimal
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
case = 'july-pension-floor'
draft_path = checks / f'{case}-draft.json'
review_path = checks / f'{case}-review-draft.json'
assert harness.sha(draft_path) == '6c86dc9eaaae1bf80e354cfff7f0785d568daaaf80c4351e47af6d7675c9af4f'
assert harness.sha(review_path) == '4065d612309da3353238f300fc3df51ad7410386eac9c5e90d736cd9f9d81864'
records = json.loads(draft_path.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (19, 15, 0)
stem = '0411-saadet-2026-7590-m16'
eid, rid = stem + '-event', stem + '-relation'
receipt = harness.main(draft_path, review_path, case, eid, rid, None,
                       expected_party='saadet', namespace='gsd-0411')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identity in (
        ('practice_event', eid),
        ('practice_statement', stem + '-statement'),
        ('practice_relation', rid),
        ('practice_candidate', stem + '-candidate'),
    ):
        row = next(row for row in records[table] if row['id'] == identity)
        assert row in export[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?', (eid,)).fetchone()[0] == '2026-07-24'
    assert db.execute('SELECT statement_at FROM practice_statement WHERE id=?', (stem + '-statement',)).fetchone()[0] == '2026-07-01'
    for identity, expected in (
        ('0411-july-pension-law-text-amend', '23.552'),
        ('0411-july-pension-law-text-effect', 'Temmuz ayı ödeme döneminden'),
        ('0411-july-pension-wage-announcement-net', '28 bin 75 lira 50 kuruş'),
    ):
        assert expected in db.execute('SELECT exact FROM passage WHERE id=?', (identity,)).fetchone()[0]
assert Decimal('28075.50') - Decimal('23552') == Decimal('4523.50')
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{rid}'
    tag = f'id="{anchor}"'
    assert report.count(tag) == 1 and f'href="#{anchor}"' in report, tag
    card = report.split(tag, 1)[1].split('</article>', 1)[0]
    for term in ('23.552 TL', '28.075,50 TL', '4.523,50 TL', '31 Temmuz'):
        assert term in card, (view, term)
print('SAADET_JULY_PENSION_FLOOR_BOTH_VIEWS_OK', folder, flush=True)
