import importlib.util,json,sqlite3
from pathlib import Path
here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('harness',here.parent/'04-04-checks'/'samsun-reply-validation.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.HERE=here;h.SOURCE=h.DATA/'practices'/'sources'/'dbp'
case='baglar-2016-reports';stem='0409-baglar-2016-reports-';package=here/(case+'-draft.json');review=here/(case+'-review-draft.json')
assert h.sha(package)=='db451e12baa2c6670c1fc074b9150339d5f109a233415bdd86886adf6dd11222'
assert h.sha(review)=='43fd373990be7a923d8b71992d8233cf9871a82679c5d5bc81ac477d9fe3f331'
draft=json.loads(package.read_bytes())['practice_records'];assert (len(draft['practice_event']),len(draft['practice_relation']),len(draft['practice_closure']))==(66,7,0)
r=h.main(package,review,case,stem+'20-event','0409-dbp-baglar-2015-cemr-relation',None,expected_party='dbp',namespace='gsd-0409')
folder=Path(r['preview']);saved=json.loads((folder/'records.json').read_bytes());page=(folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table in ('practice_event','practice_relation','practice_candidate'):
  for row in draft[table]:assert row in saved[table] and row==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(row['id'],)).fetchone())
 for n in ('18','20'):assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(stem+n+'-event',)).fetchone()
for view in ('party','comparison'):
 for n,word in [('18','gıda'),('20','Kardelen')]:
  tag='id="'+view+'-unmatched-'+stem+n+'-unmatched"';assert page.count(tag)==1
  assert word.lower() in page.split(tag,1)[1].split('</article>',1)[0].lower()
print('DBP2016_REPORTS_BOTH_VIEWS_OK',folder,flush=True)
