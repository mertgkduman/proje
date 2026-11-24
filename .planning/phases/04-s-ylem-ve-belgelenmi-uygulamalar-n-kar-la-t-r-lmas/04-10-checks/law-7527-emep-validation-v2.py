import importlib.util,json,sqlite3,sys
from pathlib import Path
checks=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('validation',checks.parent/'04-04-checks'/'samsun-reply-validation.py'); h=importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
h.HERE=checks; h.SOURCE=h.DATA/'practices'/'sources'/'emep'; case='law-7527-emep'; p=checks/(case+'-draft-v2.json'); r=checks/(case+'-review-draft-v2.json')
assert [h.sha(p),h.sha(r)]==sys.argv[1:]; package=json.loads(p.read_bytes()); old=json.loads((h.DATA/'practices/04-emep.json').read_bytes()); oldreview=json.loads((h.DATA/'practices/04-emep-review.json').read_bytes()); newreview=json.loads(r.read_bytes()); rec=package['practice_records']
assert (len(old['practice_records']['practice_event']),len(old['practice_records']['practice_relation']))==(79,76)
assert (len(rec['practice_event']),len(rec['practice_relation']),len(rec['practice_closure']))==(80,77,0)
for table,rows in old['practice_records'].items(): assert all(row in rec[table] for row in rows),table
assert all(row in package['entries'] for row in old['entries']); assert all(row in newreview['practice_source_review'] for row in oldreview['practice_source_review'])
receipt=h.main(p,r,case,'0410-law-7527-emep-event','0410-law-7527-emep-relation',None,expected_party='emep',namespace='gsd-0410'); folder=Path(receipt['preview']); exported=json.loads((folder/'records.json').read_bytes()); report=(folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table,ident in [('practice_event','0410-law-7527-emep-event'),('practice_relation','0410-law-7527-emep-relation'),('practice_statement','0410-law-7527-emep-statement'),('practice_candidate','0410-law-7527-emep-candidate')]:
  expected=next(v for v in rec[table] if v['id']==ident); assert expected in exported[table] and expected==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone())
 for view in ('party','comparison'):
  anchor=view+'-practice-0410-law-7527-emep-relation'; start='id="'+anchor+'"'; assert report.count(start)==1 and 'href="#'+anchor+'"' in report; card=report.split(start,1)[1].split('</article>',1)[0]
  for text in ('18 Temmuz','30 Temmuz','7527','Karaca','273','275'): assert text in card,(view,text)
print('LAW7527_EMEP_BOTH_VIEWS_OK',folder,flush=True)
