"""Verify the pension floor statement, amendment, and adopted law."""

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
harness.SOURCE = harness.DATA/'practices'/'sources'/'iyi'
stem = '0407-iyi-2026-7573'
package = here/'pension-floor-final-draft.json'
review = here/'pension-floor-final-review-draft.json'
assert harness.sha(package) == '12f81c972dcc768ea6d6c61c77b50369b6b879bcb924ac74c2484b533770031f'
assert harness.sha(review) == 'aca52ae985bcaefea0c09f923ef48253df4c2657753d081f950fde553383ebea'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 6 and len(draft['practice_relation']) == 6
assert not draft['practice_closure']
receipt = harness.main(package, review, 'pension-floor-final', stem+'-event', stem+'-relation', None,
                       expected_party='iyi', namespace='gsd-0407')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_statement', 'practice_dispute'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    event = db.execute('SELECT event_at, common_event_key FROM practice_event WHERE id=?',
                       (stem+'-event',)).fetchone()
    assert tuple(event) == ('2026-01-23', 'tbmm-28-4-050-2-3464-7573')
    result = db.execute('SELECT result_finding_id FROM practice_relation WHERE id=?',
                        (stem+'-relation',)).fetchone()
    assert result[0] == stem+'-result'
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    assert all(word in card for word in
               ('7573','25.000 TL','20.000 TL','247 kabul ve 179 ret','245 kabul, 179 ret ve 2 mükerrer','asgari ücret','Fakıbaba'))
print('IYI_7573_FINAL_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
