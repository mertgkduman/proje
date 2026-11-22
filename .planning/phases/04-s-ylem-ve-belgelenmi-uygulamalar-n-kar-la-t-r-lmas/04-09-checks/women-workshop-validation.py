"""Verify the dated conference policy and reports on the Edremit workshop."""

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
stem = '0409-dbp-van-women-workshop-2025'
package = here/'women-workshop-draft.json'
review = here/'women-workshop-review-draft.json'
assert harness.sha(package) == '8626a8779cbb70ff020c0eec2b8076f970897ff442b57f3f28efc4a47b4d9342'
assert harness.sha(review) == '7867e4da4d78b0a8a04959e7a4f7b2b8f15fb9ac7151bf316025bfb27c477693'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 9 and len(draft['practice_relation']) == 6
assert not draft['practice_closure']
receipt = harness.main(package, review, 'women-workshop', stem+'-event', stem+'-relation', None,
                       expected_party='dbp', namespace='gsd-0409')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_statement'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    row = db.execute('SELECT event_at,date_precision FROM practice_event WHERE id=?',(stem+'-event',)).fetchone()
    assert tuple(row) == (None,'unknown')
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    assert all(word in card for word in ('Van Edremit','Berivan Bahçeci','13 Ağustos 2025','kadın akademileri'))
print('DBP_WOMEN_WORKSHOP_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
