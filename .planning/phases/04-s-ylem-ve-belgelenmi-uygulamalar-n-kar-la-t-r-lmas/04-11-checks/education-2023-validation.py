"""Verify Atmaca speech and the 2/2691 final vote."""

import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', checks.parent / '04-04-checks' / 'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'saadet'
case = 'education-2023'
stem = '0411-saadet-education-2023'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == '4dc52f051576cdc4f2eab0bec4361569eb3e172572757e655c5c852f86b6e74f'
assert harness.sha(review) == 'cd17be98c22acb24f1ed778e3d4869a31bd661c96524ef6a4718a80fbcb15f31'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (37, 33, 0)
if len(sys.argv)==2:
    job=sys.argv[1]; assert job.isdecimal()
    receipt=json.loads((checks/f'{case}-{job}.json').read_bytes())
    assert receipt['package_sha256']==harness.sha(package) and receipt['review_sha256']==harness.sha(review)
else:
    receipt=harness.main(package,review,case,stem+'-event',stem+'-relation',None,expected_party='saadet',namespace='gsd-0411')
folder=Path(receipt['preview']); manifest=json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version']==31
export=json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    for table in ('practice_statement','practice_event','practice_relation'):
        row=next(x for x in records[table] if x['id']==stem+'-'+table.removeprefix('practice_'))
        assert row in export[table]
        assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
report=(folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor=f'{view}-practice-{stem}-relation'; tag=f'id="{anchor}"'
    assert report.count(tag)==1 and f'href="#{anchor}"' in report
    card=report.split(tag,1)[1].split('</article>',1)[0]
    for term in ('22 Şubat','30 Mart','3 Nisan','uzaktan'):
        assert term.casefold() in card.casefold(),(view,term)
print('SAADET_EDUCATION_2023_BOTH_VIEWS_OK',folder,flush=True)
