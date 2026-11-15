from pathlib import Path
import os,sys,json,subprocess,datetime,socket,signal
base=Path(__file__).resolve().parent
copy=base/'workspace'
meta=json.loads((base/'prospective-inputs.json').read_text())
handshake={'token':meta['token'],'host':socket.gethostname(),'supervisor_pid':os.getpid(),'supervisor_sid':os.getsid(0),'copy_root':str(copy),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(base/'handshake.json').write_text(json.dumps(handshake,indent=2)+'\n')
env=dict(os.environ,PYTHONPATH=str(copy/'src')+os.pathsep+str(copy/'tests'),PYTHONUNBUFFERED='1')
with (base/'run.log').open('w') as log:
    command=[sys.executable,'-u','-m','unittest','-v',meta['test']]
    log.write(json.dumps({'command':command,'cwd':str(copy),'token':meta['token']})+'\n');log.flush()
    child=subprocess.Popen(command,cwd=copy,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    handshake.update(child_pid=child.pid,child_sid=os.getsid(child.pid));(base/'handshake.json').write_text(json.dumps(handshake,indent=2)+'\n')
    try: code=child.wait(timeout=10800)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid,signal.SIGTERM);code=124
        try:child.wait(timeout=30)
        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
    (base/'exit.json').write_text(json.dumps({'exit_code':code,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
