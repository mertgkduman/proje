import json, os, pathlib, shutil, signal, subprocess, sys, time
root=pathlib.Path('/hpc/group/pfisterlab/mg551/storage/proje')
out=root/'.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-15-checks/nav-percentzz'
sys.path.insert(0,str(root/'tests'))
from test_comparison_navigation import REPORT, selected_records
from browser_probe import browser
from urllib.parse import quote
mode=sys.argv[1]; probe=sys.argv[2]; label=sys.argv[3]
config=selected_records();config['direct']=True
url=REPORT.as_uri()+'#comparison-'+quote(config['row'],safe='')
trace=out/('wr01-'+label+'-'+mode+'.jsonl')
env=dict(os.environ,WR01_BROWSER=browser(),WR01_MODE=mode,WR01_TRACE=str(trace))
proxy=pathlib.Path('/tmp/gsd-wr01-proxy.cjs');proxy.chmod(0o755)
start=time.monotonic()
process=subprocess.Popen(['node',probe,str(proxy),url,'1365',json.dumps(config,ensure_ascii=False)],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env,start_new_session=True)
try:
    stdout,stderr=process.communicate(timeout=12);timeout=False
except subprocess.TimeoutExpired:
    os.killpg(process.pid,signal.SIGKILL);stdout,stderr=process.communicate();timeout=True
elapsed=time.monotonic()-start
lines=[json.loads(x) for x in trace.read_text().splitlines()]
profiles={x['profile'] for x in lines if x['event']=='start'}
left=[p for p in profiles if pathlib.Path(p).exists()]
result={'label':label,'mode':mode,'probe_pid':process.pid,'timeout':timeout,'exit':process.returncode,'elapsed_seconds':elapsed,'stdout':stdout,'stderr':stderr,'profiles':list(profiles),'leftovers':left,'events':lines}
(out/('wr01-'+label+'-'+mode+'.json')).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
for p in left:shutil.rmtree(p)
if label=='red': assert timeout or left,result
else:
 assert not timeout and process.returncode==0 and not left,result
 assert len(profiles)==1 and any(x['event']=='close-request' for x in lines),result
 assert mode!='hang' or elapsed>=4.8,result
