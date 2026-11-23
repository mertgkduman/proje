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
scope = 'baglar-services'
stem = '0409-baglar-services-'
package = here/f'{scope}-draft.json'
review = here/f'{scope}-review-draft.json'
assert harness.sha(package) == 'a379f4a80a73e73fd9609eccb8f148c00d41af7875a0e37372d6683fb1dded83'
assert harness.sha(review) == '238af44daf29f7ca7e80bef5533e4eadd41aa0ffc404fdae9a2adc4bb8188729'
cases = {
    '11': ('2015-01-06','96 kişi-ay','geçici işçi'),
    '15': ('2015-01-07','125.050 TL','367 kişi'),
    '17': ('2015-01-08','Şeyhşamil','yakacak'),
    '18': ('2015-01-08','Nevroz Parkı','emzirme odası'),
    '19': ('2015-01-08','11.000 TL','Eğitim Destek Evi'),
    '21': ('2015-01-08','Şeyhşamil','kaldırım'),
    '232': ('2015-11-06','basketbol','Gençlik ve Spor Komisyonuna'),
}
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (25, 7)
assert not draft['practice_closure']
receipt = harness.main(package,review,scope,stem+'18-event','0409-dbp-baglar-2015-cemr-relation',
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
print('DBP_BAGLAR_SERVICES_BOTH_VIEWS_OK',folder,flush=True)
