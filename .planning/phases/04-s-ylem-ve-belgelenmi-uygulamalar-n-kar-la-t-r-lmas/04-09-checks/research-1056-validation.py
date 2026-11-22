"""Check the 10/1056 proposal and its earlier documented statement."""

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
stem = '0409-dbp-2024-10-1056'
package = here/'research-1056-draft.json'
review = here/'research-1056-review-draft.json'
assert harness.sha(package) == '8b1f94c034f0eca3ceefbe35a8872ef676134b80a28be637024caef373e1b05d'
assert harness.sha(review) == '94a2c6242b80f6e30f4efc33e1948d95e4de6727f70292819bc7bb983abaab9f'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 6 and len(draft['practice_relation']) == 4
assert not draft['practice_closure']
receipt = harness.main(package, review, 'research-1056', stem+'-event', stem+'-relation', None,
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
    assert not db.execute(
        "SELECT 1 FROM practice_event_evidence WHERE event_id=? AND stage='result'", (stem+'-event',)).fetchone()
    assert db.execute('SELECT result_finding_id FROM practice_relation WHERE id=?', (stem+'-relation',)).fetchone()[0] is None
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    assert all(term in card for term in ('10/1056', 'Gündemde', 'DBP de tecridin kırılması için ısrarlıdır.'))
print('DBP_1056_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
