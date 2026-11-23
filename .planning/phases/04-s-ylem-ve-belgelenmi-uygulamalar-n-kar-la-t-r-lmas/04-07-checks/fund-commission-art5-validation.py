"""Verify the distinct written and spoken scopes of the Article 5 motion."""

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
scope = 'fund-commission-art5'
stem = '0407-iyi-2026-commission-art5'
event = stem+'-event'
candidate = stem+'-unmatched'
package = here/f'{scope}-draft.json'
review = here/f'{scope}-review-draft.json'
assert harness.sha(package) == '8cfe91727b157c6f74bbbeebfd7409cb422eac72565171a87610d0be97f21189'
assert harness.sha(review) == '18d966415b2b7a353b1eff72b7d03bf7eea4d93b448e9b825b62dc6a74adb0ed'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (12, 9)
assert not draft['practice_closure']
receipt = harness.main(package, review, scope, event,'0407-iyi-2026-commission-art4-relation',
                       None, expected_party='iyi', namespace='gsd-0407')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_candidate'):
        row = next(r for r in draft[table] if r['id'].startswith(stem))
        assert row in saved[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    assert db.execute('SELECT state FROM practice_candidate WHERE id=?',(candidate,)).fetchone()[0] == 'unmatched'
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(event,)).fetchone()
    evidence = dict(db.execute('SELECT passage_id, stage FROM practice_event_evidence WHERE event_id=?',(event,)))
    for key,stage in [('written-officials','initiative'),('spoken','action'),('rejection','result')]:
        assert evidence['0407-fund-commission-art5-'+key] == stage
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-unmatched-{candidate}'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    for expected in ('5. madde','Kurul görevlileri','yönetim kurulu','yazımında hata'):
        assert expected in card,(view,expected)
print('IYI_FUND_ARTICLE5_BOTH_VIEWS_OK',folder,flush=True)
