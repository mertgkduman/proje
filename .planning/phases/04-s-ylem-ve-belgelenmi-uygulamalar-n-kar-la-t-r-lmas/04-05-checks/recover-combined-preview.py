import hashlib, json, shutil, sys
from pathlib import Path

ROOT = Path('/hpc/group/pfisterlab/mg551/storage/proje')
sys.path.insert(0, str(ROOT / 'src'))
from arsiv import audit_release

source = Path('/tmp/gsd-0405-combined-62397038')
target = ROOT / 'data/.staging/gsd-0405-combined-recovered-62397038'
release = '3e9aed8b876d46d3be125256207259b2'
expected = '6873bdd3c56a4fff548076e1a687f4cbb200582024c3fc9a23787840c8e2c132'
receipt = ROOT / '.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/combined-62397038-recovery.json'
assert source.is_dir(), 'compute-node preview no longer exists'
assert not target.exists(), 'recovery target already exists'
shutil.copytree(source, target)
manifest_path = target / 'releases' / release / 'manifest.json'
digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
assert digest == expected, 'recovered manifest differs from original receipt'
manifest = json.loads(manifest_path.read_text())
assert manifest['renderer_version'] == 29, 'unexpected renderer version'
for name, expected_hash in manifest['files'].items():
    assert hashlib.sha256((manifest_path.parent / name).read_bytes()).hexdigest() == expected_hash
print('RECOVERY_BYTES_OK', digest, 'renderer', manifest['renderer_version'], flush=True)
audit_release(release, storage_root=target)
result = {'original_job': '62397038', 'package_commit': '89d990b', 'preview_root': str(target),
          'release': release, 'manifest_sha256': digest, 'renderer_version': manifest['renderer_version'],
          'audit': 'PASS'}
receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print('INDEPENDENT_AUDIT_OK', flush=True)
