"""Check both October fund procedures across SQLite and report views."""

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
harness.SOURCE = harness.DATA/'practices/sources/iyi'
stem = '0407-iyi-2026-fund-7596'
opening = '0407-iyi-2026-fund-1007'
package = here/'fund-floor-draft.json'
review = here/'fund-floor-review-draft.json'
assert harness.sha(package)=='91a4be3e94e699d1c63414016e69ca7b4201a1f83a666b95e2039f349b1cd930'
assert harness.sha(review)=='e175f977ac9160185e4fdd3fd750549e60ae4fe6c7446c4803b963e77a50aac0'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event'])==9 and len(draft['practice_relation'])==7
assert not draft['practice_closure']
receipt = harness.main(package,review,'fund-floor',stem+'-event',stem+'-relation',None,
                       expected_party='iyi',namespace='gsd-0407')
folder = Path(receipt['preview'])
assert json.loads((folder/'manifest.json').read_bytes())['renderer_version']==31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_candidate','practice_relation','practice_statement','practice_contribution'):
        for row in draft[table]:
            assert row in saved[table]
            assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    assert not db.execute("SELECT 1 FROM practice_event_evidence WHERE event_id=? AND stage='result'",
                          (opening+'-event',)).fetchone()
    assert db.execute("SELECT count(*) FROM practice_contribution WHERE event_id=?",
                      (opening+'-event',)).fetchone()[0]==2
    assert db.execute("SELECT count(*) FROM practice_contribution WHERE event_id=?",
                      (stem+'-event',)).fetchone()[0]==1
report = (folder/'index.html').read_text()
for view in ('party','comparison'):
    for anchor,required in [
        (f'{view}-unmatched-{opening}-unmatched',('Usta','Dalgın','komisyon')),
        (f'{view}-practice-{stem}-relation',('7596','isteğe bağlı','tahsil','elektronik')),
    ]:
        tag = f'id="{anchor}"'
        assert report.count(tag)==1 and f'href="#{anchor}"' in report
        card = report.split(tag,1)[1].split('</article>',1)[0]
        assert all(word in card for word in required),(view,anchor)
print('IYI_FUND_FLOOR_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
