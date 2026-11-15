import hashlib, json, os, pathlib, shutil, socket, subprocess, sys, time
root = pathlib.Path('/hpc/group/pfisterlab/mg551/storage/proje')
base = pathlib.Path('/tmp/gsd-nav-percentzz-diag-20261115')
base.mkdir(exist_ok=False)
for name in ('src', 'tests'):
    shutil.copytree(root / name, base / name, ignore=shutil.ignore_patterns('__pycache__'))
data = base / 'data'
(data / 'releases').mkdir(parents=True)
shutil.copy2(root / 'data/current.json', data / 'current.json')
rid = json.loads((data / 'current.json').read_text())['release_id']
shutil.copytree(root / 'data/releases' / rid, data / 'releases' / rid)
view = 'ecc51c44806790d9980a80aebb940c57'
(data / 'views').mkdir()
shutil.copytree(root / 'data/views' / view, data / 'views' / view)
files = [p for p in base.rglob('*') if p.is_file()]
hashes = {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(base / 'hashes.json').write_text(json.dumps(hashes, indent=2, sort_keys=True))
env = dict(os.environ, PYTHONPATH=str(base / 'tests'))
env.pop('NAV_REPORT', None); env.pop('NAV_RECORDS', None); env.pop('NAV_EVIDENCE', None)
cmd = [sys.executable, '-m', 'unittest', '-v', 'test_comparison_navigation.ComparisonNavigation.test_unicode_and_space_ids_in_real_source_preview']
with (base / 'test.log').open('w') as log:
    result = subprocess.run(cmd, cwd=base, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=700)
(base / 'test.exit').write_text(str(result.returncode) + '\n')
