"""Verify the separate article 5 motion, contribution and report links."""

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
scope = 'fund-kisacik'
stem = '0408-yeni-yol-2026-kisacik-madde5'
event = stem+'-event'
relation = stem+'-relation'
package = here/f'{scope}-draft.json'
review = here/f'{scope}-review-draft.json'
assert harness.sha(package) == '873f72cc844d2e2256881248f782b6ed5846432aac6356f93c068fae75ad47be'
assert harness.sha(review) == 'fdd7954a1a181186db388904a5baa5f0d60b2d503974d7aa77d6fc97bc5a3cad'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']),len(draft['practice_relation'])) == (16,11)
assert not draft['practice_closure']
receipt = harness.main(package,review,scope,event,relation,None,expected_party='yeni-yol',namespace='gsd-0408')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table,identity in [('practice_event',event),('practice_relation',relation),
                           ('practice_contribution',stem+'-contribution')]:
        row = next(r for r in draft[table] if r['id']==identity)
        assert row in saved[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(identity,)).fetchone())
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?',(event,)).fetchone()[0]=='2026-10-14'
    assert db.execute('SELECT kind FROM actor WHERE id=?',(stem+'-actor',)).fetchone()[0]=='individual_mp'
    endpoints = {r[0] for r in db.execute(
        "SELECT passage_id FROM practice_event_evidence WHERE event_id=? AND stage='result'",(event,))}
    assert endpoints == {'0408-fund-kisacik-report-reject','0408-fund-kisacik-report-article'}
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-practice-{relation}'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    for expected in ('2/3939','Kısacık','14 Ekim','22 Ekim','reddetti','7596'):
        assert expected in card,(view,expected)
print('YENI_YOL_KISACIK_ART5_BOTH_VIEWS_OK',folder,flush=True)
