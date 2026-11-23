"""Verify the 10/4826 motion, three agenda votes and attribution."""

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
stem = '0408-yeni-yol-2026-4826'
package = here/'fund-4826-draft.json'
review = here/'fund-4826-review-draft.json'
assert harness.sha(package) == '36d6fe365920fccb8925f8e38e4be96160cb803891148ba61bb28754f9b24119'
assert harness.sha(review) == '12ef132f5b60f9320152f8b69bb36347f00133a416ec0debcf48535221c75ee8'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (12, 8)
assert not draft['practice_closure']
receipt = harness.main(package, review, 'fund-4826', stem+'-event', stem+'-relation', None,
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
    assert [status['0408-fund-4826-floor-'+key] for key in ('first','second','decision')] == ['action','action','result']
    keys = dict(db.execute('SELECT id,common_event_key FROM practice_event WHERE id IN (?,?)',
        (stem+'-event','0408-yeni-yol-2026-4343-event')))
    assert keys == {stem+'-event':'tbmm-28-5-009-10-4826-gundem',
                    '0408-yeni-yol-2026-4343-event':'tbmm-28-4-108-10-4343-gundem'}
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    for expected in ('10/4826','21 Ekim','karar yeter sayısı','Üçüncü oturum','Gündemde','Atmaca'):
        assert expected in card, (view, expected)
print('YENI_YOL_FUND_4826_VOTE_ORDER_BOTH_VIEWS_OK', folder, flush=True)
