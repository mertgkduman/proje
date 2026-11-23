import importlib.util,json,os,sqlite3,subprocess,sys
from pathlib import Path
here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('harness',here.parent/'04-04-checks'/'samsun-reply-validation.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
h.HERE=here;h.SOURCE=h.DATA/'practices'/'sources'/'iyi'
scope='teacher-4314';stem='0407-iyi-teacher-4314';package=here/(scope+'-draft.json');review=here/(scope+'-review-draft.json')
assert h.sha(package)=='c64ce1c1de05d5f2662ce1ac25f1000cca43f648753f2a735c1979eaa6131fc8'
assert h.sha(review)=='15c155ffe954ef0d75bcc73e7cccd4c03e99cdd5e143a600d8662ca45613d0ad'
draft=json.loads(package.read_bytes())['practice_records'];assert (len(draft['practice_event']),len(draft['practice_relation']))==(17,10) and not draft['practice_closure']
r=h.main(package,review,scope,stem+'-event','0407-iyi-2026-7573-relation',None,expected_party='iyi',namespace='gsd-0407')
folder=Path(r['preview']);manifest=json.loads((folder/'manifest.json').read_bytes());assert manifest['renderer_version']==31
saved=json.loads((folder/'records.json').read_bytes());page=(folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table in ('practice_event','practice_relation','practice_candidate','practice_contribution'):
  for row in draft[table]:assert row in saved[table] and row==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(row['id'],)).fetchone())
 assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(stem+'-event',)).fetchone()
 assert db.execute('SELECT common_event_key FROM practice_event WHERE id=?',(stem+'-event',)).fetchone()[0]=='tbmm-28-4-106-10-4314-gundem'
for view in ('party','comparison'):
 tag='id="'+view+'-unmatched-'+stem+'-candidate"';assert page.count(tag)==1
 card=page.split(tag,1)[1].split('</article>',1)[0]
 for item in ('10/4314','Türkoğlu','kabul edilmedi'):assert item in card,(view,item)
root=here.parents[3];artifact=folder.parents[1]
audit=subprocess.run([sys.executable,'-c','import sys;from pathlib import Path;from arsiv import audit_release;audit_release(sys.argv[1],storage_root=Path(sys.argv[2]));print("INDEPENDENT_AUDIT_OK")',folder.name,str(artifact)],cwd=root,env={**os.environ,'PYTHONPATH':str(root/'src')},capture_output=True,text=True)
job=os.environ['SLURM_JOB_ID'];(here/(scope+'-'+job+'-independent.log')).write_text(audit.stdout+audit.stderr);(here/(scope+'-'+job+'-independent.exit')).write_text(str(audit.returncode)+'\n');assert audit.returncode==0 and 'INDEPENDENT_AUDIT_OK' in audit.stdout
r.update(renderer_version=31,independent_audit='PASS',both_views='PASS',sqlite='PASS');(here/(scope+'-'+job+'-complete.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('TEACHER_4314_VIEWS_AUDIT_OK',folder,flush=True)
