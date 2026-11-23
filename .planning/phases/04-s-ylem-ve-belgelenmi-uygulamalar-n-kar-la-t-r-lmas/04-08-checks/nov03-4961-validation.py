"""Verify the 10/4961 agenda record and group contribution on both reader views."""

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
scope = 'nov03-4961'
if party=='iyi':
    namespace, counts, package_hash, review_hash, relation, term = (
        'gsd-0407', (16,10),
        'b268cf0188bb5b785378d27db0605e8e9e83106c8d40740c553ac013cee180fe',
        '6ef5d3804433db824a71e1f70bf4d98a7be978b30a2c61abce41f3f3a6f73a4d',
        '0407-iyi-2026-4625-relation','Turhan Çömez')
else:
    assert party=='yeni-yol'
    namespace, counts, package_hash, review_hash, relation, term = (
        'gsd-0408', (18,11),
        '1f3baf56de0521d3906440525231f2fb70813c86e1ea609716cf8b93ac0d6dda',
        '3bd0fd614e81851691bc1d7fdefafb50982676fdfc2a36bc7c148ea44ef2672f',
        '0408-yeni-yol-2026-kisacik-madde5-relation','Selçuk Özdağ')
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
    for expected in (term,'10/4961','Gündemde','kabul edilmedi','isimli oylama','16.339.546.449 TL','16 Kasım dahil'):
        assert expected.casefold().replace('i̇','i') in card.casefold().replace('i̇','i'),(view,expected)
print('TBMM_104961_PARTY_CONTRIBUTION_BOTH_VIEWS_OK',party,folder,flush=True)
