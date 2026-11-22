"""Verify the distinct İYİ group contribution to the 10/3998 agenda debate."""

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
stem = '0407-iyi-2026-10-3998'
package = here/'tuik-3998-group-draft.json'
review = here/'tuik-3998-group-review-draft.json'
assert harness.sha(package) == 'fa26528da70095da44c9f622a6794941f1b3da74348d0d35c0ad7bb907d88d7a'
assert harness.sha(review) == 'd54c4d7cc7772db48d3cef620c7e39806bc7a293e40536c078dfb0a6d819a0a9'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 7 and len(draft['practice_relation']) == 6
assert not draft['practice_closure']
receipt = harness.main(package, review, 'tuik-3998-group', stem+'-event',
                       '0407-iyi-2026-7573-relation', None, expected_party='iyi', namespace='gsd-0407')
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
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?', (stem+'-event',)).fetchone()
    assert db.execute('SELECT common_event_key FROM practice_event WHERE id=?',
                      (stem+'-event',)).fetchone()[0] == 'tbmm-28-4-079-10-3998-gundem'
    for row in db.execute("SELECT original_path,readable_path FROM document_version WHERE id LIKE '0407-tuik-3998%'"):
        for path in row:
            assert (harness.SOURCE/path).read_bytes() == (harness.DATA/'practices'/'sources'/'yeni-yol'/path).read_bytes()
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-unmatched-{stem}-candidate'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    assert all(word in card for word in ('10/3998','Burak Dalgın','akademik','kabul etmedi','Araştırma sürüyor'))
assert page.count(f'data-finding-id="{stem}-dalgin-finding"') == 2
print('IYI_TUIK_3998_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
