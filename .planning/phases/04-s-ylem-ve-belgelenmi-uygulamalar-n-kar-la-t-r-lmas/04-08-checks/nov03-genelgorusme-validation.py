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
scope = 'nov03-genelgorusme'
if party=='iyi':
    namespace, counts, package_hash, review_hash, relation, term = (
        'gsd-0407', (15,10),
        '11ba39158dc46142f991cfa0fc9b55f104a3803898ad38caabb116b4d313e030',
        'ecf0da64a85188cf99f1f6f88aec8f845c5520f37bd5046b460fa05c216f9a19',
        '0407-iyi-2026-4625-relation','Hasan Toktaş')
else:
    assert party=='yeni-yol'
    namespace, counts, package_hash, review_hash, relation, term = (
        'gsd-0408', (17,11),
        'e9ed471ef47e320f8826eed5e36702fe04a982546975e7d3ab4c13241ca2d43b',
        'f9d950044b19ffb6d259c23c7940f4caedcea5d65837f7edfae384a5a3dd3381',
        '0408-yeni-yol-2026-kisacik-madde5-relation','Sadullah Kısacık')
stem = namespace.removeprefix('gsd-')+'-'+scope
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
