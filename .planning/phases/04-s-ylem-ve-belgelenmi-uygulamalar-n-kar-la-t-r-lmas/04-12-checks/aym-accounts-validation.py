"""Verify the two accounts decisions and the archived charter provision."""

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
stem = '0412-demokrat-aym-2023-hesap'
package = here/'aym-accounts-draft.json'
review = here/'aym-accounts-review-draft.json'
assert harness.sha(package) == '607d094894504a06decebb2e1c1d60320eac1faf9d0571cc4de68f061f86b1f1'
assert harness.sha(review) == '7cd4547abd58a31685fa339dcdf236a327b7e9b69fd94dd6dd0686851a2a497e'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']),len(draft['practice_relation'])) == (14,13)
assert not draft['practice_closure']
receipt = harness.main(package, review, 'aym-accounts', stem+'-event', stem+'-relation', None,
                       expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
page = (folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for year, day, publication, text_day, text_pub in (
        (2021,'2024-12-25','2025-03-14','25 Aralık 2024','14 Mart 2025'),
        (2023,'2025-12-25','2026-04-20','25 Aralık 2025','20 Nisan 2026'),
    ):
        stem = f'0412-demokrat-aym-{year}-hesap'
        for table in ('practice_event','practice_relation','practice_candidate'):
            row = next(r for r in draft[table] if r['id'].startswith(stem))
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
        assert db.execute('SELECT event_at FROM practice_event WHERE id=?', (stem+'-event',)).fetchone()[0] == day
        assert db.execute('SELECT published_at FROM source_attribution WHERE version_id=?',
                          (f'0412-aym-{year}-hesap-v1',)).fetchone()[0] == publication
        assert not db.execute('SELECT 1 FROM practice_contribution WHERE event_id=?', (stem+'-event',)).fetchone()
        for view in ('party','comparison'):
            anchor = f'{view}-practice-{stem}-relation'
            tag = f'id="{anchor}"'
            assert page.count(tag) == 1 and f'href="#{anchor}"' in page
            card = page.split(tag,1)[1].split('</article>',1)[0]
            assert all(text in card for text in (str(year),text_day,text_pub,'oybirliğiyle','İlk gönderim günü')), (view, year)
print('DEMOKRAT_TWO_AYM_DECISIONS_BOTH_VIEWS_OK', folder, flush=True)
