"""Verify the 8/153 agenda record and group contribution on both reader views."""

import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

here = Path(sys.argv[2]).resolve()
party = sys.argv[1]
spec = importlib.util.spec_from_file_location(
    'practice_validation', here.parent/'04-04-checks'/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = here
harness.SOURCE = harness.DATA/'practices'/'sources'/party
scope = 'nov03-genelgorusme-v2'
if party=='iyi':
    namespace, counts, package_hash, review_hash, relation, term = (
        'gsd-0407', (15,10),
        '4b909a10e22d15d71c962cd4f703cfa605baa47e6470ef95aa05358b76c8c86b',
        '1fd77f8eaa7a31e88e04635389288b8532636767d285f5d6d66b5f0599d7fc0f',
        '0407-iyi-2026-4625-relation','Hasan Toktaş')
else:
    assert party=='yeni-yol'
    namespace, counts, package_hash, review_hash, relation, term = (
        'gsd-0408', (17,11),
        '0bb0d54df584d6ab3068bdbd8bacfc9e857977610a2e351b75e5fad052c047cb',
        '4ec2771c1581b64abce0c607f9d5dc00db8efccfd1b777ff519b2bcdb05a3c7d',
        '0408-yeni-yol-2026-kisacik-madde5-relation','Sadullah Kısacık')
stem = namespace.removeprefix('gsd-')+'-nov03-genelgorusme'
package = here/f'{scope}-draft.json'
review = here/f'{scope}-review-draft.json'
assert harness.sha(package) == package_hash
assert harness.sha(review) == review_hash
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']),len(draft['practice_relation']))==counts
assert not draft['practice_closure']
eid = stem+'-event'
candidate = stem+'-unmatched'
cid = stem+'-contribution'
receipt = harness.main(package,review,scope,eid,relation,None,expected_party=party,namespace=namespace)
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version']==31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory=sqlite3.Row
    for table,row_id in [('practice_event',eid),('practice_candidate',candidate),('practice_contribution',cid)]:
        row=next(r for r in draft[table] if r['id']==row_id)
        assert row in saved[table]
        assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row_id,)).fetchone())
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(eid,)).fetchone()
    assert {row[0] for row in db.execute('SELECT stage FROM practice_event_evidence WHERE event_id=?',(eid,))}=={'initiative','action','result'}
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor=f'{view}-unmatched-{candidate}'
    tag=f'id="{anchor}"'
    assert page.count(tag)==1 and f'href="#{anchor}"' in page
    card=page.split(tag,1)[1].split('</article>',1)[0]
    for expected in (term,'8/153','Gündemde','kabul edilmedi','isimli oylama','10/4826'):
        assert expected.casefold().replace('i̇','i') in card.casefold().replace('i̇','i'),(view,expected)
print('TBMM_8153_PARTY_CONTRIBUTION_BOTH_VIEWS_OK',party,folder,flush=True)
