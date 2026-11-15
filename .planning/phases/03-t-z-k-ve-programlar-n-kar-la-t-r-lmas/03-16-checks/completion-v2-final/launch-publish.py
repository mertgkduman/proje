"""Guard and supervise a single production-local v2 refresh."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import uuid

root = Path.cwd()
here = Path(__file__).resolve().parent
job = Path('/tmp/proje-v2-production-publish-20261115')
gate_dir = Path('/tmp/proje-phase3-final-regression-20261115T221331Z')
gate = gate_dir / 'exit.json'
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

integrity_path = gate_dir / 'post-input-integrity.json'
if not gate.exists() or not integrity_path.exists():
    raise SystemExit('Full regression and input integrity have not completed')
result = json.loads(gate.read_text())
integrity = json.loads(integrity_path.read_text())
matches = re.findall(r'TESTS_OK count=(\d+)', (gate_dir / 'run.log').read_text(errors='replace'))
if (result.get('exit_code') != 0 or result.get('status') != 'passed' or
    not matches or int(matches[-1]) <= 0 or int(matches[-1]) != result.get('test_count') or
    integrity.get('changed') != [] or integrity.get('unchanged_count') != 2255):
    raise SystemExit('Full regression or input integrity failed')
handshake = json.loads((gate_dir / 'handshake.json').read_text())
try:
    os.kill(handshake['supervisor_pid'], 0)
except ProcessLookupError:
    pass
else:
    raise SystemExit('Regression supervisor has not exited')
gate_inputs = json.loads((gate_dir / 'prospective-inputs.json').read_text())
if gate_inputs.get('source_current') != base or len(gate_inputs.get('inputs', [])) != 2255:
    raise SystemExit('Unexpected regression input epoch')
required = [x for x in gate_inputs['inputs'] if x['path'].startswith(('src/', 'tests/')) or x['path'] == 'data/comparisons/03-completion-review-v2.json']
if not required or not any(x['path'] == 'data/comparisons/03-completion-review-v2.json' for x in required):
    raise SystemExit('Regression package or source/test input missing')
for item in required:
    path = root / item['path']
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
        raise SystemExit('Regression source, test or package changed: ' + item['path'])
package = root / 'data/comparisons/03-completion-review-v2.json'
if hashlib.sha256(package.read_bytes()).hexdigest() != 'e5156e8f32d5d305aa0ceb48bd003dcd969ba74e11e0c404f21d32a9dade4989':
    raise SystemExit('Canonical package digest changed')
if (root / 'data/.write.lock').exists() or json.loads((root / 'data/current.json').read_text())['release_id'] != base:
    raise SystemExit('Writer exists or current changed; reconcile before publication')
prospective = json.loads((here / 'prospective.json').read_text())
for group in ('file_sha256', 'raw_original_sha256', 'view_sha256'):
    for path, expected in prospective[group].items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
            raise SystemExit('Prospective input changed: ' + path)
job.mkdir(exist_ok=False)
worker = (here / 'publish-owned.py').read_bytes()
(job / 'publish-owned.py').write_bytes(worker)
token = uuid.uuid4().hex
meta = {'host': socket.gethostname(), 'token': token, 'base': base,
        'prospective_sha256': hashlib.sha256((here / 'prospective.json').read_bytes()).hexdigest(),
        'worker_sha256': hashlib.sha256(worker).hexdigest(),
        'launcher_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'regression_exit_sha256': hashlib.sha256(gate.read_bytes()).hexdigest(),
        'regression_integrity_sha256': hashlib.sha256(integrity_path.read_bytes()).hexdigest(),
        'regression_inputs_sha256': hashlib.sha256((gate_dir / 'prospective-inputs.json').read_bytes()).hexdigest(),
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'log': str(job / 'run.log'), 'exit': str(job / 'exit.json')}
(job / 'job.json').write_text(json.dumps(meta, indent=2) + '\n')
with (job / 'supervisor.log').open('w') as log:
    process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--supervisor'], cwd=root,
                               stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
print(json.dumps({'pid': process.pid, 'sid': os.getsid(process.pid), 'token': token, 'job': str(job)}))
