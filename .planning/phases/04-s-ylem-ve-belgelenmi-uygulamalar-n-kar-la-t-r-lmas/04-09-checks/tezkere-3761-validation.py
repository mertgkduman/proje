"""Verify each independent party package for the same 3/761 event."""

import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

phase = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'practice_validation', phase/'04-04-checks'/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
cases = {
    'dbp': ('09', 'Keskin Bayındır', '19.33.58', 5, 3,
        'e32f94f3a9100e4dd05c02b9c7f253212ffefe1d9873479fd226fa0b943c5694',
        'cdf97cb61ea811a1e579898d26f6c599bdd42f574ba4ec7e1bce30abcc46cf5d'),
    'demokrat': ('12', 'Cemal Enginyurt', '19.33.47', 6, 7,
        '8212b58af35d79a0242ac08d83d8828d2eb7c5c6569dd3933c617935f85429a8',
        'a80ddba90da67f14c75600d1adf805c92f4cebd798a9f3ab7da390320e871b7b'),
}
party = sys.argv[1]
plan, name, clock, events, relations, package_hash, review_hash = cases[party]
here = phase/f'04-{plan}-checks'
harness.HERE = here
harness.SOURCE = harness.DATA/'practices'/'sources'/party
stem = f'04{plan}-{party}-2023-3-761'
package = here/'tezkere-3761-draft.json'
review = here/'tezkere-3761-review-draft.json'
assert (harness.sha(package), harness.sha(review)) == (package_hash, review_hash)
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation'])) == (events, relations)
assert not draft['practice_closure']
receipt = harness.main(package, review, 'tezkere-3761', stem+'-event', stem+'-relation', None,
                       expected_party=party, namespace=f'gsd-04{plan}')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_contribution', 'practice_dispute'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    event = db.execute('SELECT event_at, common_event_key FROM practice_event WHERE id=?', (stem+'-event',)).fetchone()
    assert tuple(event) == ('2023-10-17', 'tbmm-28-2-008-3-761-tezkere')
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    for value in ('353 kabul', '163 ret', '357 kabul', '164 ret', 'Mustafa Oğuz', clock, name):
        assert value in card, (view, value)
    assert f'data-finding-id="{stem}-speech-finding"' in card
print('TEZKERE_DB_JSON_BOTH_VIEWS_OK', party, folder, flush=True)
