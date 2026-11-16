from pathlib import Path
import json,os,subprocess,sys,datetime,socket,hashlib
root=Path('/hpc/group/pfisterlab/mg551/storage/proje');proof=root/'.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-navigation'
meta=json.loads((proof/'prospective-inputs.json').read_text());token='v2-navigation-projection-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
run=dict(token=token,host=socket.gethostname(),supervisor_pid=os.getpid(),supervisor_sid=os.getsid(0),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
env=dict(os.environ,NAV_EVIDENCE=str(proof/'navigation-evidence.json'),PYTHONUNBUFFERED='1')
with (proof/'run.log').open('w') as log:
 child=subprocess.Popen([sys.executable,'tests/run.py','--pattern','test_comparison_navigation.py'],cwd=root,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 run.update(child_pid=child.pid,child_sid=os.getsid(child.pid));(proof/'handshake.json').write_text(json.dumps(run,indent=2)+'\n');code=child.wait()
changed=[p for p,h in meta['inputs'].items() if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]
(proof/'exit.json').write_text(json.dumps(dict(exit_code=code,changed_inputs=changed,unchanged_inputs=len(meta['inputs'])-len(changed),ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
