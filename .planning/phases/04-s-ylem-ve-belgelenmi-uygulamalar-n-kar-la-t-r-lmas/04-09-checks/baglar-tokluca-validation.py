"""Verify four municipal decisions with separate limits on their legal effect."""

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
scope = 'baglar-tokluca'
stem = '0409-tokluca-'
package = here/f'{scope}-draft.json'
review = here/f'{scope}-review-draft.json'
assert harness.sha(package) == '38b248a8e32b4f232b201c710d19dfffd4c0fffa80a52dbbb3ea2c88682a056c'
assert harness.sha(review) == 'de7cdd5cfaef9ee32fb0c95a10be87614f67039ea2ee8ad70dcbca8518851253'
cases = {
    '2015-22': ('2015-01-09', 'Avşin', '564 kişi'),
    '2015-251': ('2015-12-11', '490-E.3299', 'komisyona sevk'),
    '2016-64': ('2016-03-11', 'Avşin', '520 kişi'),
    '2016-187': ('2016-09-08', 'Tokluca', '4774'),
}
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (29, 7)
assert not draft['practice_closure']
receipt = harness.main(package,review,scope,stem+'2016-187-event',
    '0409-dbp-baglar-2015-cemr-relation',None,expected_party='dbp',namespace='gsd-0409')
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
    for key in ('5393-approval','5393-effect','6360-threshold','2021-road','2021-road-later'):
        assert db.execute('SELECT 1 FROM passage WHERE id=?',(stem+key,)).fetchone()
page = (folder/'index.html').read_text()
for number,(_, *terms) in cases.items():
    candidate = stem+number+'-unmatched'
    for view in ('party','comparison'):
        tag = f'id="{view}-unmatched-{candidate}"'
        assert page.count(tag) == 1 and f'href="#{view}-unmatched-{candidate}"' in page
        card = page.split(tag,1)[1].split('</article>',1)[0]
        for expected in (*terms,'vali onayının tarihi'):
            assert expected.casefold().replace('i̇','i') in card.casefold().replace('i̇','i'),(view,number,expected)
print('DBP_TOKLUCA_FOUR_COUNCIL_DECISIONS_BOTH_VIEWS_OK',folder,flush=True)
