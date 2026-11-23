"""Check the Diyarbakır bus introduction evidence and unmatched presentation."""

import importlib.util
import json
from pathlib import Path
import sqlite3

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', here.parent/'04-04-checks'/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = here
harness.SOURCE = harness.DATA/'practices'/'sources'/'dbp'
stem = '0409-diyarbakir-2015-cng'
event = stem+'-event'
candidate = stem+'-unmatched'
package = here/'diyarbakir-cng-draft.json'
review = here/'diyarbakir-cng-review-draft.json'
assert harness.sha(package) == '7cfc0109c27d6bdb6a94d74582e0d0f1a2e0ce8098df8be4ffa3fa12b7274fcb'
assert harness.sha(review) == '2a24fadb43a67494ad8cee89675f1fb05c54c7b4e994b71e24e6f2d3667bec90'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 11 and len(draft['practice_relation']) == 7
assert not draft['practice_closure']
receipt = harness.main(package, review, 'diyarbakir-cng', event,
                       '0409-dbp-baglar-2015-cemr-relation', None,
                       expected_party='dbp', namespace='gsd-0409')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_text())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_contribution'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?', (event,)).fetchone()[0] == '2015-05-27'
    assert db.execute('SELECT state FROM practice_candidate WHERE id=?', (candidate,)).fetchone()[0] == 'unmatched'
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?', (event,)).fetchone()
    assert {row[0] for row in db.execute('SELECT stage FROM practice_event_evidence WHERE event_id=?', (event,))} == {'action'}
    assert db.execute('SELECT contribution_kind FROM practice_contribution WHERE id=?',
                      (stem+'-contribution',)).fetchone()[0] == 'support'
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-unmatched-{candidate}'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    assert all(text in card for text in ('Henüz incelenmedi', '22', 'ertesi gün', 'Ali Şimşek', 'belediyeye teşekkür etti'))
print('DBP_CNG_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
