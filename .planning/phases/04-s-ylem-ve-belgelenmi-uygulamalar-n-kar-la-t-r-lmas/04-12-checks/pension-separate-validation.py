"""Check that 2/1597, the 7573 vote and 2/3489 retain their own scope."""

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
harness.SOURCE = harness.DATA/'practices'/'sources'/'demokrat'
stem = '0412-demokrat-2026-7573'
bill = '0412-demokrat-2026-2-3489'
package = here/'pension-separate-draft.json'
review = here/'pension-separate-review-draft.json'
assert harness.sha(package) == '7f9326adf48f3e1697e057ae2c9d7672279e8dd1c3926f9f415a86df2249bbb9'
assert harness.sha(review) == '4166c9a17a6b5dc17787aa134948676b2f7c1a613b787579a126e0c5c32895c8'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 10 and len(draft['practice_relation']) == 9
assert not draft['practice_closure']
receipt = harness.main(package, review, 'pension-separate', stem+'-event', stem+'-relation', None,
                       expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_relation','practice_candidate','practice_dispute','practice_statement'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    assert db.execute('SELECT common_event_key FROM practice_event WHERE id=?',
                      (stem+'-event',)).fetchone()[0] == 'tbmm-28-4-050-2-3464-7573'
    assert db.execute('SELECT state FROM practice_candidate WHERE id=?',
                      (bill+'-candidate',)).fetchone()[0] == 'unmatched'
    assert not db.execute("SELECT 1 FROM practice_event_evidence WHERE event_id=? AND stage='result'",
                          (bill+'-event',)).fetchone()
    assert 'KATILMADI' in db.execute("SELECT exact FROM passage WHERE id='0412-floor-iyi-7573-ballot-altintas'").fetchone()[0]
    for row in db.execute("SELECT original_path,readable_path FROM document_version WHERE id LIKE '0412-floor-%'"):
        for path in row:
            assert (harness.SOURCE/path).read_bytes() == (harness.DATA/'practices'/'sources'/'iyi'/path).read_bytes()
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    targets = (
        (f'{view}-practice-{stem}-relation', ('2/1597','20.000 TL','net asgari ücret','KATILMADI')),
        (f'{view}-unmatched-{bill}-candidate', ('2/3489','2.345 gösterge','Araştırma sürüyor')),
    )
    for anchor,terms in targets:
        tag = f'id="{anchor}"'
        assert page.count(tag) == 1 and f'href="#{anchor}"' in page
        card = page.split(tag,1)[1].split('</article>',1)[0]
        assert all(word in card for word in terms)
assert page.count(f'data-finding-id="{stem}-vote-dispute-finding"') == 2
print('DP_RETIREMENT_DISTINCT_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
