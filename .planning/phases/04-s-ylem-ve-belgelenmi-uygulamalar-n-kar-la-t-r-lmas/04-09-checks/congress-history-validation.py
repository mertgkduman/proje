"""Check the two earlier DBP elections and the reported venue conflict."""

import importlib.util
import json
import os
from pathlib import Path
import sqlite3

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', here.parent/'04-04-checks'/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = here
harness.ROOT = Path(os.environ['GSD04_RENDERER_CHECKOUT'])
harness.DATA = harness.ROOT/'data'
harness.INVENTORY = harness.DATA/'practices'/'04-inventory.json'
harness.SOURCE = harness.DATA/'practices'/'sources'/'dbp'
package = here/'congress-history-draft.json'
review = here/'congress-history-review-draft.json'
assert harness.sha(package) == '0f9624bb191c10b0c2fd5279d5b9e150380bf4c0d06fc2b99260906be3873adb'
assert harness.sha(review) == 'ba358098b52c0a3f9c298d4d0180c33232195f5b4c3ac6363c366377a62dbb8d'
early_stems = ('0409-dbp-2022-6-olagan','0409-dbp-2023-6-olaganustu')
dispute = '0409-dbp-2023-election-venue-finding'
receipt = harness.main(package, review, 'congress-history', early_stems[1]+'-event',
                       '0409-dbp-2025-7-olagan-relation', None, expected_party='dbp', namespace='gsd-0409')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 4 and len(draft['practice_relation']) == 2
assert not draft['practice_closure']
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_relation','practice_candidate','practice_dispute'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    for stem in early_stems:
        assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(stem+'-event',)).fetchone()
page = (folder/'index.html').read_text()
for stem in early_stems:
    for view in ('party','comparison'):
        anchor = f'{view}-unmatched-{stem}-candidate'
        tag = f'id="{anchor}"'
        assert page.count(tag) == 1 and f'href="#{anchor}"' in page
        card = page.split(tag,1)[1].split('</article>',1)[0]
        assert 'Araştırma sürüyor' in card
        if stem == early_stems[1]:
            assert 'Ankara' in card and 'Diyarbakır' in card
assert page.count(f'data-finding-id="{dispute}"') == 2
print('DBP_HISTORY_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
