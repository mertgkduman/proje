import json,sqlite3,sys,subprocess
from pathlib import Path
c=Path(__file__).resolve().parent
case=sys.argv[2] if len(sys.argv)>2 else 'idlib-2020-emep'
assert case in {'idlib-2020-emep','idlib-2020-emep-v2'}
receipt=json.loads((c/(case+'-'+sys.argv[1]+'.json')).read_text()); folder=Path(receipt['preview']); old_package=json.loads(subprocess.check_output(['git','show','982023d1:data/practices/04-emep.json'])); old_review=json.loads(subprocess.check_output(['git','show','982023d1:data/practices/04-emep-review.json'])); new_package=json.loads((c/f'{case}-draft.json').read_bytes()); new_review=json.loads((c/f'{case}-review-draft.json').read_bytes()); old=old_package['practice_records']; new=new_package['practice_records']; exported=json.loads((folder/'records.json').read_bytes()); html=(folder/'index.html').read_text(); stem='0410-idlib-2020'; counts={}
assert (len(old['practice_event']),len(old['practice_relation']))==(86,80); assert (len(new['practice_event']),len(new['practice_relation']),len(new['practice_closure']))==(87,81,0); assert all(row in new_package['entries'] for row in old_package['entries']); assert all(row in new_review['practice_source_review'] for row in old_review['practice_source_review'])
event=next(x for x in new['practice_event'] if x['id']==stem+'-event'); assert (event['common_event_key'],event['event_at'],event['date_precision'])==('idlib-2020-03-05-moskova-ek-protokol','2020-03-05','day')
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table,rows in old.items():
  for row in rows:
   assert row in new[table] and row in exported[table],(table,row); cols=list(row); sql='SELECT '+','.join('"'+x+'"' for x in cols)+' FROM "'+table+'" WHERE '+' AND '.join('"'+x+'" IS ?' for x in cols); assert db.execute(sql,tuple(row[x] for x in cols)).fetchone() is not None,(table,row)
  counts[table]=len(rows)
 for table in ('practice_event','practice_statement','practice_relation','practice_candidate'):
  ident=stem+'-'+table.removeprefix('practice_'); row=next(x for x in new[table] if x['id']==ident); assert row in exported[table] and row==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone())
 for view in ('party','comparison'):
  anchor=view+'-practice-'+stem+'-relation'; assert html.count('id="'+anchor+'"')==1 and 'href="#'+anchor+'"' in html
print('IDLIB2020_EMEP_INDEPENDENT_APPEND_ONLY_OK',json.dumps(counts,sort_keys=True),flush=True)
