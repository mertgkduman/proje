import hashlib,json,shutil,sqlite3,sys
from pathlib import Path
D=Path(__file__).parent
package_name,review_name,log_name,receipt_name,release_name,package_hash,review_hash,event_count,relation_count,job=sys.argv[1:]
P=Path('data/practices/04-emep.json');R=Path('data/practices/04-emep-review.json');pp=D/package_name;rr=D/review_name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(pp)==package_hash and sha(rr)==review_hash
a=json.loads(P.read_text());b=json.loads(pp.read_text());x=json.loads(R.read_text());y=json.loads(rr.read_text())
assert all(v in b['entries'] for v in a['entries'])
assert all(all(v in b['practice_records'][k] for v in vs) for k,vs in a['practice_records'].items())
assert all(all(v in y[k] for v in vs) for k,vs in x.items())
assert not b['practice_records']['practice_closure']
assert len(b['practice_records']['practice_event'])==int(event_count) and len(b['practice_records']['practice_relation'])==int(relation_count)
log=(D/log_name).read_text()
assert all(s in log for s in ['PRACTICE_INPUT_OK','PRACTICE_SOURCE_REVIEW_OK','PRACTICE_PREVIEW_OK','EMEP_PREVIEW_DB_JSON_BOTH_VIEWS_AND_INDEPENDENT_AUDIT_OK'])
canonical=sha(Path('data/current.json'));assert canonical=='5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7'
release=Path(release_name);export=json.loads((release/'records.json').read_text());html=(release/'index.html').read_text()
with sqlite3.connect((release/'records.sqlite3').resolve().as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table in ['practice_event','practice_relation']:
  for row in b['practice_records'][table]:assert row in export[table] and dict(db.execute('select * from '+table+' where id=?',(row['id'],)).fetchone())==row
for row in b['practice_records']['practice_relation']:
 for prefix in ['party','comparison']:
  anchor=prefix+'-practice-'+row['id'];assert html.count('id="'+anchor+'"')==1 and html.count('href="#'+anchor+'"')>=1
receipt=dict(job=job,status='COMPLETED 0:0; input/source/preview and independent audit pass',renderer=29,package_sha256=sha(pp),review_sha256=sha(rr),release=str(release),files_sha256={n:sha(release/n) for n in ['manifest.json','records.json','records.sqlite3','index.html']},canonical_current_sha256=canonical,relations=int(relation_count),event_count=int(event_count),old_package_and_review_preserved=True,both_view_href_pass=True,scope_closures=0)
with (D/receipt_name).open('x') as f:json.dump(receipt,f,indent=2,ensure_ascii=False);f.write('\n')
shutil.copyfile(pp,P);shutil.copyfile(rr,R)
print('MONOTONIC_SQL_JSON_HTML_PASS',package_hash)
