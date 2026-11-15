"""Sabit final sürümünde bağımsız, salt okunur P2/P3 denetimlerini başlat."""
import datetime
import hashlib
import json
import os
import subprocess
import shutil
from pathlib import Path

root = Path('/hpc/group/pfisterlab/mg551/storage/proje')
checks = root / '.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-15-checks'
if (root / 'data/.write.lock').exists():
    raise SystemExit('Yazıcı kilidi var; denetim başlatılmadı')
release = json.loads((root / 'data/current.json').read_text())['release_id']
release_dir = root / 'data/releases' / release
files = ['manifest.json', 'records.sqlite3', 'records.json', 'index.html']
snapshot = Path('/tmp') / ('gsd-0315-final-audit-' + release)
snapshot.mkdir(exist_ok=False)
shutil.copytree(root / 'src', snapshot / 'src', ignore=shutil.ignore_patterns('__pycache__'))
for name in files:
    shutil.copyfile(release_dir / name, snapshot / name)
hashes = {name: hashlib.sha256((snapshot / name).read_bytes()).hexdigest() for name in files}
source_hashes = {str(p.relative_to(snapshot)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted((snapshot / 'src').rglob('*')) if p.is_file()}
runs = {}
for name, extra in [('phase2', '--phase 2'), ('phase3-partial', '--phase 3 --stage partial')]:
    log = checks / (name + '.log')
    exit_file = checks / (name + '.exit')
    command = f'python3 src/arsiv.py audit --release {release} {extra}'
    shell = f'{command}; r=$?; printf "%s\\n" "$r" > "{exit_file}"; exit "$r"'
    out = log.open('w')
    proc = subprocess.Popen(['bash', '-c', shell], cwd=root, stdin=subprocess.DEVNULL,
                            stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
    runs[name] = {'pid': proc.pid, 'command': command, 'log': str(log), 'exit': str(exit_file)}
record = {'release': release, 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'host': os.uname().nodename, 'input_snapshot': str(snapshot), 'release_hashes': hashes,
          'source_hashes': source_hashes, 'runs': runs}
(checks / 'final-audits-run.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
