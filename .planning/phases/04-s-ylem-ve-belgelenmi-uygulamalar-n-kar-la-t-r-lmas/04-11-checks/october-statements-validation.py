"""Verify earlier Saadet statements link to the verified events without duplication."""

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
harness.SOURCE = harness.DATA/'practices'/'sources'/'saadet'
fund = '0411-saadet-fund-1007'
mekke = '0411-saadet-mekke-1014'
fund_event = '0411-saadet-2026-fund-7596-event'
mekke_event = '0411-saadet-2026-mekke-event'
package = here/'october-statements-draft.json'
review = here/'october-statements-review-draft.json'
assert harness.sha(package) == '7bbe99652113aa5d53df8c64065db89e207da11ddf3780bf5094c0570c4697ed'
assert harness.sha(review) == '940950e0374322567c44ba02c383e7fbf0f4f078ce3933a4f26ab495be9febae'
draft=json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']),len(draft['practice_relation'])) == (11,11)
assert not draft['practice_closure']
receipt=harness.main(package,review,'october-statements',fund_event,fund+'-relation',None,
                     expected_party='saadet',namespace='gsd-0411')
folder=Path(receipt['preview'])
manifest=json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version']==31
saved=json.loads((folder/'records.json').read_bytes())
page=(folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    for stem,eid,day,snippets in (
        (fund,fund_event,'2026-10-07',('7 Ekim','22 Ekim','portföy yönetim şirketinin','TMSF')),
        (mekke,mekke_event,'2026-10-14',('14 Ekim','5 Kasım','Yemen Diyalog Masası','oyu ret')),
    ):
        for table in ('practice_statement','practice_relation','practice_candidate'):
            row=next(r for r in draft[table] if r['id'].startswith(stem))
            assert row in saved[table]
            assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
        assert db.execute('SELECT statement_at FROM practice_statement WHERE id=?',(stem+'-statement',)).fetchone()[0]==day
        assert db.execute('SELECT count(*) FROM practice_relation WHERE event_id=?',(eid,)).fetchone()[0]==2
        for view in ('party','comparison'):
            anchor=f'{view}-practice-{stem}-relation'
            tag=f'id="{anchor}"'
            assert page.count(tag)==1 and f'href="#{anchor}"' in page
            assert all(val in page.split(tag,1)[1].split('</article>',1)[0] for val in snippets),(view,stem)
print('SAADET_EARLIER_STATEMENTS_SHARED_EVENTS_BOTH_VIEWS_OK',folder,flush=True)
