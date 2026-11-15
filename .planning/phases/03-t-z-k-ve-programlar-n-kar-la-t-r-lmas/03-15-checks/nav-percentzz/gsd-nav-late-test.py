import json, os, pathlib, shutil, subprocess, sys, time
root=pathlib.Path('/hpc/group/pfisterlab/mg551/storage/proje')
out=root/'.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-15-checks/nav-percentzz'
sys.path.insert(0,str(root/'tests'))
from test_comparison_navigation import REPORT, selected_records
from browser_probe import browser
from urllib.parse import quote
config=selected_records(); config['direct']=True
url=REPORT.as_uri()+'#comparison-'+quote(config['row'],safe='')
trace=pathlib.Path('/tmp/gsd-nav-late-profile.jsonl')
wrapper=pathlib.Path('/tmp/gsd-nav-late-browser.cjs')
wrapper.chmod(0o755)
env=dict(os.environ,NAV_REAL_BROWSER=browser(),NAV_LATE_TRACE=str(trace))
results=[]
for label, probe in [('original','/tmp/gsd-nav-original.cjs'),('fixed',str(root/'tests/comparison_navigation.cjs'))]:
    before=len(trace.read_text().splitlines()) if trace.exists() else 0
    run=subprocess.run(['node',probe,str(wrapper),url,'1365',json.dumps(config,ensure_ascii=False)],env=env,capture_output=True,text=True,timeout=100)
    lines=trace.read_text().splitlines() if trace.exists() else []
    profiles=[json.loads(line)['profile'] for line in lines[before:]]
    leftovers=[p for p in profiles if pathlib.Path(p).exists()]
    results.append({'version':label,'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'profiles':profiles,'leftovers':leftovers})
    for p in leftovers: shutil.rmtree(p)
(out/'late-write-test.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
assert len(results[0]['leftovers'])==1,results
assert results[1]['returncode']==0 and len(results[1]['profiles'])==1 and not results[1]['leftovers'],results
(out/'late-write-test.exit').write_text('0\n')
