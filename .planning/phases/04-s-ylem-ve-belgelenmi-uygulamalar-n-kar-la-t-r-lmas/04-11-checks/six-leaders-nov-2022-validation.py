"""Verify both November 2022 events and both reader views."""
import importlib.util,json,sqlite3,sys
from pathlib import Path
checks=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('practice_validation',checks.parent/'04-04-checks'/'samsun-reply-validation.py')
harness=importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
harness.HERE=checks;harness.SOURCE=harness.DATA/'practices'/'sources'/'saadet'
case='six-leaders-nov-2022';stems=('0411-saadet-nov-2022-presentation','0411-saadet-nov-2022-meeting')
package=checks/f'{case}-draft.json';review=checks/f'{case}-review-draft.json'
assert harness.sha(package)=='29efd316a1a23aeef483bae5c8fdec9a45046e3fa2823c58730f1c790dac499d'
assert harness.sha(review)=='5119b532e55b461fdd995ef824614a4bba6d44d78b345303a13c5d14835dfe76'
records=json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(40,36,0)
if len(sys.argv)==2:
 job=sys.argv[1];assert job.isdecimal();receipt=json.loads((checks/f'{case}-{job}.json').read_bytes());assert receipt['package_sha256']==harness.sha(package) and receipt['review_sha256']==harness.sha(review)
else:receipt=harness.main(package,review,case,stems[0]+'-event',stems[0]+'-relation',None,expected_party='saadet',namespace='gsd-0411')
folder=Path(receipt['preview']);manifest=json.loads((folder/'manifest.json').read_bytes());assert manifest['preview'] and manifest['renderer_version']==31
export=json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for stem in stems:
  for table in ('practice_statement','practice_event','practice_relation'):
   row=next(x for x in records[table] if x['id']==stem+'-'+table.removeprefix('practice_'));assert row in export[table];assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
report=(folder/'index.html').read_text()
for stem in stems:
 for view in ('party','comparison'):
  anchor=f'{view}-practice-{stem}-relation';tag=f'id="{anchor}"';assert report.count(tag)==1 and f'href="#{anchor}"' in report
  card=report.split(tag,1)[1].split('</article>',1)[0]
  for term in ('14 Kasım','28 Kasım','altı'):
   assert term.casefold() in card.casefold(),(stem,view,term)
print('SAADET_NOV_2022_BOTH_EVENTS_BOTH_VIEWS_OK',folder,flush=True)
