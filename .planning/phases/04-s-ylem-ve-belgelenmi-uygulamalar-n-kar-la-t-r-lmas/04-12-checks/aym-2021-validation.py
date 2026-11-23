"""Verify the separate accounting year, decision day and publication day."""

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
harness.SOURCE = harness.DATA/'practices'/'sources'/'demokrat'
stem = '0412-demokrat-aym-2021-hesap'
package = here/'aym-2021-draft.json'
review = here/'aym-2021-review-draft.json'
assert harness.sha(package) == '15bb4a16c5cd4a9b319b05d0af87c6570856307408768a4a9b43532db6f5a2e2'
assert harness.sha(review) == '125f1850efd900cabb3a1f7eb00fbcd50a9f0bbba0a0ad330285e02caf09368f'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']),len(draft['practice_relation'])) == (13,12)
assert not draft['practice_closure']
receipt = harness.main(package, review, 'aym-2021', stem+'-event', stem+'-relation', None,
                       expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_relation','practice_candidate','practice_statement'):
        row = next(r for r in draft[table] if r['id'].startswith(stem))
        assert row in saved[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?', (stem+'-event',)).fetchone()[0] == '2024-12-25'
    assert db.execute('SELECT published_at FROM source_attribution WHERE version_id=?',
                      ('0412-aym-2021-hesap-v1',)).fetchone()[0] == '2025-03-14'
    assert not db.execute('SELECT 1 FROM practice_contribution WHERE event_id=?', (stem+'-event',)).fetchone()
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    assert all(text in card for text in ('2021','25 Aralık 2024','14 Mart 2025','oybirliğiyle','ilk gönderim günü')), view
print('DEMOKRAT_AYM_2021_DECISION_AND_PUBLICATION_BOTH_VIEWS_OK', folder, flush=True)
