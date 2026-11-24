import importlib.util, json, sqlite3
from pathlib import Path
checks=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('validation',checks.parent/'04-04-checks'/'samsun-reply-validation.py')
h=importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
h.HERE=checks; h.SOURCE=h.DATA/'practices'/'sources'/'emep'
p=checks/'ayasofya-2020-union-draft.json'; r=checks/'ayasofya-2020-union-review-draft.json'
assert h.sha(p)=='9eba464c4e4e637ffb3b49cf3edee6b9fb0d03eee0225a4ed51c2ab879028ed6'
assert h.sha(r)=='f84ed681926440805bf7abf9f3da3cf53b57b190b685eaf958b061c12380c3ee'
draft=json.loads(p.read_bytes()); old=json.loads((h.DATA/'practices/04-emep.json').read_bytes()); oldreview=json.loads((h.DATA/'practices/04-emep-review.json').read_bytes()); review=json.loads(r.read_bytes())
assert (len(old['practice_records']['practice_event']),len(old['practice_records']['practice_relation']))==(69,71)
for table,rows in old['practice_records'].items():
 assert all(row in draft['practice_records'][table] for row in rows),table
assert all(row in draft['entries'] for row in old['entries'])
assert all(row in review['practice_source_review'] for row in oldreview['practice_source_review'])
receipt=h.main(p,r,'ayasofya-2020','0410-ayasofya-2020-court-event','0410-youth9-conference-relation',None,expected_party='emep',namespace='gsd-0410')
folder=Path(receipt['preview']); snapshot=json.loads((folder/'records.json').read_bytes()); report=(folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for ident in ('court','gazette','opening'):
  eid='0410-ayasofya-2020-'+ident+'-event'; cid='0410-ayasofya-2020-'+ident+'-candidate'
  for table,key in (('practice_event',eid),('practice_candidate',cid)):
   row=next(x for x in draft['practice_records'][table] if x['id']==key)
   assert row in snapshot[table] and row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(key,)).fetchone())
  assert tuple(db.execute('SELECT state,relation_id FROM practice_candidate WHERE id=?',(cid,)).fetchone())==('unmatched',None)
  for view in ('party','comparison'):
   anchor=f'{view}-unmatched-{cid}'; assert report.count(f'id="{anchor}"')==1 and f'href="#{anchor}"' in report
assert (len(draft['practice_records']['practice_event']),len(draft['practice_records']['practice_relation']))==(72,71)
print('AYASOFYA_3_UNMATCHED_BOTH_VIEWS_OK',folder,flush=True)
