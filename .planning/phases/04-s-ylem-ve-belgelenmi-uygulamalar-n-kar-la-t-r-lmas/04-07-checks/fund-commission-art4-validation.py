"""Verify the separate 14 October article 4 committee decision."""

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
package = here/'fund-commission-art4-draft.json'
review = here/'fund-commission-art4-review-draft.json'
assert harness.sha(package) == '7e6d78c61a1647e8157b806ed4017067aa29cd820fea0d92afa6b77bdd6ac56a'
assert harness.sha(review) == '7e96cb916293476db91c31bee1f1761bbe7f5be52d109b13aa9f19b7b83b4abc'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (11,9)
assert not draft['practice_closure']
stem = '0407-iyi-2026-commission-art4'
receipt = harness.main(package, review, 'fund-commission-art4', stem+'-event', stem+'-relation', None,
                       expected_party='iyi', namespace='gsd-0407')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version']==31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_statement','practice_relation','practice_candidate'):
        row = next(r for r in draft[table] if r['id'].startswith(stem))
        assert row in saved[table]
        assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    statement = db.execute('SELECT statement_at FROM practice_statement WHERE id=?',(stem+'-statement',)).fetchone()[0]
    assert statement=='2026-10-14'
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?',(stem+'-event',)).fetchone()[0]==statement
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?',('0407-iyi-2026-fund-7596-event',)).fetchone()[0]=='2026-10-22'
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag)==1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    for expected in ('14 Ekim','zorunlu iade','isteğe bağlı','22 Ekim','Taş','Usta'):
        assert expected in card,(view,expected)
print('IYI_COMMITTEE_ART4_DISTINCT_BOTH_VIEWS_OK',folder,flush=True)
