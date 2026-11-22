"""Verify the DBP fifth extraordinary congress in both report views."""

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
stem = '0409-dbp-2023-5-olaganustu'
package = here/'congress-june-draft.json'
review = here/'congress-june-review-draft.json'
assert harness.sha(package) == 'cab0684c245f4af7c0785f38ce7da48c555fb53416764d25a45ffeceab846d04'
assert harness.sha(review) == '058d65fd5db9821c9790962abdf3e1725caa4bd27639f3b9d97e74afbeb5b5e4'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 7 and len(draft['practice_relation']) == 4
assert not draft['practice_closure']
receipt = harness.main(package, review, 'congress-june', stem+'-event',
                       '0409-dbp-2024-10-1056-relation', None, expected_party='dbp', namespace='gsd-0409')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?', (stem+'-event',)).fetchone()
    assert db.execute(
        "SELECT COUNT(*) FROM practice_event_evidence WHERE event_id=? AND stage='result'", (stem+'-event',)
    ).fetchone()[0] == 2
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-unmatched-{stem}-candidate'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    assert all(text in card for text in ('Saliha Aydeniz', 'Keskin Bayındır', 'Haziran', 'Araştırma sürüyor'))
print('DBP_JUNE_CONGRESS_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
