"""Verify the 2/3940 referral and the different recorded filing dates."""

import importlib.util
import json
from pathlib import Path
import sqlite3

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation',here.parent/'04-04-checks'/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = here
harness.SOURCE = harness.DATA/'practices/sources/yeni-yol'
stem = '0408-yeni-yol-2026-3940'
package = here/'imei-bill-draft.json'
review = here/'imei-bill-review-draft.json'
assert harness.sha(package)=='baef58104d5b41de20874569d5feb95fae00887e518b0d00dcc7d472725147a4'
assert harness.sha(review)=='13140d2aba0e643c6f56c773f24da306e701078257484f23d3eedd19a45988b0'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event'])==9 and len(draft['practice_relation'])==5
assert not draft['practice_closure']
receipt = harness.main(package,review,'imei-bill',stem+'-event','0408-yeni-yol-2026-7573-relation',None,
    expected_party='yeni-yol',namespace='gsd-0408')
folder = Path(receipt['preview'])
assert json.loads((folder/'manifest.json').read_bytes())['renderer_version']==31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_candidate','practice_relation','practice_contribution','practice_dispute'):
        for row in draft[table]:
            assert row in saved[table]
            assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    assert not db.execute("SELECT 1 FROM practice_event_evidence WHERE event_id=? AND stage='result'",
        (stem+'-event',)).fetchone()
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(stem+'-event',)).fetchone()
    assert db.execute("SELECT count(*) FROM manual_passage WHERE passage_id LIKE '0408-imei-signed-%'").fetchone()[0]==8
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor=f'{view}-unmatched-{stem}-unmatched'
    tag=f'id="{anchor}"'
    assert page.count(tag)==1 and f'href="#{anchor}"' in page
    card=page.split(tag,1)[1].split('</article>',1)[0]
    assert all(word in card for word in ('2/3940','7 Ekim','8 Ekim','9 Ekim','telefon kullanım izin harc'))
print('YENI_YOL_3940_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
