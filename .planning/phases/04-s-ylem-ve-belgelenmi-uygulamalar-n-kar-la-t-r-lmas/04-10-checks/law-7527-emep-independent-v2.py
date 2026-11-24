import json,sqlite3,sys
from pathlib import Path
checks=Path(__file__).resolve().parent; receipt=json.loads((checks/('law-7527-emep-'+sys.argv[1]+'.json')).read_text()); folder=Path(receipt['preview']); old=json.loads(Path('data/practices/04-emep.json').read_text()); new=json.loads((checks/'law-7527-emep-draft-v2.json').read_text()); exported=json.loads((folder/'records.json').read_text()); report=(folder/'index.html').read_text()
assert (len(old['practice_records']['practice_event']),len(old['practice_records']['practice_relation']))==(79,76)
counts={}
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table,rows in old['practice_records'].items():
  for row in rows:
   assert row in new['practice_records'][table] and row in exported[table],(table,row)
   cols=list(row); sql='SELECT '+','.join('"'+c+'"' for c in cols)+' FROM "'+table+'" WHERE '+' AND '.join('"'+c+'" IS ?' for c in cols)
   assert db.execute(sql,tuple(row[c] for c in cols)).fetchone() is not None,(table,row)
  counts[table]=len(rows)
 for table,ident in [('practice_event','0410-law-7527-emep-event'),('practice_relation','0410-law-7527-emep-relation'),('practice_statement','0410-law-7527-emep-statement'),('practice_candidate','0410-law-7527-emep-candidate')]:
  expected=next(r for r in new['practice_records'][table] if r['id']==ident); assert expected in exported[table] and expected==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone())
 assert db.execute('SELECT COUNT(*) FROM practice_event WHERE id=?',('0410-law-7527-emep-event',)).fetchone()[0]==1
 assert db.execute('SELECT COUNT(*) FROM practice_relation WHERE id=?',('0410-law-7527-emep-relation',)).fetchone()[0]==1
 for view in ('party','comparison'):
  anchor=view+'-practice-0410-law-7527-emep-relation'; assert report.count('id="'+anchor+'"')==1 and 'href="#'+anchor+'"' in report
print('LAW7527_EMEP_INDEPENDENT_APPEND_ONLY_OK',json.dumps(counts,sort_keys=True),flush=True)
