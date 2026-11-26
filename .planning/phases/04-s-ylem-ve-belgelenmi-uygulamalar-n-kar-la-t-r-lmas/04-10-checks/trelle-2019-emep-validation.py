import importlib.util,json,sqlite3,sys
from pathlib import Path
c=Path(__file__).resolve().parent; spec=importlib.util.spec_from_file_location('validation',c.parent/'04-04-checks'/'samsun-reply-validation.py'); h=importlib.util.module_from_spec(spec); spec.loader.exec_module(h); h.HERE=c; h.SOURCE=h.DATA/'practices'/'sources'/'emep'; case='trelle-2019-emep'; p=c/(case+'-draft.json'); r=c/(case+'-review-draft.json')
assert [h.sha(p),h.sha(r)]==sys.argv[1:]; package=json.loads(p.read_bytes()); old=json.loads((h.DATA/'practices/04-emep.json').read_bytes()); oldreview=json.loads((h.DATA/'practices/04-emep-review.json').read_bytes()); newreview=json.loads(r.read_bytes()); rec=package['practice_records']
assert h.sha(h.DATA/'practices/04-emep.json')=='570fd88c8aba0e216dd9e6568f0775421317b210bc6cc6bfbb7fa3be011cfec2'; assert h.sha(h.DATA/'practices/04-emep-review.json')=='8ac039468285698df17517d11d0dcd2613d1b97d63084a6bd739f4f465754645'
assert (len(rec['practice_event']),len(rec['practice_relation']),len(rec['practice_closure']))==(86,80,0)
for table,rows in old['practice_records'].items(): assert all(row in rec[table] for row in rows),table
assert all(row in package['entries'] for row in old['entries']); assert all(row in newreview['practice_source_review'] for row in oldreview['practice_source_review'])
stem='0410-trelle-2019'; receipt=h.main(p,r,case,stem+'-event',stem+'-relation',None,expected_party='emep',namespace='gsd-0410'); folder=Path(receipt['preview']); exported=json.loads((folder/'records.json').read_bytes()); report=(folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table in ('practice_event','practice_relation','practice_statement','practice_candidate','practice_contribution'):
  ident=stem+'-'+table.removeprefix('practice_'); expected=next(v for v in rec[table] if v['id']==ident); assert expected in exported[table] and expected==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone())
 for view in ('party','comparison'):
  anchor=view+'-practice-'+stem+'-relation'; start='id="'+anchor+'"'; assert report.count(start)==1 and 'href="#'+anchor+'"' in report; card=report.split(start,1)[1].split('</article>',1)[0]
  for text in ('Trelleborg','Arzu Erkan'): assert text in card,(view,text)
print('TRELLE2019_EMEP_BOTH_VIEWS_OK',folder,flush=True)
