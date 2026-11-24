"""Check both independent Roboski decisions in SQLite, JSON and both HTML views."""

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
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'emep'
case = 'encu-decisions'
base = f'0410-{case}'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']),
        len(records['practice_closure'])) == (75, 72, 0)
receipt = harness.main(package, review, case, f'{base}-aym-event', '0410-tezkere-1310-relation', None,
                       expected_party='emep', namespace='gsd-0410')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
report = (folder / 'index.html').read_text()
cases = {
    'aym': ('2016-02-24', ('2014/11864', '24 Şubat 2016', '23 Mart 2016')),
    'echr': ('2018-04-10', ('49976/16', '10 Nisan 2018', '17 Mayıs 2018')),
}
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for court, (day, phrases) in cases.items():
        event = f'{base}-{court}-event'
        candidate = f'{base}-{court}-unmatched'
        for table, ident in (('practice_event', event), ('practice_candidate', candidate)):
            expected = next(row for row in records[table] if row['id'] == ident)
            actual = db.execute(f'SELECT * FROM {table} WHERE id=?', (ident,)).fetchone()
            assert expected in export[table] and expected == dict(actual), ident
        assert db.execute('SELECT event_at FROM practice_event WHERE id=?', (event,)).fetchone()[0] == day
        assert tuple(db.execute('SELECT state, relation_id FROM practice_candidate WHERE id=?',
                                (candidate,)).fetchone()) == ('unmatched', None)
        for view in ('party', 'comparison'):
            anchor = f'{view}-unmatched-{candidate}'
            start = f'id="{anchor}"'
            assert report.count(start) == 1 and f'href="#{anchor}"' in report
            card = report.split(start, 1)[1].split('</article>', 1)[0]
            for phrase in phrases:
                assert phrase in card, (view, court, phrase)
print('EMEP_ENCU_DECISIONS_BOTH_VIEWS_OK', folder, flush=True)
