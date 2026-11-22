"""Verify the exact 2024 congress addition for İYİ Parti."""

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
harness.SOURCE=harness.DATA/'practices'/'sources'/'iyi'
package=here/'extraordinary-2024-draft.json'
review=here/'extraordinary-2024-review-draft.json'
assert harness.sha(package)=='3f63e22889b72d527e75cb5686ce193e3dff8aade4804d054ac0797b063af26a'
assert harness.sha(review)=='ce6e1318c9af54249a199fa9aff789e9626c44fbe4846df07a7f2207154da31d'
stem='0407-iyi-2024-5-olaganustu'
receipt=harness.main(package,review,'extraordinary-2024',stem+'-event',stem+'-relation',None,
                     expected_party='iyi',namespace='gsd-0407')
folder=Path(receipt['preview'])
manifest=json.loads((folder/'manifest.json').read_text())
assert manifest['preview'] and manifest['renderer_version']==30
saved=json.loads((folder/'records.json').read_text())
draft=json.loads(package.read_text())['practice_records']
assert len(draft['practice_event'])==2 and len(draft['practice_relation'])==2 and not draft['practice_closure']
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    for table in ('practice_event','practice_relation','practice_statement'):
        for row in draft[table]:
            assert row in saved[table] and row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
html=(folder/'index.html').read_text()
for row in draft['practice_relation']:
    for view in ('party','comparison'):
        anchor=f'{view}-practice-{row["id"]}'
        assert html.count(f'id="{anchor}"')==1 and f'href="#{anchor}"' in html
for suffix in ('quote','result'):
    assert html.count(f'data-finding-id="{stem}-{suffix}"')==2
print('IYI_2024_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
