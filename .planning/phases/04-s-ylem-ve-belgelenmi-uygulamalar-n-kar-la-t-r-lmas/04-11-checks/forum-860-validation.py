"""Verify the 8/60 request and distinct same-day agenda vote."""

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
case = 'forum-860'
stem = '0411-saadet-forum-860'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == '2c72b61440ad6eb2f550c2f1fd8b1f85862292d42db5cebf6bcde1b67424bed4'
assert harness.sha(review) == 'faf1c5af22630fb665fd9ba16c75e62eafe15e3eec77a21e74da4c288ad16038'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (31, 27, 0)
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
    for term in ('8/60','görüşme','gündem'):
        assert term.casefold() in card.casefold(),(view,term)
print('SAADET_FORUM_860_BOTH_VIEWS_OK',folder,flush=True)
