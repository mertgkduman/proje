"""Verify the seven later oversight records and retain the isolated release."""

import importlib.util
import json
from pathlib import Path
import sqlite3

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('practice_validation', here/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
package = here/'package-fund-late-132-union-draft.json'
review = here/'fund-late-132-union-review-draft.json'
assert harness.sha(package) == 'e46584ce7f19e8cf252658ba741da34211f0174a909d6ab66c3455c2366d3870'
assert harness.sha(review) == 'cdad9cd2eb673db263ded783ea0aa2d56bd43d72f4b34814158ad70ee88fc888'
numbers = ('51273','51538','51802','51946','52059','52440','52493')
stems = [f'0404-tbmm-erken-7-{number}' for number in numbers]
receipt = harness.main(package, review, 'fund-late-v30', stems[0]+'-event', stems[0]+'-relation', None)
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_text())
assert manifest['preview'] and manifest['renderer_version'] == 30
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 139 and len(draft['practice_relation']) == 140
assert not draft['practice_closure']
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for stem in stems:
        for table, suffix in (('practice_event','event'), ('practice_relation','relation')):
            identity = stem+'-'+suffix
            row = next(r for r in draft[table] if r['id']==identity)
            sql = db.execute(f'SELECT * FROM {table} WHERE id=?',(identity,)).fetchone()
            assert row in saved[table] and row == dict(sql)
        assert not db.execute(
            "SELECT 1 FROM practice_event_evidence WHERE event_id=? AND stage='result'",
            (stem+'-event',)).fetchone()
html = (folder/'index.html').read_text()
for row in draft['practice_relation']:
    for view in ('party','comparison'):
        anchor = f'{view}-practice-{row["id"]}'
        assert html.count(f'id="{anchor}"')==1 and f'href="#{anchor}"' in html
print('YENI_PARTI_FUND_LATE_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
