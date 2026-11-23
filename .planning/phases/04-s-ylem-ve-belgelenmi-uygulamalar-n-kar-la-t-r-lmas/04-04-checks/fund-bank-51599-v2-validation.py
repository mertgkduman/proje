"""Verify filing and dated notice for written question 7/51599."""

import importlib.util
import json
from pathlib import Path
import sqlite3

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', here/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = here
scope = 'fund-bank-51599-v2'
stem = '0404-yeni-parti-2026-bank-51599'
event = stem+'-event'
candidate = stem+'-unmatched'
package = here/f'{scope}-draft.json'
review = here/f'{scope}-review-draft.json'
assert harness.sha(package) == '7dd0e9d53922d65a4940b169aeca52b71ce16693bc6eadc4696d8d41ba6bb667'
assert harness.sha(review) == 'cfab87e0a39814413640d4a9ccabf062d5e27794bc8058e29a90f418f7bf0bc8'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (142, 141)
assert not draft['practice_closure']
receipt = harness.main(package,review,scope,event,'0404-fon-komisyon-1014-relation',None)
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
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?',(event,)).fetchone()[0] == '2026-10-20'
    assert db.execute('SELECT state FROM practice_candidate WHERE id=?',(candidate,)).fetchone()[0] == 'unmatched'
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(event,)).fetchone()
    evidence = dict(db.execute('SELECT passage_id, stage FROM practice_event_evidence WHERE event_id=?',(event,)))
    for key,stage in [('signed-payments','initiative'),('register-filed','action'),('gelen-question','result')]:
        assert evidence['0404-bank-51599-'+key] == stage
    assert not any('reply' in key or 'pending' in key for key in evidence)
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-unmatched-{candidate}'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    for expected in ('7/51599','Hazine ve Maliye Bakanı','19 Ekim','20 Ekim','5 Kasım'):
        assert expected in card,(view,expected)
print('YENI_PARTI_BANK_51599_BOTH_VIEWS_OK',folder,flush=True)
