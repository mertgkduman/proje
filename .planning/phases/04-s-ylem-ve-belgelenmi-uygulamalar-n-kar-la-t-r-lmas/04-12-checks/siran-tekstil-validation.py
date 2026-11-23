"""Verify the published local goal and the reported Tekstilkent site visit."""

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
stem = '0412-demokrat-siran-tekstilkent'
package = here/'siran-tekstil-draft.json'
review = here/'siran-tekstil-review-draft.json'
assert harness.sha(package) == '80787f0178cdac4bf5c6f91af33c323f7897ad4e393c886fb2a24a24750d4f13'
assert harness.sha(review) == 'dddef62ae47a4cb9b84d9ba0bd90f13727e05da4d15a8643bb064793e0ff7dbe'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 12 and len(draft['practice_relation']) == 11
assert not draft['practice_closure']
receipt = harness.main(package, review, 'siran-tekstil', stem+'-event',stem+'-relation', None,
                       expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_text())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_statement'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?', (stem+'-event',)).fetchone()[0]=='2024-05-18'
    assert db.execute('SELECT statement_at FROM practice_statement WHERE id=?', (stem+'-statement',)).fetchone()[0]=='2024-02-29'
    assert db.execute('SELECT result_finding_id FROM practice_relation WHERE id=?', (stem+'-relation',)).fetchone()[0] is None
    assert {row[0] for row in db.execute('SELECT stage FROM practice_event_evidence WHERE event_id=?',
                                        (stem+'-event',))} == {'action'}
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    assert all(word in card for word in ('Tekstilkent','120','500','yatırımcılarla','saha incelemesi'))
print('DP_SIRAN_TEKSTIL_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
