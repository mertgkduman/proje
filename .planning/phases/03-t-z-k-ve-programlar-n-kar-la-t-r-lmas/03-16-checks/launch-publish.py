"""Capture prospective inputs, then launch one owned detached local refresh."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import uuid

root = Path(__file__).resolve().parents[4]
checks = Path(__file__).resolve().parent
data = root / 'data'
base = '27033583248b4951b3fe8e5fd6d77b9f'
if (data / '.write.lock').exists():
    raise SystemExit('A writer lock exists; do not start another writer')
if json.loads((data / 'current.json').read_text())['release_id'] != base:
    raise SystemExit('Current changed; reconcile before starting')
if (checks / 'comparison-check.exit').read_text().strip() != '0' or 'COMPARISON_INPUT_OK' not in (checks / 'comparison-check.log').read_text():
    raise SystemExit('The real package check has not passed')
job = Path('/tmp/gsd-0316-owned-publish')
job.mkdir(exist_ok=False)
inputs = [p for p in (root / 'src').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
inputs += [checks / 'publish-owned.py', checks / 'launch-publish.py',
           checks / 'comparison-check.exit', checks / 'comparison-check.log',
           data / 'comparisons/03-source-review.json', data / 'current.json']
inputs += [data / 'releases' / base / name for name in ('manifest.json', 'records.json', 'records.sqlite3', 'index.html')]
digests = {}
for path in inputs:
    relative = path.relative_to(root)
    target = job / 'inputs' / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, target)
    digests[str(relative)] = hashlib.sha256(target.read_bytes()).hexdigest()
    if hashlib.sha256(path.read_bytes()).hexdigest() != digests[str(relative)]:
        raise SystemExit('Input changed while copied: ' + str(relative))
records = json.loads((job / 'inputs/data/releases' / base / 'records.json').read_text())
sources = [{k: v[k] for k in ('id', 'original_path', 'sha256')} for v in records['document_version']]
chain = []
release = base
while release:
    path = data / 'releases' / release / 'manifest.json'
    raw = path.read_bytes()
    manifest = json.loads(raw)
    chain.append({'release_id': release, 'manifest_sha256': hashlib.sha256(raw).hexdigest(), 'files': manifest['files']})
    release = manifest.get('base_release')
log = (job / 'run.log').open('w')
exit_path = job / 'exit'
process = subprocess.Popen(['bash', '-c', 'python3 "$1"; code=$?; printf "%s\\n" "$code" > "$2"',
                            'publish', str(checks / 'publish-owned.py'), str(exit_path)],
                           cwd=root, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                           start_new_session=True)
metadata = {'host': socket.gethostname(), 'pid': process.pid, 'sid': os.getsid(process.pid),
            'token': uuid.uuid4().hex, 'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'command': 'python3 ' + str(checks / 'publish-owned.py'), 'input_sha256': digests,
            'immutable_source_version_references': sources, 'immutable_view_references': records.get('archive_view', []),
            'release_chain_references': chain,
            'log': str(job / 'run.log'), 'exit': str(exit_path)}
(job / 'job.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'pid': process.pid, 'sid': metadata['sid'], 'host': metadata['host'], 'token': metadata['token'], 'metadata': str(job / 'job.json')}))
