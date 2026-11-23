"""Verify one unmatched internet proposal and its two reader views."""

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
scope = 'internet-4012'
stem = '0412-demokrat-2026-2-4012'
event = stem+'-event'
candidate = stem+'-unmatched'
package = here/f'{scope}-draft.json'
review = here/f'{scope}-review-draft.json'
assert harness.sha(package) == '465657f17288833b00f17f0bdeb7e569d24b83a35a74fd0f4372718b64550cfd'
assert harness.sha(review) == '62d9d411cbb0de6e94de96044eb1e4bb445291e3fe6714fc8c67b20375728aef'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']),len(draft['practice_relation'])) == (18,16)
assert not draft['practice_closure']
receipt = harness.main(package,review,scope,event,'0412-demokrat-2026-2-4007-relation',
                       None,expected_party='demokrat',namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table,row_id in [('practice_event',event),('practice_candidate',candidate)]:
        row = next(r for r in draft[table] if r['id']==row_id)
        assert row in saved[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row_id,)).fetchone())
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?',(event,)).fetchone()[0] == '2026-11-03'
    assert db.execute('SELECT state FROM practice_candidate WHERE id=?',(candidate,)).fetchone()[0] == 'unmatched'
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(event,)).fetchone()
    assert {r[0] for r in db.execute('SELECT stage FROM practice_event_evidence WHERE event_id=?',(event,))} == {'initiative','action'}
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-unmatched-{candidate}'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    for expected in ('2/4012','Altıntaş','2 Kasım','3 Kasım','5 Kasım','bant daraltma','Komisyonda'):
        assert expected in card,(view,expected)
print('DP_4012_PROPOSAL_BOTH_VIEWS_OK',folder,flush=True)
