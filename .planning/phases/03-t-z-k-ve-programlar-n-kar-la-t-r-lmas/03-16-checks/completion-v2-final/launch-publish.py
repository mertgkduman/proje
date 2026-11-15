"""Guard and supervise a single production-local v2 refresh."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import uuid

root = Path.cwd()
here = Path(__file__).resolve().parent
job = Path('/tmp/proje-v2-production-publish-20261115')
gate = Path('/tmp/proje-v2-api-final-20261115T200402Z/exit.json')
base = '85b1a453ce2346a8ad0df325a2b73ae9'

if len(sys.argv) == 2 and sys.argv[1] == '--supervisor':
    meta = json.loads((job / 'job.json').read_text())
    handshake = {'token': meta['token'], 'host': socket.gethostname(), 'supervisor_pid': os.getpid(),
                 'supervisor_sid': os.getsid(0), 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (job / 'handshake.json').write_text(json.dumps(handshake, indent=2) + '\n')
    with (job / 'run.log').open('w') as log:
        child = subprocess.Popen([sys.executable, '-u', str(job / 'publish-owned.py')], cwd=root,
                                 stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        handshake.update(child_pid=child.pid, child_sid=os.getsid(child.pid))
        (job / 'handshake.json').write_text(json.dumps(handshake, indent=2) + '\n')
        code = child.wait()
    (job / 'exit.json').write_text(json.dumps({'exit_code': code, 'ended_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=2) + '\n')
    raise SystemExit(code)

if not gate.exists() or json.loads(gate.read_text())['exit_code'] != 0:
    raise SystemExit('API gate has not passed')
if (root / 'data/.write.lock').exists() or json.loads((root / 'data/current.json').read_text())['release_id'] != base:
    raise SystemExit('Writer exists or current changed; reconcile before publication')
prospective = json.loads((here / 'prospective.json').read_text())
for path, expected in prospective['file_sha256'].items():
    if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
        raise SystemExit('Prospective input changed: ' + path)
job.mkdir(exist_ok=False)
worker = (here / 'publish-owned.py').read_bytes()
(job / 'publish-owned.py').write_bytes(worker)
token = uuid.uuid4().hex
meta = {'host': socket.gethostname(), 'token': token, 'base': base,
        'prospective_sha256': hashlib.sha256((here / 'prospective.json').read_bytes()).hexdigest(),
        'worker_sha256': hashlib.sha256(worker).hexdigest(),
        'api_exit_sha256': hashlib.sha256(gate.read_bytes()).hexdigest(),
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'log': str(job / 'run.log'), 'exit': str(job / 'exit.json')}
(job / 'job.json').write_text(json.dumps(meta, indent=2) + '\n')
with (job / 'supervisor.log').open('w') as log:
    process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--supervisor'], cwd=root,
                               stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
print(json.dumps({'pid': process.pid, 'sid': os.getsid(process.pid), 'token': token, 'job': str(job)}))
