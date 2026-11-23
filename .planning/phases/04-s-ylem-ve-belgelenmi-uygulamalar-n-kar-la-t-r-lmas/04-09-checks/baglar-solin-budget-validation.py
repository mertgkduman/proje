import importlib.util,json,os,sqlite3,subprocess,sys
from pathlib import Path
here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('harness',here.parent/'04-04-checks'/'samsun-reply-validation.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.HERE=here;h.SOURCE=h.DATA/'practices'/'sources'/'dbp'
case='baglar-solin-budget';stem='0409-baglar-solin-budget-';package=here/(case+'-draft.json');review=here/(case+'-review-draft.json')
assert h.sha(package)=='c261a747122fd39d50250c84c2ae6aed9884515ba5a8506610a9ff55f06b2957'
assert h.sha(review)=='56f9115e9e4006f24900431a9ac442a0b7d56590ec6dcbcdbaefc816d48c3cae'
draft=json.loads(package.read_bytes())['practice_records'];assert (len(draft['practice_event']),len(draft['practice_relation']),len(draft['practice_closure']))==(64,7,0)
r=h.main(package,review,case,stem+'171-event','0409-dbp-baglar-2015-cemr-relation',None,expected_party='dbp',namespace='gsd-0409')
folder=Path(r['preview']);manifest=json.loads((folder/'manifest.json').read_bytes());assert manifest['renderer_version']==31
saved=json.loads((folder/'records.json').read_bytes());page=(folder/'index.html').read_text();numbers=('139','140','167','171','210','256')
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table in ('practice_event','practice_relation','practice_candidate','practice_dispute'):
  for row in draft[table]:assert row in saved[table] and row==dict(db.execute('SELECT * FROM '+table+' WHERE id=?',(row['id'],)).fetchone())
 for n in numbers:assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(stem+n+'-event',)).fetchone()
 for n,prior in [('167','139'),('171','140'),('210','184')]:assert db.execute('SELECT 1 FROM practice_event_evidence WHERE event_id=? AND passage_id=?',(stem+n+'-event',stem+prior+'-file')).fetchone()
for view in ('party','comparison'):
 for n in numbers:
  tag='id="'+view+'-unmatched-'+stem+n+'-unmatched"';assert page.count(tag)==1,(view,n)
  card=page.split(tag,1)[1].split('</article>',1)[0]
  assert {'139':'Yazı İşleri','140':'Solin','167':'Yazı İşleri','171':'Solin','210':'İnsan Kaynakları','256':'2015'}[n] in card,(view,n)
root=here.parents[3];artifact=folder.parents[1]
audit=subprocess.run([sys.executable,'-c','import sys;from pathlib import Path;from arsiv import audit_release;audit_release(sys.argv[1],storage_root=Path(sys.argv[2]));print("INDEPENDENT_AUDIT_OK")',folder.name,str(artifact)],cwd=root,env={**os.environ,'PYTHONPATH':str(root/'src')},capture_output=True,text=True)
job=os.environ['SLURM_JOB_ID'];(here/(case+'-'+job+'-independent.log')).write_text(audit.stdout+audit.stderr);(here/(case+'-'+job+'-independent.exit')).write_text(str(audit.returncode)+'\n');assert audit.returncode==0 and 'INDEPENDENT_AUDIT_OK' in audit.stdout
r.update(renderer_version=31,independent_audit='PASS',both_views='PASS',sqlite='PASS');(here/(case+'-'+job+'-complete.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('DBP_SOLIN_BUDGET_VIEWS_AUDIT_OK',folder,flush=True)

