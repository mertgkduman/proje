"""Verify two pension tracks without assigning one bill's result to the other."""

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
stem = '0411-saadet-2026-7573'
proposal = '0411-saadet-2026-2-3456'
package = here/'pension-floor-final-draft.json'
review = here/'pension-floor-final-review-draft.json'
assert harness.sha(package) == '4135d9325145df18e6d2ac1251347da31838c5f1d39b92d6a6ca3df50fbd42c0'
assert harness.sha(review) == 'bdc097084d4121d5f33ce836c278c164b3b78b6a63e7e920f743d1a7157fb3ff'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 8 and len(draft['practice_relation']) == 6
assert not draft['practice_closure']
receipt = harness.main(package, review, 'pension-floor-final', stem+'-event', stem+'-relation', None,
                       expected_party='saadet', namespace='gsd-0411')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_statement', 'practice_dispute'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?', (proposal+'-event',)).fetchone()
    assert not db.execute(
        "SELECT 1 FROM practice_event_evidence WHERE event_id=? AND stage='result'", (proposal+'-event',)).fetchone()
    assert db.execute('SELECT result_finding_id FROM practice_relation WHERE id=?',
                      (stem+'-relation',)).fetchone()[0] == stem+'-result'
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    for anchor, snippets in (
        (f'{view}-unmatched-{proposal}-candidate', ('2/3456','asgari ücret','Araştırma sürüyor')),
        (f'{view}-practice-{stem}-relation', ('2/3464','20.000 TL','asgari ücret','Ocak 2026','247 kabul','245 kabul','2 mükerrer','KATILMADI')),
    ):
        tag = f'id="{anchor}"'
        assert page.count(tag) == 1 and f'href="#{anchor}"' in page
        card = page.split(tag, 1)[1].split('</article>', 1)[0]
        assert all(text in card for text in snippets)
print('SAADET_PENSION_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
