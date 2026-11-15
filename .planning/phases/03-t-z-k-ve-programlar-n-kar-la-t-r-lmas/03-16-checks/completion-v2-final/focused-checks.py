"""Run the release-bound focused acceptance checks once, with captured inputs."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import uuid

root = Path.cwd()
job = Path('/tmp/proje-v2-production-focused-20261115')

if len(sys.argv) == 3 and sys.argv[1] == '--worker':
    release = sys.argv[2]
    meta = json.loads((job / 'job.json').read_text())
    (job / 'handshake.json').write_text(json.dumps({'token': meta['token'], 'host': socket.gethostname(),
        'pid': os.getpid(), 'sid': os.getsid(0), 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=2) + '\n')
    env = dict(os.environ, NAV_EVIDENCE=str(job / 'navigation-evidence.json'))
    patterns = [('comparisons', 'test_comparisons.py'), ('content', 'test_comparison_content.py'),
                ('synthesis', 'test_comparison_synthesis_contract.py'), ('stage', 'test_phase3_stage_compatibility.py'),
                ('navigation', 'test_comparison_navigation.py'), ('topics', 'test_topics.py'),
                ('documents', 'test_documents.py'), ('publication', 'test_publication.py'), ('dossiers', 'test_dossiers.py')]
    runs = [(name, [sys.executable, 'tests/run.py', '--pattern', pattern]) for name, pattern in patterns]
    runs += [('audit', [sys.executable, 'src/arsiv.py', 'audit', '--release', release]),
             ('phase2', [sys.executable, 'src/arsiv.py', 'audit', '--release', release, '--phase', '2']),
             ('phase3', [sys.executable, 'src/arsiv.py', 'audit', '--release', release, '--phase', '3', '--stage', 'complete'])]
    results = []
    code = 1
    try:
        for name, command in runs:
            if json.loads((root / 'data/current.json').read_text())['release_id'] != release or (root / 'data/.write.lock').exists():
                raise RuntimeError('Current changed or writer exists')
            with (job / (name + '.log')).open('w') as log:
                result = subprocess.run(command, cwd=root, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
            output = (job / (name + '.log')).read_text(errors='replace')
            count = re.search(r'TESTS_OK count=(\d+)', output)
            valid = result.returncode == 0
            if name in ('phase2', 'phase3'):
                valid = valid and ('PHASE' + name[-1] + '_AUDIT_OK') in output
            elif name != 'audit':
                valid = valid and bool(count and int(count.group(1)) > 0) and not re.search(r'\bskipped(?:=|\s)', output, re.I)
            if name == 'navigation' and valid:
                evidence = json.loads((job / 'navigation-evidence.json').read_text())
                valid = evidence.get('release_id') == release and len(evidence.get('results', [])) == 4 and all(r.get('checks') == '1' * 19 and r.get('archiveExcerptFound') for r in evidence['results'])
            results.append({'name': name, 'command': command, 'exit_code': result.returncode,
                            'test_count': int(count.group(1)) if count else None, 'valid': bool(valid)})
            (job / 'results.json').write_text(json.dumps({'release_id': release, 'results': results}, indent=2) + '\n')
            if not valid:
                break
        else:
            changed = [p for p, digest in meta['input_sha256'].items() if hashlib.sha256((root / p).read_bytes()).hexdigest() != digest]
            results.append({'name': 'input-integrity', 'changed': changed, 'valid': not changed})
            code = 0 if not changed else 1
    finally:
        (job / 'results.json').write_text(json.dumps({'release_id': release, 'results': results}, indent=2) + '\n')
        (job / 'exit.json').write_text(json.dumps({'exit_code': code, 'ended_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=2) + '\n')
    raise SystemExit(code)

if len(sys.argv) != 2:
    raise SystemExit('Usage: focused-checks.py RELEASE')
release = sys.argv[1]
if json.loads((root / 'data/current.json').read_text())['release_id'] != release or (root / 'data/.write.lock').exists():
    raise SystemExit('Current changed or writer exists')
job.mkdir(exist_ok=False)
paths = [p for tree in ('src', 'tests', 'data/comparisons', 'data/dossiers', 'data/deliveries') for p in (root / tree).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
paths += [root / 'data/current.json', Path(__file__).resolve()]
paths += [root / 'data/releases' / release / n for n in ('index.html', 'manifest.json', 'records.json', 'records.sqlite3')]
digests = {}
for path in paths:
    relative = path.relative_to(root)
    target = job / 'inputs' / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit('Input changed during capture: ' + str(relative))
    digests[str(relative)] = digest
token = uuid.uuid4().hex
meta = {'release_id': release, 'host': socket.gethostname(), 'token': token,
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'input_sha256': digests,
        'log': str(job / 'supervisor.log'), 'exit': str(job / 'exit.json')}
(job / 'job.json').write_text(json.dumps(meta, indent=2) + '\n')
with (job / 'supervisor.log').open('w') as log:
    process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker', release], cwd=root,
                               stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
print(json.dumps({'pid': process.pid, 'sid': os.getsid(process.pid), 'token': token, 'job': str(job)}))
