import importlib.util,json,os,sqlite3,subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('harness',D/'samsun-reply-validation.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
scope='nov03-genelgorusme-yeniparti-v2';stem='0404-nov03-genelgorusme-yeniparti';event=stem+'-event';candidate=stem+'-unmatched';con=stem+'-contribution'
package=D/(scope+'-draft.json');review=D/(scope+'-review.json')
assert h.sha(package)=='23918fd2d01247f5794b82af355568873fe39028c9636344c9d825e3d3b452f2'
assert h.sha(review)=='662aca6458f577464b0895ee7af49e486eec34c45d1c124cc532c6b7a93f6995'
draft=json.loads(package.read_bytes())['practice_records']; assert (len(draft['practice_event']),len(draft['practice_relation']))==(143,141) and not draft['practice_closure']
r=h.main(package,review,scope,event,'0404-fon-komisyon-1014-relation',None)
folder=Path(r['preview']); manifest=json.loads((folder/'manifest.json').read_bytes()); assert manifest['renderer_version']==31
saved=json.loads((folder/'records.json').read_bytes());page=(folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table,ident in [('practice_event',event),('practice_candidate',candidate),('practice_contribution',con)]:
  row=next(x for x in draft[table] if x['id']==ident);assert row in saved[table] and row==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone())
 assert db.execute('SELECT state FROM practice_candidate WHERE id=?',(candidate,)).fetchone()[0]=='unmatched'
 assert db.execute('SELECT contribution_kind FROM practice_contribution WHERE id=?',(con,)).fetchone()[0]=='support'
 assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(event,)).fetchone()
for view in ('party','comparison'):
 tag='id="'+view+'-unmatched-'+candidate+'"';assert page.count(tag)==1
 card=page.split(tag,1)[1].split('</article>',1)[0]
 for item in ('Aşkın Genç','ön görüşme','kabul edilmedi','8/153'):
  assert item in card,(view,item)
root=D.parents[3];artifact=folder.parents[1]
audit=subprocess.run([sys.executable,'-c','import sys;from pathlib import Path;from arsiv import audit_release;audit_release(sys.argv[1],storage_root=Path(sys.argv[2]));print("INDEPENDENT_AUDIT_OK")',folder.name,str(artifact)],cwd=root,env={**os.environ,'PYTHONPATH':str(root/'src')},capture_output=True,text=True)
job=os.environ['SLURM_JOB_ID'];(D/(scope+'-'+job+'-audit.log')).write_text(audit.stdout+audit.stderr);(D/(scope+'-'+job+'-audit.exit')).write_text(str(audit.returncode)+'\n');assert audit.returncode==0 and 'INDEPENDENT_AUDIT_OK' in audit.stdout
r.update(renderer_version=31,independent_audit='PASS',both_views='PASS',sqlite='PASS');(D/(scope+'-'+job+'-complete.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print('YENIPARTI_NOV03_BOTH_VIEWS_AUDIT_OK',folder,flush=True)
