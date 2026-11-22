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

package=here/'congress-2025-draft.json'
review=here/'congress-2025-review-draft.json'
assert harness.sha(package)=='0176a3b3f9b99208200c973370adbdfea726a0625a136139342139884e6d355a'
assert harness.sha(review)=='d584938c1ee6ed51520bed43dbe28c7e566bacd4ad89af1e0678d9ab62643126'
stem='0409-dbp-2025-7-olagan'
receipt=harness.main(package,review,'congress-2025',stem+'-event',stem+'-relation',None,
                     expected_party='dbp',namespace='gsd-0409')
folder=Path(receipt['preview'])
manifest=json.loads((folder/'manifest.json').read_text())
assert manifest['preview'] and manifest['renderer_version']==30
records=json.loads((folder/'records.json').read_text())
draft=json.loads(package.read_text())['practice_records']
assert len(draft['practice_event'])==2 and len(draft['practice_relation'])==2 and not draft['practice_closure']
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    for table in ('practice_event','practice_relation','practice_statement'):
        for row in draft[table]:
            saved=db.execute('SELECT * FROM '+table+' WHERE id=?',(row['id'],)).fetchone()
            assert saved is not None and row==dict(saved) and row in records[table]
html=(folder/'index.html').read_text()
for row in draft['practice_relation']:
    for where in ('party','comparison'):
        anchor=f'{where}-practice-{row["id"]}'
        assert html.count(f'id="{anchor}"')==1 and f'href="#{anchor}"' in html
for suffix in ('quote','result'):
    assert html.count(f'data-finding-id="{stem}-{suffix}"')==2
print('DBP_CONGRESS_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
