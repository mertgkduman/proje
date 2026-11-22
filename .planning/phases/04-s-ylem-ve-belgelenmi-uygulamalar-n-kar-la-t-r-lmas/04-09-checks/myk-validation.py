"""Check the exact DBP draft and retain its isolated reader snapshot."""

import importlib.util
import json
from pathlib import Path
import sqlite3

here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location(
    'practice_validation',here.parent/'04-04-checks'/'samsun-reply-validation.py')
harness=importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE=here
harness.SOURCE=harness.DATA/'practices'/'sources'/'dbp'

package=here/'myk-institution-draft.json'
review=here/'myk-institution-review-draft.json'
assert harness.sha(package)=='56621deffc7030f1d44a836f927e9d4f86ab55310e3655c5be661c1b08d7112b'
assert harness.sha(review)=='783d123af83273af2b1bd8866bf9c72b361ac5780a52a8b8e90da9ce0a0acddf'
stem='0409-dbp-myk-2025'
receipt=harness.main(package,review,'myk-institution',stem+'-event',stem+'-relation',None,
                     expected_party='dbp',namespace='gsd-0409')
folder=Path(receipt['preview'])
manifest=json.loads((folder/'manifest.json').read_text())
assert manifest['preview'] and manifest['renderer_version']==29
records=json.loads((folder/'records.json').read_text())
draft=json.loads(package.read_text())['practice_records']
assert not draft['practice_closure']
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    for table in ('practice_event','practice_relation','practice_statement'):
        for row in draft[table]:
            saved=db.execute('SELECT * FROM '+table+' WHERE id=?',(row['id'],)).fetchone()
            assert saved is not None and row==dict(saved) and row in records[table]
html=(folder/'index.html').read_text()
for where in ('party','comparison'):
    anchor=f'{where}-practice-{stem}-relation'
    assert html.count(f'id="{anchor}"')==1 and f'href="#{anchor}"' in html
for suffix in ('statement-quote','result'):
    assert html.count(f'data-finding-id="{stem}-{suffix}"')==2
print('DBP_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
