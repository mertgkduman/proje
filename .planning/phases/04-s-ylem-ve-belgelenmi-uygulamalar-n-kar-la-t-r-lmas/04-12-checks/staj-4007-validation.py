"""Verify the proposal, commission referral, and open legislative outcome."""

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
stem = '0412-demokrat-2026-2-4007'
package = here/'staj-4007-draft.json'
review = here/'staj-4007-review-draft.json'
assert harness.sha(package) == '7ca11e8745d829d251c415f79f9ab918b8ada7ad491ec1fd4a66648563f84871'
assert harness.sha(review) == '4cf9a5d80abe0c2dc205d2590224bee2b94606cb4aa9bc035e3ec1c30e033258'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 17 and len(draft['practice_relation']) == 16
assert not draft['practice_closure']
receipt = harness.main(package, review, 'staj-4007', stem+'-event',stem+'-relation', None,
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
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?', (stem+'-event',)).fetchone()[0]=='2026-11-03'
    assert db.execute('SELECT statement_at FROM practice_statement WHERE id=?', (stem+'-statement',)).fetchone()[0] is None
    assert db.execute('SELECT result_finding_id FROM practice_relation WHERE id=?', (stem+'-relation',)).fetchone()[0] is None
    assert {row[0] for row in db.execute('SELECT stage FROM practice_event_evidence WHERE event_id=?',
                                        (stem+'-event',))} == {'initiative','action'}
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    assert all(word in card for word in ('2/4007','2 Kasım','3 Kasım','4 Kasım','borçlanma','Komisyonda','Altıntaş'))
print('DP_4007_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
