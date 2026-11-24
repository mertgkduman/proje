"""Verify the corrected Bulu case with the current production path."""

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
case = 'bulu-2021-current'
package = checks / 'bulu-2021-v3-union-draft.json'
review = checks / 'bulu-2021-v3-union-review-draft.json'
assert harness.sha(package) == 'd4dd95588e70772429ee8f4690442d1e3fee0c7fee039467dad734b5b1e078cc'
assert harness.sha(review) == '9ce12d304582ded05ebcd6359032ccc0c3ea0a2c46d7b42cb26126b106c2b83e'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']),
        len(records['practice_closure'])) == (69, 70, 0)
event = '0410-bulu-dismissal-2021-event'
candidate = '0410-bulu-2021-unmatched'
dispute = '0410-bulu-2021-conflict'
receipt = harness.main(package, review, case, event, '0410-youth9-conference-relation',
                       None, expected_party='emep', namespace='gsd-0410')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identity in (('practice_event', event), ('practice_candidate', candidate), ('practice_dispute', dispute)):
        row = next(row for row in records[table] if row['id'] == identity)
        assert row in export[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
    assert tuple(db.execute('SELECT state,relation_id FROM practice_candidate WHERE id=?',
                            (candidate,)).fetchone()) == ('unmatched', None)
    assert '0410-emep-bogazici-20210519-p' in db.execute(
        'SELECT passage_ids FROM practice_candidate WHERE id=?', (candidate,)).fetchone()[0]
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-unmatched-{candidate}'
    start = f'id="{anchor}"'
    assert report.count(start) == 1 and f'href="#{anchor}"' in report
    card = report.split(start, 1)[1].split('</article>', 1)[0]
    for phrase in ('görevden alınması', 'istifa', 'özerk demokratik üniversite'):
        assert phrase.casefold() in card.casefold(), (view, phrase)
print('EMEP_BULU_CURRENT_BOTH_VIEWS_OK', folder, flush=True)
