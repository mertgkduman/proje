"""Verify the dated Bulu demand, recorded outcome and retained dispute."""

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
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'emep'
case = 'bulu-2021-v4'
package = checks / 'bulu-2021-v4-union-draft.json'
review = checks / 'bulu-2021-v4-union-review-draft.json'
assert harness.sha(package) == 'db65dc73f93ef31ff466da7c2ca930411c0eb462655ed93ed02c08c1a12cfba6'
assert harness.sha(review) == 'c83f5ac8e91df54b977e87ad9e140b5b6ea97a453b363accc89c7746409a3db1'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']),
        len(records['practice_closure'])) == (69, 71, 0)
event = '0410-bulu-dismissal-2021-event'
candidate = '0410-bulu-2021-candidate'
relation = '0410-bulu-2021-relation'
statement = '0410-bulu-2021-demand-statement'
dispute = '0410-bulu-2021-conflict'
receipt = harness.main(package, review, case, event, relation,
                       None, expected_party='emep', namespace='gsd-0410')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identity in (
        ('practice_event', event), ('practice_candidate', candidate),
        ('practice_dispute', dispute), ('practice_relation', relation),
        ('practice_statement', statement),
    ):
        row = next(row for row in records[table] if row['id'] == identity)
        assert row in export[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
    assert tuple(db.execute('SELECT state,relation_id FROM practice_candidate WHERE id=?',
                            (candidate,)).fetchone()) == ('eligible', relation)
    assert db.execute('SELECT statement_at FROM practice_statement WHERE id=?', (statement,)).fetchone()[0] == '2021-02-03'
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?', (event,)).fetchone()[0] == '2021-07-14'
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{relation}'
    start = f'id="{anchor}"'
    assert report.count(start) == 1 and f'href="#{anchor}"' in report
    card = report.split(start, 1)[1].split('</article>', 1)[0]
    for phrase in ('görevden al', 'istifa', 'seçim'):
        assert phrase.casefold() in card.casefold(), (view, phrase)
print('EMEP_BULU_V4_BOTH_VIEWS_OK', folder, flush=True)
