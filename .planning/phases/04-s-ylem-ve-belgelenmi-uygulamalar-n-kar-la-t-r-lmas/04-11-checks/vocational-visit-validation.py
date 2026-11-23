"""Verify the documented federation visit and its open policy outcome."""

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
stem = '0411-saadet-2026-vocational-visit'
package = here/'vocational-visit-draft.json'
review = here/'vocational-visit-review-draft.json'
assert harness.sha(package)=='ff7d63f1d5c831b549129f2a483b1d72474d30a658a885e0d54c2fa82362ed7d'
assert harness.sha(review)=='9bf93cb7b73b2eb79e46b15b437c2a62dbda4929ccf49b1b5adbae40eb78cca5'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']),len(draft['practice_relation']))==(12,12)
assert not draft['practice_closure']
receipt = harness.main(package, review, 'vocational-visit', stem+'-event', stem+'-relation', None,
                       expected_party='saadet', namespace='gsd-0411')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version']==31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_relation','practice_candidate','practice_statement'):
        row = next(r for r in draft[table] if r['id'].startswith(stem))
        assert row in saved[table]
        assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?',(stem+'-event',)).fetchone()[0]=='2026-10-04'
    assert db.execute('SELECT result_finding_id FROM practice_relation WHERE id=?',(stem+'-relation',)).fetchone()[0] is None
    assert {r[0] for r in db.execute('SELECT stage FROM practice_event_evidence WHERE event_id=?',(stem+'-event',))}=={'action'}
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag)==1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    assert all(word in card for word in ('Ankara','4 Ekim','Murat Aydın','ANKA','emeklilik')),view
print('SAADET_VOCATIONAL_VISIT_BOTH_VIEWS_OK',folder,flush=True)
