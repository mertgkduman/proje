"""Verify the 10/437 filing, agenda decision, and attributed statements."""

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
stem = '0407-iyi-2024-10-437-gundem'
package = here/'aged-draft.json'
review = here/'aged-review-draft.json'
assert harness.sha(package) == '75bba80fbf84351137804af840280625925f2b3a2d78788a36c16139d08b2755'
assert harness.sha(review) == 'e3a2d750b600e38f1f8baee02dc2c5f29fe71f64f77aa0fa832cba5f669c0d6e'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 5 and len(draft['practice_relation']) == 5
assert not draft['practice_closure']
receipt = harness.main(package, review, 'aged', stem+'-event', stem+'-relation', None,
                       expected_party='iyi', namespace='gsd-0407')
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
    results = db.execute(
        "SELECT passage_id FROM practice_event_evidence WHERE event_id=? AND stage='result'", (stem+'-event',)
    ).fetchall()
    assert [row[0] for row in results] == ['0407-aged-pension-2024-summary-result']
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    assert all(word in card for word in ('10/437','Gündemde','gündeme alma önerisi kabul edilmedi','huzurevleri'))
assert page.count(f'data-finding-id="{stem}-sunat-finding"') == 2
print('IYI_437_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
