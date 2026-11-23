"""Verify the Saadet statement and 7596 result in both reader views."""

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
stem = '0411-saadet-2026-fund-7596'
package = here/'fund-7596-draft.json'
review = here/'fund-7596-review-draft.json'
assert harness.sha(package) == 'a9004e045d900e4bea5a58c65604e6f7bb77b2fd0dc1112823bc125358b01953'
assert harness.sha(review) == '2db26b3bc299304c96cfbd3af276b2e33821c41a3f5819f30874fa226f23d6db'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (9, 7)
assert not draft['practice_closure']
receipt = harness.main(package, review, 'fund-7596', stem+'-event', stem+'-relation', None,
                       expected_party='saadet', namespace='gsd-0411')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_statement'):
        row = next(r for r in draft[table] if r['id'].startswith(stem))
        assert row in saved[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    assert not db.execute('SELECT 1 FROM practice_contribution WHERE event_id=?', (stem+'-event',)).fetchone()
    key = db.execute('SELECT common_event_key FROM practice_event WHERE id=?', (stem+'-event',)).fetchone()[0]
    assert key == 'tbmm-28-5-010-2-3939-yatirim-fonlari-7596'
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    for expected in ('Mahmut Arıkan','1.000.000 TL','2/3939','21 Ekim','22 Ekim','7596','SPK','fiilen'):
        assert expected in card, (view, expected)
print('SAADET_FUND_7596_DATES_AUTHORITY_BOTH_VIEWS_OK', folder, flush=True)
