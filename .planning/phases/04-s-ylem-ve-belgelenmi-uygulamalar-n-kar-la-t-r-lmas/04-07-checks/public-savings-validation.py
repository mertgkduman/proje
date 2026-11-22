"""Verify the selected savings records against the pinned work renderer."""

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
harness.SOURCE = harness.DATA/'practices'/'sources'/'iyi'
package = here/'public-savings-draft.json'
review = here/'public-savings-review-draft.json'
assert harness.sha(package) == '84e4ba9141390fdf81c39db3965855c56810fda1fb5472dfc8931b80b924fdc3'
assert harness.sha(review) == 'f6757a116cc082ce026561698d2a2c4f3fbc84a2aa857681f992837ca0f0dd07'
stem = '0407-iyi-2025-10-3466-tasarruf'
receipt = harness.main(package, review, 'public-savings-v31', stem+'-event', stem+'-relation', None,
                       expected_party='iyi', namespace='gsd-0407')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
draft = json.loads(package.read_bytes())['practice_records']
saved = json.loads((folder/'records.json').read_bytes())
assert len(draft['practice_event']) == len(draft['practice_relation']) == 4 and not draft['practice_closure']
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_relation','practice_statement'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
page = (folder/'index.html').read_text()
for row in draft['practice_relation']:
    for view in ('party','comparison'):
        anchor = f'{view}-practice-{row["id"]}'
        assert page.count(f'id="{anchor}"')==1 and f'href="#{anchor}"' in page
for view in ('party','comparison'):
    card = page.split(f'id="{view}-practice-0407-iyi-2026-7-49651-tasarruf-relation"',1)[1].split('</article>',1)[0]
    assert '484 milyar TL' in card and '2024–2025' in card
print('IYI_SAVINGS_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
