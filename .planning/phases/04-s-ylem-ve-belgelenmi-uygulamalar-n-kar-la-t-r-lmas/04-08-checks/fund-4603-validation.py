"""Verify the 10/4603 motion, separate 8 October agenda vote and attribution."""

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
harness.SOURCE = harness.DATA/'practices'/'sources'/'yeni-yol'
stem = '0408-yeni-yol-2026-4603'
package = here/'fund-4603-draft.json'
review = here/'fund-4603-review-draft.json'
assert harness.sha(package) == 'b10a8838438a5d5621de11cf5ea3ec69c493def9a7b2363756daacea42eda147'
assert harness.sha(review) == '83251a96d527273d84a91dedd234103526cbd6ceea71d5e9d52ac0b0b53e4fa9'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (13, 9)
assert not draft['practice_closure']
receipt = harness.main(package, review, 'fund-4603', stem+'-event', stem+'-relation', None,
                       expected_party='yeni-yol', namespace='gsd-0408')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_relation','practice_candidate','practice_contribution'):
        row = next(r for r in draft[table] if r['id'].startswith(stem))
        assert row in saved[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    status = {r['passage_id']:r['stage'] for r in db.execute(
        'SELECT passage_id,stage FROM practice_event_evidence WHERE event_id=?', (stem+'-event',))}
    assert status['0408-fund-4603-floor-agenda']=='action'
    assert status['0408-fund-4603-floor-decision']=='result'
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?',(stem+'-event',)).fetchone()[0]=='2026-10-08'
    keys = dict(db.execute('SELECT id,common_event_key FROM practice_event WHERE id IN (?,?)',
        (stem+'-event','0408-yeni-yol-2026-4343-event')))
    assert keys == {stem+'-event':'tbmm-28-5-004-10-4603-gundem',
                    '0408-yeni-yol-2026-4343-event':'tbmm-28-4-108-10-4343-gundem'}
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    for expected in ('10/4603','6 Ekim','8 Ekim','ön görüşme','Gündemde','Kısacık'):
        assert expected in card, (view, expected)
print('YENI_YOL_FUND_4603_AGENDA_BOTH_VIEWS_OK', folder, flush=True)
