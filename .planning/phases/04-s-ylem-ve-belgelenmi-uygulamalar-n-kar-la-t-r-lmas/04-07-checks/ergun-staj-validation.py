"""Verify the historical signed proposal and the later shared agenda event."""

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
harness.SOURCE = harness.DATA/'practices'/'sources'/'iyi'
scope = 'ergun-staj'
older = '0407-iyi-2018-1019'
later = '0407-iyi-2026-4625'
package = here/f'{scope}-draft.json'
review = here/f'{scope}-review-draft.json'
assert harness.sha(package) == 'e6dd4a04a243146db7954b0da9bac7a2ab0e499e8fb3aa44502ce84ac28679bd'
assert harness.sha(review) == '7108426d324b90f4e76f9cbd384814b1045012f636bf4cca71bd08757f572f33'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']),len(draft['practice_relation'])) == (14,10)
assert not draft['practice_closure']
peer = json.loads((harness.DATA/'practices'/'04-yeni-yol.json').read_bytes())['practice_records']
key = 'tbmm-28-5-008-10-4625-gundem'
peer_event = next(r for r in peer['practice_event'] if r['common_event_key']==key)
group_event = next(r for r in draft['practice_event'] if r['common_event_key']==key)
assert {k:v for k,v in peer_event.items() if k!='id'} == {k:v for k,v in group_event.items() if k!='id'}
receipt = harness.main(package,review,scope,later+'-event',later+'-relation',
                       None,expected_party='iyi',namespace='gsd-0407')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table,row_id in [('practice_event',older+'-event'),('practice_candidate',older+'-unmatched'),
                         ('practice_statement',older+'-statement'),('practice_event',later+'-event'),
                         ('practice_relation',later+'-relation'),('practice_contribution',later+'-contribution')]:
        row = next(r for r in draft[table] if r['id']==row_id)
        assert row in saved[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row_id,)).fetchone())
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?',(older+'-event',)).fetchone()[0]=='2018-09-17'
    assert db.execute('SELECT contribution_kind FROM practice_contribution WHERE id=?',
                      (later+'-contribution',)).fetchone()[0]=='support'
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    for prefix,identity,terms in (
        ('unmatched',older+'-unmatched',('2/1019','17 Eylül','14 Eylül','hükümsüz')),
        ('practice',later+'-relation',('10/4625','20 Ekim','Ergun','borçlanma','Gündemde')),
    ):
        anchor = f'{view}-{prefix}-{identity}'
        tag = f'id="{anchor}"'
        assert page.count(tag)==1 and f'href="#{anchor}"' in page
        card = page.split(tag,1)[1].split('</article>',1)[0]
        for term in terms:
            assert term.casefold() in card.casefold(),(view,identity,term)
print('IYI_ERGUN_STAJ_AND_DATE_CONFLICT_BOTH_VIEWS_OK',folder,flush=True)
