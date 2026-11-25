import json,sqlite3,sys,subprocess
from pathlib import Path
c=Path(__file__).resolve().parent;receipt=json.loads((c/('joint-2020-dbp-v2-'+sys.argv[1]+'.json')).read_text());folder=Path(receipt['preview']);old=json.loads(subprocess.check_output(['git','show','ff71e587:data/practices/04-dbp.json']))['practice_records'];new=json.loads((c/'joint-2020-dbp-v2-draft.json').read_text())['practice_records'];export=json.loads((folder/'records.json').read_text());html=(folder/'index.html').read_text();assert (len(old['practice_event']),len(old['practice_relation']))==(67,7)
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
  ident='0409-joint-2020-dbp-'+suffix;expected=next(row for row in new[table] if row['id']==ident);assert expected in export[table] and expected==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone())
 assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',('0409-joint-2020-dbp-event',)).fetchone()
 for view in ('party','comparison'):
  anchor=view+'-unmatched-0409-joint-2020-dbp-unmatched';assert html.count('id="'+anchor+'"')==1 and 'href="#'+anchor+'"' in html
print('JOINT2020_DBP_INDEPENDENT_APPEND_ONLY_OK',json.dumps(counts,sort_keys=True),flush=True)
