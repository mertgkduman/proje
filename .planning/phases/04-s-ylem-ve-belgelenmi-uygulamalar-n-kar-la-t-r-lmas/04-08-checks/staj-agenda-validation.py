"""Verify the two legislative steps and Yeni Yol's attributed support."""

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
july = '0408-yeni-yol-2026-3778'
october = '0408-yeni-yol-2026-4625'
package = here/'staj-agenda-draft.json'
review = here/'staj-agenda-review-draft.json'
assert harness.sha(package) == '610af41f5cf37084de3e2aabe99a5c43e4070f0c02348d5998440f195b34152b'
assert harness.sha(review) == '1edbbb5d1c21b02771d8f6db49f15dc148265f3f478f65974cc0eee30f7348df'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (15, 10)
assert not draft['practice_closure']
receipt = harness.main(package, review, 'staj-agenda', october+'-event', october+'-relation', None,
                       expected_party='yeni-yol', namespace='gsd-0408')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_relation','practice_candidate','practice_contribution'):
        for row in draft[table]:
            if row['id'].startswith((july,october)):
                assert row in saved[table]
                assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    actions = dict(db.execute(
        'SELECT event_at, common_event_key FROM practice_event WHERE id IN (?,?)',
        (july+'-event',october+'-event')))
    assert actions == {'2026-07-21':'tbmm-28-4-2-3778-filing','2026-10-20':'tbmm-28-5-008-10-4625-gundem'}
    evidence = dict(db.execute('SELECT passage_id, stage FROM practice_event_evidence WHERE event_id=?',
                               (october+'-event',)))
    assert evidence['0408-staj-agenda-floor-call'] == 'action'
    assert evidence['0408-staj-agenda-floor-decision'] == 'result'
    assert evidence['0408-staj-agenda-inquiry-register-filed'] == 'initiative'
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-practice-{october}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    for expected in ('2/3778','10/4625','20 Ekim','ön görüşme','Gündemde','Elif Esen'):
        assert expected in card,(view,expected)
print('YENI_YOL_STAJ_AGENDA_BOTH_VIEWS_OK',folder,flush=True)
