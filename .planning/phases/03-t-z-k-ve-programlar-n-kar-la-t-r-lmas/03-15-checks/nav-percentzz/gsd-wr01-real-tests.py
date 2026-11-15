import datetime,json,os,pathlib,socket,subprocess,sys
root=pathlib.Path('/hpc/group/pfisterlab/mg551/storage/proje')
out=root/'.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-15-checks/nav-percentzz'
cmd=[sys.executable,'tests/run.py','--pattern','test_comparison_navigation.py']
env=dict(os.environ,NAV_EVIDENCE=str(out/'wr01-real-navigation.json'))
for k in ('NAV_REPORT','NAV_RECORDS'):env.pop(k,None)
(out/'wr01-real-run.json').write_text(json.dumps({'pid':os.getpid(),'host':socket.gethostname(),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd,'inputs':'wr01-fixed-inputs.sha256'},indent=2)+'\n')
with (out/'wr01-real-tests.log').open('w') as log:
 try:code=subprocess.run(cmd,cwd=root,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,timeout=900).returncode
 except subprocess.TimeoutExpired:code=124
(out/'wr01-real-tests.exit').write_text(str(code)+'\n')
