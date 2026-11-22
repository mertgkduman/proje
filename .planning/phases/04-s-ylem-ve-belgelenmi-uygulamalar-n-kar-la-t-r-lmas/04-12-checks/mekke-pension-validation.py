"""Verify the Democratic Party Mekke vote and unrelated pension bill."""

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
stem = '0412-demokrat-2026-mekke'
pension = '0412-demokrat-2026-2-3489'
package = here/'mekke-pension-draft.json'
review = here/'mekke-pension-review-draft.json'
assert harness.sha(package) == '5a276774f05752a94a6857645f66e9d74513c028bab46d36da491b6755a65611'
assert harness.sha(review) == '73975fa3129f792fb0fd4dc8cefecb3c07b3416f4855451c0a01ba0c125ca914'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 8 and len(draft['practice_relation']) == 8
assert not draft['practice_closure']
receipt = harness.main(package, review, 'mekke-pension', stem+'-event', stem+'-relation', None,
                       expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_contribution'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?', (pension+'-event',)).fetchone()
    assert not db.execute(
        "SELECT 1 FROM practice_event_evidence WHERE event_id=? AND stage='result'", (pension+'-event',)).fetchone()
    v=db.execute('SELECT original_path FROM document_version WHERE id=?',
                 ('0412-policy-shared-ballot-v1',)).fetchone()[0]
    assert (harness.SOURCE/v).read_bytes() == (harness.DATA/'practices'/'sources'/'saadet'/v).read_bytes()
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    for anchor, snippets in (
        (f'{view}-practice-{stem}-relation', ('2/3961','277 kabul ve 118 ret','23.49.42')),
        (f'{view}-unmatched-{pension}-candidate', ('2/3489','2.345 gösterge','Araştırma sürüyor')),
    ):
        tag = f'id="{anchor}"'
        assert page.count(tag) == 1 and f'href="#{anchor}"' in page
        card = page.split(tag, 1)[1].split('</article>', 1)[0]
        assert all(word in card for word in snippets)
assert page.count(f'data-finding-id="{stem}-altintas-finding"') == 2
print('DP_MEKKE_PENSION_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
