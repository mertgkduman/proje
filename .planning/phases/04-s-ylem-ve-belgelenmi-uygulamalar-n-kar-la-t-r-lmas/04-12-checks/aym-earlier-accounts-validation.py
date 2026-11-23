"""Verify the 2020 and 2022 court decisions and source chronology."""

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
stem = '0412-demokrat-aym-2022-hesap'
package = here/'aym-earlier-accounts-draft.json'
review = here/'aym-earlier-accounts-review-draft.json'
assert harness.sha(package) == '3ed0bafd5a7a350c44efe50efc0e10dda714286e8b775ca01b05b878c74ef58e'
assert harness.sha(review) == '038059e25629db63fab9ac057f002409e783839dc35c2b1e0904a58f347c5588'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']),len(draft['practice_relation'])) == (16,15)
assert not draft['practice_closure']
receipt = harness.main(package, review, 'aym-earlier-accounts', stem+'-event', stem+'-relation', None,
                       expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
page = (folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for year, day, publication, text_day, text_pub in (
        (2020,'2024-06-27','2025-01-10','27 Haziran 2024','10 Ocak 2025'),
        (2022,'2025-12-25','2026-04-16','25 Aralık 2025','16 Nisan 2026'),
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
print('DEMOKRAT_TWO_EARLIER_AYM_DECISIONS_BOTH_VIEWS_OK', folder, flush=True)
