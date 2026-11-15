"""Launch serialized, release-bound final checks with prospective input proof."""
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

root = Path(__file__).resolve().parents[4]
checks = Path(__file__).resolve().parent
job = Path('/tmp/gsd-0316-final-checks')


def worker(release):
    env = dict(os.environ, NAV_EVIDENCE=str(job / 'navigation-evidence.json'))
    runs = [('comparisons', ['python3', 'tests/run.py', '--pattern', 'test_comparisons.py']),
            ('coverage', ['python3', 'tests/run.py', '--pattern', 'test_completion_coverage.py']),
            ('comparison-content', ['python3', 'tests/run.py', '--pattern', 'test_comparison_content.py']),
            ('comparison-synthesis', ['python3', 'tests/run.py', '--pattern', 'test_comparison_synthesis_contract.py']),
            ('phase3-stage', ['python3', 'tests/run.py', '--pattern', 'test_phase3_stage_compatibility.py']),
            ('navigation', ['python3', 'tests/run.py', '--pattern', 'test_comparison_navigation.py']),
            ('topics', ['python3', 'tests/run.py', '--pattern', 'test_topics.py']),
            ('documents', ['python3', 'tests/run.py', '--pattern', 'test_documents.py']),
            ('publication', ['python3', 'tests/run.py', '--pattern', 'test_publication.py']),
            ('dossiers', ['python3', 'tests/run.py', '--pattern', 'test_dossiers.py']),
            ('phase2', ['python3', 'src/arsiv.py', 'audit', '--release', release, '--phase', '2']),
            ('phase3', ['python3', 'src/arsiv.py', 'audit', '--release', release, '--phase', '3', '--stage', 'complete'])]
    results = []
    exit_code = 1
    try:
        for name, command in runs:
            if json.loads((root / 'data/current.json').read_text())['release_id'] != release:
                raise RuntimeError('Current changed during checks')
            with (job / (name + '.log')).open('w') as log:
                result = subprocess.run(command, cwd=root, env=env, stdin=subprocess.DEVNULL,
                                        stdout=log, stderr=subprocess.STDOUT)
            text = (job / (name + '.log')).read_text(errors='replace')
            count = re.search(r'TESTS_OK count=(\d+)', text)
            valid = result.returncode == 0
            if name in ('phase2', 'phase3'):
                valid = valid and ('PHASE' + name[-1] + '_AUDIT_OK') in text
            else:
                valid = valid and bool(count and int(count.group(1)) > 0) and not re.search(r'\bskipped(?:=|\s)', text, re.I)
            results.append({'name': name, 'command': command, 'exit_code': result.returncode,
                            'test_count': int(count.group(1)) if count else None, 'valid': bool(valid)})
            (job / (name + '.exit')).write_text(str(result.returncode) + '\n')
            if not valid:
                break
            if name == 'navigation':
                evidence = json.loads((job / 'navigation-evidence.json').read_text())
                if evidence.get('release_id') != release or len(evidence.get('results', [])) != 4 or any(r.get('checks') != '1' * 19 or not r.get('archiveExcerptFound') for r in evidence['results']):
                    raise RuntimeError('Navigation evidence is incomplete or names a different release')
        else:
            saved = json.loads((job / 'job.json').read_text())
            changed = [path for path, digest in saved['input_sha256'].items()
                       if hashlib.sha256((root / path).read_bytes()).hexdigest() != digest]
            results.append({'name': 'input-integrity', 'changed': changed, 'valid': not changed})
            if not changed:
                exit_code = 0
    finally:
        (job / 'results.json').write_text(json.dumps({'release_id': release, 'results': results}, ensure_ascii=False, indent=2) + '\n')
        (job / 'exit').write_text(str(exit_code) + '\n')
    return exit_code


if len(sys.argv) == 3 and sys.argv[1] == '--worker':
    raise SystemExit(worker(sys.argv[2]))
if len(sys.argv) != 2:
    raise SystemExit('Usage: final-checks.py RELEASE_ID')
release = sys.argv[1]
data = root / 'data'
if (data / '.write.lock').exists() or json.loads((data / 'current.json').read_text())['release_id'] != release:
    raise SystemExit('Current differs or a writer lock exists')
folder = data / 'releases' / release
manifest = json.loads((folder / 'manifest.json').read_text())
if manifest.get('comparison_completion_version') != 1:
    raise SystemExit('Final completion marker is absent')
job.mkdir(exist_ok=False)
inputs = [p for tree in ('src', 'tests') for p in (root / tree).rglob('*')
          if p.is_file() and '__pycache__' not in p.parts]
inputs += [Path(__file__), data / 'current.json', data / 'comparisons/03-source-review.json']
inputs += [folder / name for name in ('manifest.json', 'records.json', 'records.sqlite3', 'index.html')]
digests = {}
for path in inputs:
    relative = path.relative_to(root)
    target = job / 'inputs' / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, target)
    digests[str(relative)] = hashlib.sha256(target.read_bytes()).hexdigest()
    if hashlib.sha256(path.read_bytes()).hexdigest() != digests[str(relative)]:
        raise SystemExit('Input changed while copied: ' + str(relative))
records = json.loads((job / 'inputs/data/releases' / release / 'records.json').read_text())
sources = [{k: v[k] for k in ('id', 'original_path', 'sha256')} for v in records['document_version']]
chain = []
rid = release
while rid:
    raw = (data / 'releases' / rid / 'manifest.json').read_bytes()
    item = json.loads(raw)
    chain.append({'release_id': rid, 'manifest_sha256': hashlib.sha256(raw).hexdigest(), 'files': item['files']})
    rid = item.get('base_release')
log = (job / 'supervisor.log').open('w')
process = subprocess.Popen([sys.executable, str(Path(__file__)), '--worker', release], cwd=root,
                           stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                           start_new_session=True)
metadata = {'release_id': release, 'host': socket.gethostname(), 'pid': process.pid,
            'sid': os.getsid(process.pid), 'token': uuid.uuid4().hex,
            'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'input_sha256': digests,
            'immutable_source_version_references': sources, 'immutable_view_references': records.get('archive_view', []),
            'release_chain_references': chain, 'log': str(job / 'supervisor.log'), 'exit': str(job / 'exit')}
(job / 'job.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'pid': process.pid, 'sid': metadata['sid'], 'host': metadata['host'], 'token': metadata['token'], 'metadata': str(job / 'job.json')}))
