import json,sqlite3,sys,subprocess
from pathlib import Path
c=Path(__file__).resolve().parent; receipt=json.loads((c/('trelle-2019-emep-'+sys.argv[1]+'.json')).read_text()); folder=Path(receipt['preview']); old_package=json.loads(subprocess.check_output(['git','show','5743af62:data/practices/04-emep.json'])); old_review=json.loads(subprocess.check_output(['git','show','5743af62:data/practices/04-emep-review.json'])); new_package=json.loads((c/'trelle-2019-emep-draft.json').read_bytes()); new_review=json.loads((c/'trelle-2019-emep-review-draft.json').read_bytes()); old=old_package['practice_records']; new=new_package['practice_records']; exported=json.loads((folder/'records.json').read_bytes()); html=(folder/'index.html').read_text(); stem='0410-trelle-2019'; counts={}
assert (len(old['practice_event']),len(old['practice_relation']))==(85,79); assert (len(new['practice_event']),len(new['practice_relation']),len(new['practice_closure']))==(86,80,0)
assert all(row in new_package['entries'] for row in old_package['entries']); assert all(row in new_review['practice_source_review'] for row in old_review['practice_source_review'])
event=next(x for x in new['practice_event'] if x['id']==stem+'-event'); assert event['event_at'] is None and event['date_precision']=='unknown' and '31 Aralık 2019' in event['date_unknown_reason'] and '1 Ocak 2020' in event['date_unknown_reason']
statement=next(x for x in new['practice_statement'] if x['id']==stem+'-statement'); assert statement['statement_at'] is None and statement['date_precision']=='unknown'
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table,rows in old.items():
  for row in rows:
   assert row in new[table] and row in exported[table],(table,row); cols=list(row); sql='SELECT '+','.join('"'+x+'"' for x in cols)+' FROM "'+table+'" WHERE '+' AND '.join('"'+x+'" IS ?' for x in cols); assert db.execute(sql,tuple(row[x] for x in cols)).fetchone() is not None,(table,row)
  counts[table]=len(rows)
 for table in ('practice_event','practice_statement','practice_relation','practice_candidate','practice_contribution'):
  ident=stem+'-'+table.removeprefix('practice_'); row=next(x for x in new[table] if x['id']==ident); assert row in exported[table] and row==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone())
 for view in ('party','comparison'):
  anchor=view+'-practice-'+stem+'-relation'; assert html.count('id="'+anchor+'"')==1 and 'href="#'+anchor+'"' in html
print('TRELLE2019_EMEP_INDEPENDENT_APPEND_ONLY_OK',json.dumps(counts,sort_keys=True),flush=True)
