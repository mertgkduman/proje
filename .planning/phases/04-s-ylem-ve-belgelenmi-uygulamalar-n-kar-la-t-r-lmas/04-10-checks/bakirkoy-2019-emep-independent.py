import json,sqlite3,sys,subprocess
from pathlib import Path
c=Path(__file__).resolve().parent;receipt=json.loads((c/('bakirkoy-2019-emep-'+sys.argv[1]+'.json')).read_text());folder=Path(receipt['preview']);old=json.loads(subprocess.check_output(['git','show','9b5f829d:data/practices/04-emep.json']))['practice_records'];new=json.loads((c/'bakirkoy-2019-emep-draft.json').read_text())['practice_records'];export=json.loads((folder/'records.json').read_text());html=(folder/'index.html').read_text();assert (len(old['practice_event']),len(old['practice_relation']))==(84,79)
counts={}
old_package=json.loads(subprocess.check_output(['git','show','9b5f829d:data/practices/04-emep.json']))
old_review=json.loads(subprocess.check_output(['git','show','9b5f829d:data/practices/04-emep-review.json']))
new_package=json.loads((c/'bakirkoy-2019-emep-draft.json').read_text())
new_review=json.loads((c/'bakirkoy-2019-emep-review-draft.json').read_text())
assert all(row in new_package['entries'] for row in old_package['entries'])
assert all(row in new_review['practice_source_review'] for row in old_review['practice_source_review'])
event=next(row for row in new['practice_event'] if row['id']=='0410-bakirkoy-2019-emep-event')
assert (event['common_event_key'],event['event_at'],event['date_precision'],event['date_unknown_reason'],event['title'],event['scope_context'],event['occurrence_basis']) == ('bakirkoy-2019-12-08-insanca-yasamak-istiyoruz','2019-12-08','day',None,'Bakırköy’de İnsanca Yaşamak İstiyoruz mitingi','8 Aralık 2019’da İstanbul Bakırköy Halk Pazarı’nda düzenlenen İnsanca Yaşamak İstiyoruz mitingi.','TMMOB Harita ve Kadastro Mühendisleri Odası İstanbul Şubesinin 25. Dönem Çalışma Raporu, PDF sayfa indeksi 99.')
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table,rows in old.items():
  for row in rows:
   assert row in new[table] and row in export[table],(table,row)
   cols=list(row);sql='SELECT '+','.join('"'+x+'"' for x in cols)+' FROM "'+table+'" WHERE '+' AND '.join('"'+x+'" IS ?' for x in cols)
   assert db.execute(sql,tuple(row[x] for x in cols)).fetchone() is not None,(table,row)
  counts[table]=len(rows)
 for table,suffix in [('practice_event','event'),('practice_candidate','unmatched'),('practice_contribution','contribution')]:
  ident='0410-bakirkoy-2019-emep-'+suffix;expected=next(row for row in new[table] if row['id']==ident);assert expected in export[table] and expected==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone())
 assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',('0410-bakirkoy-2019-emep-event',)).fetchone()
 for view in ('party','comparison'):
  anchor=view+'-unmatched-0410-bakirkoy-2019-emep-unmatched';assert html.count('id="'+anchor+'"')==1 and 'href="#'+anchor+'"' in html
print('BAKIRKOY2019_EMEP_INDEPENDENT_APPEND_ONLY_OK',json.dumps(counts,sort_keys=True),flush=True)
