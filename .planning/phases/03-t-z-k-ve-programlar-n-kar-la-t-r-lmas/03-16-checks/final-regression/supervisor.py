from pathlib import Path
import os,sys,json,subprocess,socket,datetime,hashlib,re
base=Path(__file__).resolve().parent;meta=json.loads((base/'prospective-inputs.json').read_text());copy=Path(meta['copy_root'])
handshake=dict(token=meta['token'],host=socket.gethostname(),supervisor_pid=os.getpid(),supervisor_sid=os.getsid(0),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(base/'handshake.json').write_text(json.dumps(handshake,indent=2)+'\n')
env=dict(os.environ,CI='true',PYTHONUNBUFFERED='1')
cmd=['node',meta['official_helper'],'run-with-timeout',str(meta['timeout_seconds']),'--','bash','-c',meta['normalized_command']]
with (base/'run.log').open('w') as log:
 log.write(json.dumps(dict(command=cmd,cwd=str(copy),token=meta['token']))+'\n');log.flush()
 child=subprocess.Popen(cmd,cwd=copy,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 handshake.update(child_pid=child.pid,child_sid=os.getsid(child.pid));(base/'handshake.json').write_text(json.dumps(handshake,indent=2)+'\n')
 code=child.wait()
text=(base/'run.log').read_text(errors='replace');matches=re.findall(r'TESTS_OK count=(\d+)',text);count=int(matches[-1]) if matches else None
result=dict(exit_code=code,test_count=count,status='passed' if code==0 and count and count>0 else ('timeout' if code==124 else 'failed'),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(base/'exit.json').write_text(json.dumps(result,indent=2)+'\n')
changed=[]
for item in meta['inputs']:
 path=copy/item['path']
 if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:changed.append(item['path'])
(base/'post-input-integrity.json').write_text(json.dumps(dict(changed=changed,unchanged_count=len(meta['inputs'])-len(changed)),indent=2)+'\n')
