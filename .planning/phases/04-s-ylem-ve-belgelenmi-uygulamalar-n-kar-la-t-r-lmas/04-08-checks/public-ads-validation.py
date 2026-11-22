"""Validate both documented media events in the Yeni Yol work package."""

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
package = here/'public-ads-draft.json'
review = here/'public-ads-review-draft.json'
assert harness.sha(package) == 'd4c47c56e74a6539d80e7d478249e3dbe1f61e322f3c4f7d3221d1e4d6e82fad'
assert harness.sha(review) == '4d6d7da1f362fb34f51a3c5936c23b96e0205c637cb9b367beb895c18f7509ea'
stem = '0408-public-ads-3465'
draft = json.loads(package.read_text())['practice_records']
relation, = (r['id'] for r in draft['practice_relation'])
receipt = harness.main(package, review, 'public-ads', stem+'-event', relation, None,
                       expected_party='yeni-yol', namespace='gsd-0408')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_text())
assert manifest['preview'] and manifest['renderer_version'] == 30
records = json.loads((folder/'records.json').read_text())
assert len(draft['practice_event']) == 3 and not draft['practice_closure']
unmatched = [r for r in draft['practice_candidate'] if r['state']=='unmatched']
assert len(unmatched) == 2
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_relation','practice_candidate','practice_dispute'):
        for row in draft[table]:
            assert row in records[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    for row in unmatched:
        assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(row['event_id'],)).fetchone()
html = (folder/'index.html').read_text()
for row in unmatched:
    for view in ('party','comparison'):
        anchor = f'{view}-unmatched-{row["id"]}'
        tag = f'id="{anchor}"'
        assert html.count(tag)==1 and f'href="#{anchor}"' in html
        card = html.split(tag,1)[1].split('</article>',1)[0]
        assert 'Araştırma sürüyor' in card
        if row['id']==stem+'-candidate':
            assert all(word in card for word in ('10/3465','kabul edilmedi','Gündemde'))
print('YENI_YOL_PUBLIC_ADS_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
