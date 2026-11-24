import json, sqlite3, sys
from pathlib import Path
checks=Path(__file__).resolve().parent
receipt=json.loads((checks/('ayasofya-2020-'+sys.argv[1]+'.json')).read_text())
folder=Path(receipt['preview']); new=json.loads((checks/'ayasofya-2020-union-draft.json').read_text()); old=json.loads(Path('data/practices/04-emep.json').read_text()); exported=json.loads((folder/'records.json').read_text()); report=(folder/'index.html').read_text()
assert (len(old['practice_records']['practice_event']),len(old['practice_records']['practice_relation']))==(69,71)
counts={}
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table,rows in old['practice_records'].items():
  for row in rows:
   assert row in new['practice_records'][table] and row in exported[table],(table,row)
   columns=list(row); sql='SELECT '+','.join('"'+c+'"' for c in columns)+' FROM "'+table+'" WHERE '+ ' AND '.join('"'+c+'" IS ?' for c in columns)
   assert db.execute(sql,tuple(row[c] for c in columns)).fetchone() is not None,(table,row)
  counts[table]=len(rows)
 for i in ('court','gazette','opening'):
  eid='0410-ayasofya-2020-'+i+'-event'; cid='0410-ayasofya-2020-'+i+'-candidate'
  assert db.execute('select count(*) from practice_event where id=?',(eid,)).fetchone()[0]==1
  assert tuple(db.execute('select state,relation_id from practice_candidate where id=?',(cid,)).fetchone())==('unmatched',None)
  assert db.execute('select count(*) from practice_relation where event_id=?',(eid,)).fetchone()[0]==0
  for view in ('party','comparison'):
   anchor=f'{view}-unmatched-{cid}'; assert report.count(f'id="{anchor}"')==1 and f'href="#{anchor}"' in report
print('AYASOFYA_INDEPENDENT_APPEND_ONLY_OK',json.dumps(counts,sort_keys=True),flush=True)
