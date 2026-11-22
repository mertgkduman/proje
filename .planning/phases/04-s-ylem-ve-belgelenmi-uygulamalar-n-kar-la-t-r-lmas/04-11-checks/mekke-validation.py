"""Check the preserved Saadet statement and named parliamentary vote."""

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
harness.SOURCE = harness.DATA/'practices'/'sources'/'saadet'
stem = '0411-saadet-2026-mekke'
package = here/'mekke-draft.json'
review = here/'mekke-review-draft.json'
assert harness.sha(package) == '3045d251531ee8aacec79838b14e7a9834b9cc5ad50479396c26564a231f1bce'
assert harness.sha(review) == 'fab142c2a981831ff9048030799736fa5c5da588db5d1efff66aff9939ac11d2'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 4 and len(draft['practice_relation']) == 3
assert not draft['practice_closure']
receipt = harness.main(package, review, 'mekke', stem+'-event', stem+'-relation', None,
                       expected_party='saadet', namespace='gsd-0411')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_contribution'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    event = db.execute('SELECT event_at, common_event_key FROM practice_event WHERE id=?', (stem+'-event',)).fetchone()
    assert tuple(event) == ('2026-11-05', 'tbmm-28-5-014-2-3961-mekke-7597')
    assert db.execute('SELECT kind FROM actor WHERE id=?', (stem+'-arikan-mp',)).fetchone()[0] == 'individual_mp'
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    assert all(term in card for term in ('277 kabul', '118 ret', '23.49.39', 'bireysel', 'kabul etmeyeceğimizi'))
    assert f'data-finding-id="{stem}-individual-ret"' in card
print('SAADET_MEKKE_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
