"""Verify Kocasinan congress and the documented incumbent result."""

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
scope = 'kocasinan-provenance'
stem = '0411-saadet-2026-kocasinan-kongre'
event = stem+'-event'
candidate = stem+'-unmatched'
package = here/f'{scope}-draft.json'
review = here/f'{scope}-review-draft.json'
assert harness.sha(package) == '9be38e0268be7749dbb9ef0e22c1b27ccbb7d6a8a78772fff5a0fae82ead7d1a'
assert harness.sha(review) == 'f494e8357baaaa0d63690c4a3c26263bb28509fa203af6ac3e115e96095b0611'
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (14, 12)
assert not draft['practice_closure']
receipt = harness.main(package,review,scope,event,'0411-saadet-2026-vocational-visit-relation',
                       None,expected_party='saadet',namespace='gsd-0411')
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
    basis = db.execute('SELECT occurrence_basis FROM practice_event WHERE id=?',(event,)).fetchone()[0]
    assert basis == '28 Ağustos tarihli Kayseri Haber kongre programı ve 29 Ağustos tarihli Kayseri Haber ile Talas Express Haber aktarımları.'
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?',(event,)).fetchone()[0] == '2026-08-28'
    assert db.execute('SELECT state FROM practice_candidate WHERE id=?',(candidate,)).fetchone()[0] == 'unmatched'
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(event,)).fetchone()
    evidence = dict(db.execute('SELECT passage_id,stage FROM practice_event_evidence WHERE event_id=?',(event,)))
    for key, stage in [('plan-day','initiative'),('talas-occurred','action'),('talas-election','result'),('kayseri-election','result')]:
        assert evidence['0411-kocasinan-congress-'+key] == stage
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor = f'{view}-unmatched-{candidate}'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    for expected in ('Kocasinan','Selçuk Onat','28 Ağustos','8. Olağan'):
        assert expected in card,(view,expected)
print('SAADET_KOCASINAN_PROVENANCE_BOTH_VIEWS_OK',folder,flush=True)
