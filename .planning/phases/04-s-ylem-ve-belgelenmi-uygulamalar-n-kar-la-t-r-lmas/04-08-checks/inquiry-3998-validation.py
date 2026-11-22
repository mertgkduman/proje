"""Verify official records of the 10/3998 agenda vote and procedural dispute."""

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
harness.SOURCE = harness.DATA/'practices'/'sources'/'yeni-yol'
stem = '0408-yeni-yol-2026-10-3998'
package = here/'inquiry-3998-draft.json'
review = here/'inquiry-3998-review-draft.json'
assert harness.sha(package) == 'd7b129bdaa370ecc57ad7a9f8643d118c8c4c04af53e06708e256fc945228a92'
assert harness.sha(review) == 'eb1ff8cd91bbc3b2215e6864b2f9d60193e996619346a9c8937de0120d094251'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 7 and len(draft['practice_relation']) == 4
assert not draft['practice_closure']
receipt = harness.main(package, review, 'inquiry-3998', stem+'-event', stem+'-relation', None,
                       expected_party='yeni-yol', namespace='gsd-0408')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_dispute', 'practice_statement'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    result = db.execute("SELECT passage_id FROM practice_event_evidence WHERE event_id=? AND stage='result'",
                        (stem+'-event',)).fetchall()
    assert {row[0] for row in result} == {'0408-stats-yy-3998-session-decision','0408-stats-yy-3998-summary-result'}
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    assert all(word in card for word in ('10/3998','Gündemde','elektronik oylama','kabul edilmedi'))
assert page.count(f'data-finding-id="{stem}-vote-dispute-finding"') == 2
print('YENI_YOL_3998_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
