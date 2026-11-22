"""Verify the dated pension eligibility proposal and its open result."""

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
stem = '0411-saadet-2024-2-1998'
package = here/'pension-age-draft.json'
review = here/'pension-age-review-draft.json'
assert harness.sha(package) == '96f6d46c9a3e44a1c64fbb210afa5af58fcf64d5dbc1eb900a03e816cc356e6b'
assert harness.sha(review) == '2bd19e5b067797a0cf2b787534950dcf76ae4e26aeed974ad3b6fbfd2bbc4d6b'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 7 and len(draft['practice_relation']) == 5
assert not draft['practice_closure']
receipt = harness.main(package, review, 'pension-age', stem+'-event', stem+'-relation', None,
                       expected_party='saadet', namespace='gsd-0411')
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
    assert db.execute('SELECT result_finding_id FROM practice_relation WHERE id=?',
                      (stem+'-relation',)).fetchone()[0] is None
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    assert all(word in card for word in ('2/1998','prim günü','9.000','Komisyonda'))
print('SAADET_AGE_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
