"""Verify the Batman provincial election and its charter connection."""

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
stem = '0409-dbp-batman-2026-2-olagan'
package = here/'batman-congress-draft.json'
review = here/'batman-congress-review-draft.json'
assert harness.sha(package) == 'e2ed6dc4d020a934c7fec20710539c2c6dccc46b052382937caa729ec65d8f8a'
assert harness.sha(review) == '1d7d664c5246e42811e86b465016e189ad02eb3e4990aa86a2d0c9e6c82f0e08'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 8 and len(draft['practice_relation']) == 5
assert not draft['practice_closure']
receipt = harness.main(package, review, 'batman-congress', stem+'-event', stem+'-relation', None,
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
    event = db.execute('SELECT event_at,date_precision FROM practice_event WHERE id=?', (stem+'-event',)).fetchone()
    assert tuple(event) == (None,'unknown')
    phases = db.execute('SELECT stage,COUNT(*) FROM practice_event_evidence WHERE event_id=? GROUP BY stage',
                       (stem+'-event',))
    assert dict(phases) == {'initiative':1, 'action':1, 'result':3}
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    assert all(text in card for text in ('Celile Yıldız','Rıdvan Erzik','19 Eylül','il kongresi'))
print('DBP_BATMAN_CONGRESS_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
