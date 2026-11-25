import json,sqlite3,sys
from pathlib import Path
c=Path(__file__).resolve().parent;receipt=json.loads((c/('joint-2020-emep-'+sys.argv[1]+'.json')).read_text());folder=Path(receipt['preview']);old=json.loads(Path('data/practices/04-emep.json').read_text())['practice_records'];new=json.loads((c/'joint-2020-emep-draft.json').read_text())['practice_records'];export=json.loads((folder/'records.json').read_text());html=(folder/'index.html').read_text();assert (len(old['practice_event']),len(old['practice_relation']))==(83,79)
counts={}
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table,rows in old.items():
  for row in rows:
   assert row in new[table] and row in export[table],(table,row)
   cols=list(row);sql='SELECT '+','.join('"'+x+'"' for x in cols)+' FROM "'+table+'" WHERE '+' AND '.join('"'+x+'" IS ?' for x in cols)
   assert db.execute(sql,tuple(row[x] for x in cols)).fetchone() is not None,(table,row)
  counts[table]=len(rows)
 for table,suffix in [('practice_event','event'),('practice_candidate','unmatched'),('practice_contribution','contribution')]:
  ident='0410-joint-2020-emep-'+suffix;expected=next(row for row in new[table] if row['id']==ident);assert expected in export[table] and expected==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone())
 assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',('0410-joint-2020-emep-event',)).fetchone()
 for view in ('party','comparison'):
  anchor=view+'-unmatched-0410-joint-2020-emep-unmatched';assert html.count('id="'+anchor+'"')==1 and 'href="#'+anchor+'"' in html
print('JOINT2020_EMEP_INDEPENDENT_APPEND_ONLY_OK',json.dumps(counts,sort_keys=True),flush=True)
