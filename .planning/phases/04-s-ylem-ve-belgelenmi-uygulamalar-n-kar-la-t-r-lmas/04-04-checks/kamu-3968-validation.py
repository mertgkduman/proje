"""Verify the 2/3968 filing, and preserve the open statement and legislative result."""

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
harness.SOURCE = harness.DATA/'practices'/'sources'/'yeni-parti'
stem = '0404-yeni-parti-2026-2-3968'
event = stem+'-event'
candidate = stem+'-unmatched'
package = here/'kamu-3968-draft.json'
review = here/'kamu-3968-review-draft.json'
assert harness.sha(package) == '05339c59954ea7a213cf06c10920249443fc5b31061511f1b14c398a877b7c9e'
assert harness.sha(review) == '9c551a5082b3c36f69687e31087631c6cca0d279119de74172defcfcbb22e4c0'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 141 and len(draft['practice_relation']) == 141
assert not draft['practice_closure']
receipt = harness.main(package, review, 'kamu-3968', event,
                       '0404-fon-komisyon-1014-relation', None,
                       expected_party='yeni-parti', namespace='gsd-0404')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_text())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_contribution'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?', (event,)).fetchone()[0] == '2026-10-21'
    assert db.execute('SELECT state FROM practice_candidate WHERE id=?', (candidate,)).fetchone()[0] == 'unmatched'
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?', (event,)).fetchone()
    assert {row[0] for row in db.execute('SELECT stage FROM practice_event_evidence WHERE event_id=?', (event,))} == {'initiative', 'action'}
    assert db.execute('SELECT contribution_kind FROM practice_contribution WHERE id=?',
                      (stem+'-contribution',)).fetchone()[0] == 'task'
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-unmatched-{candidate}'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag,1)[1].split('</article>',1)[0]
    assert all(text in card for text in ('2/3968', 'aynı kapsamdaki parti söylemi', 'azami emeklilik ikramiyesi', 'Günaydın', 'Komisyonda'))
print('YENI_PARTI_3968_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
