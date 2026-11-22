"""Verify separate 10/856 docket, agenda decision, and date discrepancy."""

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
stem = '0411-saadet-2024-10-856'
package = here/'inquiry-856-draft.json'
review = here/'inquiry-856-review-draft.json'
assert harness.sha(package) == '1ef0fedae94d0b6a7cf4ea6fc3b3f3442bb9949031ec74ab1b5cd771c9264862'
assert harness.sha(review) == '07604cdf06ad8915318541a29ae45c80ac5ddf84141fd1379a887fc0f72bdc7f'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 8 and len(draft['practice_relation']) == 6
assert not draft['practice_closure']
receipt = harness.main(package, review, 'inquiry-856', stem+'-event', stem+'-relation', None,
                       expected_party='saadet', namespace='gsd-0411')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_dispute', 'practice_contribution'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    version = db.execute('SELECT original_path FROM document_version WHERE id=?',
                         ('0411-inquiry-pension-2024-session-v1',)).fetchone()[0]
    assert (harness.SOURCE/version).read_bytes() == (harness.DATA/'practices'/'sources'/'iyi'/version).read_bytes()
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    assert all(word in card for word in ('10/856','Gündemde','16.01.2023','16 Ocak 2024','gündeme alma önerisi'))
assert page.count(f'data-finding-id="{stem}-source-date-finding"') == 2
print('SAADET_856_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
