"""Validate an exact congress package and retain both reader views."""

import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

phase = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'practice_validation', phase / '04-04-checks' / 'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)

variants = {
    'saadet': ('11', '0411-saadet-2024-9-kongre',
               'eb17a7262d09350f0b6fe0ff6d5fe90fdb88e7e84cd0d6b3c9c7d02fe98507ef',
               'dbac70a9b10eb1c0b63654ca868327b4d10eb6a05f76f4d699864797879ede16'),
    'demokrat': ('12', '0412-demokrat-2024-15-kongre',
                 '40ebf114702fd38d27cf414ae5203f44a2a32abd5a0688d18eb0aa8ae80837b8',
                 '3edae7e0a58e422b41a9418a3700ef13b345d2f0579a1b0d7252043bbac46cb1'),
}
party = sys.argv[1]
plan, stem, package_hash, review_hash = variants[party]
here = phase / f'04-{plan}-checks'
harness.HERE = here
harness.SOURCE = harness.DATA / 'practices' / 'sources' / party
package = here / 'congress-institution-draft.json'
review = here / 'congress-institution-review-draft.json'
assert harness.sha(package) == package_hash and harness.sha(review) == review_hash
relation = stem + '-relation'
receipt = harness.main(package, review, 'congress-institution', stem + '-event', relation, None,
                       expected_party=party, namespace=f'gsd-04{plan}')

folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_text())
assert manifest['preview'] and manifest['renderer_version'] == 29
records = json.loads((folder / 'records.json').read_text())
draft = json.loads(package.read_text())['practice_records']
assert not draft['practice_closure']
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_statement', 'practice_dispute'):
        for row in draft[table]:
            saved = db.execute('SELECT * FROM ' + table + ' WHERE id=?', (row['id'],)).fetchone()
            assert saved is not None and row == dict(saved) and row in records[table]
html = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{relation}'
    assert html.count(f'id="{anchor}"') == 1 and f'href="#{anchor}"' in html
for suffix in ('statement-quote', 'result'):
    assert html.count(f'data-finding-id="{stem}-{suffix}"') == 2
for row in draft['practice_dispute']:
    assert html.count(f'data-finding-id="{row["summary_finding_id"]}"') == 2
print('CONGRESS_DB_JSON_BOTH_VIEWS_OK', party, folder, flush=True)
