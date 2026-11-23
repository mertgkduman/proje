"""Verify seven distinct council decisions and their reader anchors."""

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
harness.SOURCE = harness.DATA/'practices'/'sources'/'dbp'
scope = 'baglar-february'
stem = '0409-baglar-february-'
package = here/f'{scope}-draft.json'
review = here/f'{scope}-review-draft.json'
assert harness.sha(package) == '637c8be0b0a2c33cbfb29a05c9bb9f7645ec42571a85f0145e43cd10ac607c1d'
assert harness.sha(review) == 'd8559c46ee68a9a4eecc4882eff6844bb9168d9a597a783b952c5c42bd69cfb4'
cases = {
    '32': ('2015-02-03','40 kişi','teslim belgeleri'),
    '35': ('2015-02-04','5 Nisan','konteyner'),
    '36': ('2015-02-04','15 resim','Protokol aslı'),
    '37': ('2015-02-04','Cuma pazarı','Gıda hijyeni'),
    '39': ('2015-02-05','araç çekicisi','ayrı komisyona ait'),
    '40': ('2015-02-05','Suruç','teslim tutanağı'),
    '41': ('2015-02-05','iki elektrik aboneliğini','Ödeme makbuzu'),
}
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (36, 7)
assert not draft['practice_closure']
receipt = harness.main(package,review,scope,stem+'36-event','0409-dbp-baglar-2015-cemr-relation',
                       None,expected_party='dbp',namespace='gsd-0409')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for number,(day,*_) in cases.items():
        event = stem+number+'-event'
        candidate = stem+number+'-unmatched'
        for table,row_id in [('practice_event',event),('practice_candidate',candidate)]:
            row = next(r for r in draft[table] if r['id']==row_id)
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row_id,)).fetchone())
        assert db.execute('SELECT event_at FROM practice_event WHERE id=?',(event,)).fetchone()[0] == day
        assert db.execute('SELECT state FROM practice_candidate WHERE id=?',(candidate,)).fetchone()[0] == 'unmatched'
        assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(event,)).fetchone()
        assert {row[0] for row in db.execute('SELECT stage FROM practice_event_evidence WHERE event_id=?',(event,))} == {'initiative','action','result'}
page = (folder/'index.html').read_text()
for number,(_, *terms) in cases.items():
    candidate = stem+number+'-unmatched'
    for view in ('party','comparison'):
        anchor = f'{view}-unmatched-{candidate}'
        tag = f'id="{anchor}"'
        assert page.count(tag) == 1 and f'href="#{anchor}"' in page
        card = page.split(tag,1)[1].split('</article>',1)[0]
        for expected in terms:
            assert expected.casefold().replace('i̇','i') in card.casefold().replace('i̇','i'),(view,number,expected)
print('DBP_BAGLAR_FEBRUARY_BOTH_VIEWS_OK',folder,flush=True)
