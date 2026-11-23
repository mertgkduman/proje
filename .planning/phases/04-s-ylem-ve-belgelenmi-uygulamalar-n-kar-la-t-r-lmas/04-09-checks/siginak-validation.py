"""Verify the field report publication and open party comparison."""

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
harness.SOURCE = harness.DATA/'practices'/'sources'/'dbp'
stem = '0409-diyarbakir-2016-siginak'
event = stem+'-event'
candidate = stem+'-unmatched'
package = here/'siginak-draft.json'
review = here/'siginak-review-draft.json'
assert harness.sha(package) == '19329c5faec65d58e87737e67975fef26e405a4915574e521d204a241ccf9c94'
assert harness.sha(review) == '3e7b2b14224f0a628f48e9a08f4a9afc93b9315adea55ed024bb7d369aa1f14a'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (12, 7)
assert not draft['practice_closure']
receipt = harness.main(package, review, 'siginak', event,
                       '0409-dbp-baglar-2015-cemr-relation', None,
                       expected_party='dbp', namespace='gsd-0409')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_candidate'):
        row = next(r for r in draft[table] if r['id'].startswith(stem))
        assert row in saved[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?',(event,)).fetchone()[0] == '2016-03-10'
    assert db.execute('SELECT state FROM practice_candidate WHERE id=?',(candidate,)).fetchone()[0] == 'unmatched'
    assert not db.execute('SELECT 1 FROM practice_contribution WHERE event_id=?',(event,)).fetchone()
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(event,)).fetchone()
    evidence = dict(db.execute('SELECT passage_id, stage FROM practice_event_evidence WHERE event_id=?',(event,)))
    assert evidence['0409-siginak-index-date'] == 'action'
    assert evidence['0409-siginak-ihd-sample'] == 'result'
    assert evidence['0409-siginak-ihd-decision'] == 'initiative'
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-unmatched-{candidate}'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    for expected in ('sığınma evi','17 kadın','İHD','taahhüdü araştırmaya açık'):
        assert expected in card,(view,expected)
print('DBP_SHELTER_REPORT_BOTH_VIEWS_OK',folder,flush=True)
