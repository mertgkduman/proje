"""Verify Yeni Yol's 7573 comparison against the common open ballot."""

from collections import Counter
import importlib.util
from html import unescape
import json
from pathlib import Path
import re
import sqlite3

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', here.parent/'04-04-checks'/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = here
harness.SOURCE = harness.DATA/'practices'/'sources'/'yeni-yol'
stem = '0408-yeni-yol-2026-7573'
package = here/'pension-floor-yeni-yol-draft.json'
review = here/'pension-floor-yeni-yol-review-draft.json'
assert harness.sha(package) == '55ae0de54f0cf6db84d9e814eb7720e3a91b37048c8394f38fa8f10f80d6abc2'
assert harness.sha(review) == '54752a26adbcbfd1f1c00ce88638f07bb4dbf73026922cd6c07aac64c1e1b1d2'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 8 and len(draft['practice_relation']) == 5
assert not draft['practice_closure']
receipt = harness.main(package, review, 'pension-floor-yeni-yol', stem+'-event', stem+'-relation', None,
                       expected_party='yeni-yol', namespace='gsd-0408')
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
    assert db.execute('SELECT common_event_key FROM practice_event WHERE id=?',
                      (stem+'-event',)).fetchone()[0] == 'tbmm-28-4-050-2-3464-7573'
    for row in db.execute("SELECT original_path,readable_path FROM document_version WHERE id LIKE '0408-floor-%' AND id NOT LIKE '0408-floor-yy-2026-%'"):
        for path in row:
            assert (harness.SOURCE/path).read_bytes() == (harness.DATA/'practices'/'sources'/'iyi'/path).read_bytes()
    ballot_path = db.execute("SELECT original_path FROM document_version WHERE id='0408-floor-iyi-7573-ballot-v1'").fetchone()[0]
ballot = (harness.SOURCE / ballot_path).read_bytes().decode('cp1254')
ballot_rows = []
for raw in re.findall(r'<tr\b[^>]*>(.*?)</tr>', ballot, re.S | re.I):
    cells = [unescape(re.sub(r'<[^>]+>', '', cell)).strip()
             for cell in re.findall(r'<td\b[^>]*>(.*?)</td>', raw, re.S | re.I)]
    if len(cells) == 9 and cells[3] == 'Yeni Yol Partisi':
        ballot_rows.append(cells)
assert Counter(row[6] for row in ballot_rows) == {'RET': 16, 'KATILMADI': 4}
assert any(row[1:3] == ['KISACIK','Sadullah'] and row[6:] == ['RET','23.01.2026','00:52:29']
           for row in ballot_rows)
assert any(row[1:3] == ['KAYA','Bülent'] and row[6:] == ['RET','23.01.2026','00:52:28']
           for row in ballot_rows)
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    assert all(word in card for word in ('20.000 TL','16 ret ve dört katılmadı','Kısacık','245 kabul','iki mükerrer'))
assert page.count(f'data-finding-id="{stem}-vote-dispute-finding"') == 2
print('YENI_YOL_7573_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
