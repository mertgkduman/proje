import json,sqlite3,sys
from pathlib import Path
c=Path(__file__).resolve().parent;receipt=json.loads((c/('halic-2022-emep-'+sys.argv[1]+'.json')).read_text());folder=Path(receipt['preview']);old=json.loads(Path('data/practices/04-emep.json').read_text())['practice_records'];new=json.loads((c/'halic-2022-emep-draft.json').read_text())['practice_records'];export=json.loads((folder/'records.json').read_text());html=(folder/'index.html').read_text();assert (len(old['practice_event']),len(old['practice_relation']))==(82,78)
counts={}
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table,rows in old.items():
  for row in rows:
   assert row in new[table] and row in export[table],(table,row)
   cols=list(row);sql='SELECT '+','.join('"'+x+'"' for x in cols)+' FROM "'+table+'" WHERE '+' AND '.join('"'+x+'" IS ?' for x in cols)
   assert db.execute(sql,tuple(row[x] for x in cols)).fetchone() is not None,(table,row)
  counts[table]=len(rows)
 for table,suffix in [('practice_event','event'),('practice_relation','relation'),('practice_statement','statement'),('practice_candidate','candidate'),('practice_contribution','contribution')]:
  ident='0410-halic-2022-'+suffix;expected=next(row for row in new[table] if row['id']==ident)
  assert expected in export[table] and expected==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone())
 for view in ('party','comparison'):
  anchor=view+'-practice-0410-halic-2022-relation';assert html.count('id="'+anchor+'"')==1 and 'href="#'+anchor+'"' in html
print('HALIC2022_EMEP_INDEPENDENT_APPEND_ONLY_OK',json.dumps(counts,sort_keys=True),flush=True)
