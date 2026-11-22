"""Validate one party's isolated parliamentary policy record."""

import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

phase = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'practice_validation', phase/'04-04-checks'/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
cases = {
    'saadet': ('11','0411-saadet-2024-dis-ticaret-1161',2,
        '37b481219abc6cdbb80b86d1fc22d7b582c94bb0d7a37dec3d4d4feaf3b5b831',
        '4e7bfd9060212786b5be9e403f16ce50a97e41b89b07998efd977f88eede80cb'),
    'demokrat': ('12','0412-demokrat-2024-2-1525-gundem',4,
        '038c41387435a499d8704e26aba1d161d5723345a8c7213f855393f38cb2926b',
        'ba14ffcbf86401a44f82df6565a6fab2c0e6111ce10d3ecce8eb3a499a739618'),
}
party = sys.argv[1]
plan, stem, expected_relations, package_hash, review_hash = cases[party]
here = phase/f'04-{plan}-checks'
harness.HERE = here
harness.SOURCE = harness.DATA/'practices'/'sources'/party
package = here/'policy-first-draft.json'
review = here/'policy-first-review-draft.json'
assert (harness.sha(package), harness.sha(review)) == (package_hash, review_hash)
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 3 and len(draft['practice_relation']) == expected_relations
assert not draft['practice_closure']
relation = draft['practice_relation'][-1]['id']
receipt = harness.main(package, review, 'policy-first', stem+'-event', relation, None,
                       expected_party=party, namespace=f'gsd-04{plan}')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 30
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_relation','practice_candidate','practice_dispute'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    if party == 'saadet':
        assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(stem+'-event',)).fetchone()
page = (folder/'index.html').read_text()
for row in draft['practice_relation']:
    for view in ('party','comparison'):
        anchor = f'{view}-practice-{row["id"]}'
        assert page.count(f'id="{anchor}"')==1 and f'href="#{anchor}"' in page
if party == 'saadet':
    for view in ('party','comparison'):
        anchor = f'{view}-unmatched-{stem}-candidate'
        tag = f'id="{anchor}"'
        assert page.count(tag)==1 and f'href="#{anchor}"' in page
        card = page.split(tag,1)[1].split('</article>',1)[0]
        assert all(item in card for item in ('10/1161','Araştırma sürüyor','kabul edilmedi','Gündemde'))
else:
    assert page.count(f'data-finding-id="{stem}-quote"') == 2
print('PARTY_POLICY_DB_JSON_BOTH_VIEWS_OK',party,folder,flush=True)
