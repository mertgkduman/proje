import importlib.util,json,sqlite3,sys
from pathlib import Path
c=Path(__file__).resolve().parent; spec=importlib.util.spec_from_file_location('validation',c.parent/'04-04-checks'/'samsun-reply-validation.py'); h=importlib.util.module_from_spec(spec); spec.loader.exec_module(h); h.HERE=c; h.SOURCE=h.DATA/'practices'/'sources'/'emep'; case='idlib-2020-emep'; p=c/(case+'-draft.json'); r=c/(case+'-review-draft.json')
assert [h.sha(p),h.sha(r)]==sys.argv[1:]; package=json.loads(p.read_bytes()); old=json.loads((h.DATA/'practices/04-emep.json').read_bytes()); oldreview=json.loads((h.DATA/'practices/04-emep-review.json').read_bytes()); newreview=json.loads(r.read_bytes()); rec=package['practice_records']
assert h.sha(h.DATA/'practices/04-emep.json')=='284da1e60fbc9b81271abbf79d41e551ace5337d9f32ced8b61cbdf81a25c874'; assert h.sha(h.DATA/'practices/04-emep-review.json')=='6e2e3efb418e164a1af33f27008f1bd6681e2b15b2802db5726717e4ee025f53'; assert (len(rec['practice_event']),len(rec['practice_relation']),len(rec['practice_closure']))==(87,81,0)
for table,rows in old['practice_records'].items(): assert all(row in rec[table] for row in rows),table
assert all(row in package['entries'] for row in old['entries']); assert all(row in newreview['practice_source_review'] for row in oldreview['practice_source_review'])
tip_path=c.parent/'04-05-checks'/'tip-2020-policy-draft.json'; assert h.sha(tip_path)=='56f351d7e0537d7640533392784c6408ac449c433637bc3657864d2a9a28083f'; tip=json.loads(tip_path.read_bytes()); key='idlib-2020-03-05-moskova-ek-protokol'; x=next(v for v in rec['practice_event'] if v.get('common_event_key')==key); y=next(v for v in tip['practice_records']['practice_event'] if v.get('common_event_key')==key); assert {k:v for k,v in x.items() if k!='id'}=={k:v for k,v in y.items() if k!='id'}
find=lambda pkg,kind,ident:next(e['values'] for e in pkg['entries'] if e['kind']==kind and e['values'].get('id')==ident)
a=find(package,'passage','0410-idlib-2020-bm-signature'); b=find(tip,'passage','0405-tip-2020-policy-idlib-signature'); assert (a['exact'],a['pdf_page_index'],a['printed_page'])==(b['exact'],b['pdf_page_index'],b['printed_page'])==('Done in Moscow on 5 March, 2020',1,'2'); assert find(package,'document_version',a['version_id'])['sha256']==find(tip,'document_version',b['version_id'])['sha256']=='041fbaf925821e6ca8b9397167017e5bcd5dd3da695159daec66ed0ef9aac92d'
stem='0410-idlib-2020'; receipt=h.main(p,r,case,stem+'-event',stem+'-relation',None,expected_party='emep',namespace='gsd-0410'); folder=Path(receipt['preview']); exported=json.loads((folder/'records.json').read_bytes()); report=(folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table in ('practice_event','practice_relation','practice_statement','practice_candidate'):
  ident=stem+'-'+table.removeprefix('practice_'); expected=next(v for v in rec[table] if v['id']==ident); assert expected in exported[table] and expected==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone())
 for view in ('party','comparison'):
  anchor=view+'-practice-'+stem+'-relation'; start='id="'+anchor+'"'; assert report.count(start)==1 and 'href="#'+anchor+'"' in report; card=report.split(start,1)[1].split('</article>',1)[0]
  for text in ('İdlib','protokol'): assert text in card,(view,text)
print('IDLIB2020_EMEP_BOTH_VIEWS_OK',folder,flush=True)
