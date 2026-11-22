"""Verify the Bağlar CEMR approval and the distinct later signature record."""

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
stem = '0409-dbp-baglar-2015-cemr'
package = here/'baglar-cemr-draft.json'
review = here/'baglar-cemr-review-draft.json'
assert harness.sha(package) == '8a552b357e8f0849a8abbeb4a133eb5cabb646dbc2c9be09322393b90814d9bb'
assert harness.sha(review) == '1132f2eadc59d655fcf3b7679b82fc94248d6af5a6e8fa7247a9126e5497897b'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 10 and len(draft['practice_relation']) == 7
assert not draft['practice_closure']
receipt = harness.main(package, review, 'baglar-cemr', stem+'-event',
                       stem+'-relation', None, expected_party='dbp', namespace='gsd-0409')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_statement'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    assert [row[0] for row in db.execute(
        "SELECT passage_id FROM practice_event_evidence WHERE event_id=? AND stage='result'",
        (stem+'-event',))] == ['0409-cemr-baglar-approval']
    assert '01.10.2024' in db.execute("SELECT exact FROM passage WHERE id='0409-cemr-tbb-signature'").fetchone()[0]
    assert not db.execute('SELECT 1 FROM practice_contribution WHERE event_id=?', (stem+'-event',)).fetchone()
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    assert all(word in card for word in ('2015/48','oybirliğiyle','1 Ekim 2024','Birsen Kaya Akat'))
print('DBP_CEMR_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
