"""Validate Yeni Yol's source-bound leadership rotation in an isolated preview."""

import json
from pathlib import Path
import sqlite3
import sys

here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'04-04-checks'))
import importlib.util
spec=importlib.util.spec_from_file_location("practice_validation",here.parent/"04-04-checks"/"samsun-reply-validation.py")
harness=importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)

harness.HERE=here
harness.SOURCE=harness.DATA/'practices'/'sources'/'yeni-yol'
package=here/'institution-rotation-draft.json'
review=here/'institution-rotation-review-draft.json'
assert harness.sha(package)=='24052bd7a0fe48f0abb09b01c14879071f81d2d972e239f9949dd6b1633aed1d'
assert harness.sha(review)=='4304ecd8eb5f0a654b1687370856edd13eab98a753059d275beaeb75b5d85657'
stem='0408-chair-rotation'
receipt=harness.main(package,review,'chair-rotation',stem+'-event',stem+'-relation',None,
                     expected_party='yeni-yol',namespace='gsd-0408')
folder=Path(receipt['preview'])
manifest=json.loads((folder/'manifest.json').read_text())
assert manifest['preview'] and manifest['renderer_version']==29
html=(folder/'index.html').read_text()
snapshot=json.loads((folder/'records.json').read_text())
draft=json.loads(package.read_text())['practice_records']
assert not draft['practice_closure']
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    for key in ('practice_event','practice_statement','practice_relation','practice_dispute'):
        for row in draft[key]:
            stored=db.execute('SELECT * FROM '+key+' WHERE id=?',(row['id'],)).fetchone()
            assert stored is not None and row==dict(stored) and row in snapshot[key]
for where in ('party','comparison'):
    anchor=f'{where}-practice-{stem}-relation'
    assert html.count(f'id="{anchor}"')==1 and f'href="#{anchor}"' in html
for suffix in ('statement-quote','result','dispute-summary'):
    assert html.count(f'data-finding-id="{stem}-{suffix}"')==2

print('YENI_YOL_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
