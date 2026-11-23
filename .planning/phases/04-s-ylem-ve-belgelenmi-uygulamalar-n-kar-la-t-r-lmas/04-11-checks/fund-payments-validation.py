"""Verify separate fund decision and first-payment events in both views."""

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
decision = '0411-saadet-2026-spk-761903'
payment = '0411-saadet-2026-fund-initial-payment'
law = '0411-saadet-2026-fund-7596'
package = here/'fund-payments-draft.json'
review = here/'fund-payments-review-draft.json'
assert harness.sha(package) == '91d8444678a1db27d7fefd816f026c628cf8f1a9eff3eb7633e1107a99fc0fe7'
assert harness.sha(review) == 'b13affd9ce0a6ac157648c37efba4e0fff9dbc2889bc051babbc51034ea368f1'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (11, 9)
assert not draft['practice_closure']
receipt = harness.main(package, review, 'fund-payments', payment+'-event', payment+'-relation', None,
                       expected_party='saadet', namespace='gsd-0411')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for stem, day in ((law,'2026-10-22'),(decision,'2026-10-27'),(payment,'2026-10-30')):
        for table in ('practice_event','practice_relation','practice_candidate'):
            row = next(r for r in draft[table] if r['id'].startswith(stem))
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
        assert db.execute('SELECT event_at FROM practice_event WHERE id=?', (stem+'-event',)).fetchone()[0] == day
        assert not db.execute('SELECT 1 FROM practice_contribution WHERE event_id=?', (stem+'-event',)).fetchone()
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    for stem, snippets in (
        (decision, ('76/1903','27 Ekim','1 milyon TL','nihai ödemeden')),
        (payment, ('30 Ekim','29,3 milyar TL','3 Kasım','Bakanlığın','İletişim Başkanlığı')),
        (law, ('22 Ekim','7596','SPK')),
    ):
        anchor = f'{view}-practice-{stem}-relation'
        tag = f'id="{anchor}"'
        assert page.count(tag) == 1 and f'href="#{anchor}"' in page
        card = page.split(tag, 1)[1].split('</article>', 1)[0]
        assert all(text in card for text in snippets), (view, stem)
print('SAADET_THREE_FUND_STAGES_BOTH_VIEWS_OK', folder, flush=True)
