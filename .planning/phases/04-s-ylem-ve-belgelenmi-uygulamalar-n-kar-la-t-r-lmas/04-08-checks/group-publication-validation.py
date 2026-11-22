"""Validate the publication question and its unpaired card in both views."""

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
package = here/'group-publication-draft.json'
review = here/'group-publication-review-draft.json'
assert harness.sha(package)=='46b5e995878a2a83ba42bbe61d62c9a88be6dbab6398c88e8840dafdb5a7b786'
assert harness.sha(review)=='61992179f0003ed93c3b3a6b4fb57d802b5ad83b0e158cf2fedd739894398707'
stem = '0408-question-36200'
draft = json.loads(package.read_text())['practice_records']
event, candidate, dispute = (stem+'-'+suffix for suffix in ('event','candidate','dispute'))
unchanged_relation, = (r['id'] for r in draft['practice_relation'])
receipt = harness.main(package,review,'group-publication',event,unchanged_relation,None,
                       expected_party='yeni-yol',namespace='gsd-0408')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_text())
assert manifest['preview'] and manifest['renderer_version']==30
records = json.loads((folder/'records.json').read_text())
assert len(draft['practice_event'])==2 and not draft['practice_closure']
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory = sqlite3.Row
    for table,identity in [('practice_event',event),('practice_candidate',candidate),('practice_dispute',dispute)]:
        row = next(r for r in draft[table] if r['id']==identity)
        assert row in records[table] and row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(identity,)).fetchone())
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(event,)).fetchone()
html = (folder/'index.html').read_text()
for where in ('party','comparison'):
    anchor = f'{where}-unmatched-{candidate}'
    tag = f'id="{anchor}"'
    assert html.count(tag)==1 and f'href="#{anchor}"' in html
    card = html.split(tag,1)[1].split('</article>',1)[0]
    assert all(word in card for word in ('Araştırma sürüyor','252','3.162','Davutoğlu'))
assert html.count(f'data-finding-id="{stem}-dispute-summary"')==2
print('YENI_YOL_UNMATCHED_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
