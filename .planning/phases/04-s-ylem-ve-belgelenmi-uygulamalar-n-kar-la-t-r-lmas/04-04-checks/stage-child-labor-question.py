import hashlib, json, shutil
from pathlib import Path

repo = Path.cwd()
checks = repo/'.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks'
stage = Path('/tmp/gsd-0404-program-staging').resolve()
source = (repo/'data/practices/sources/yeni-parti').resolve()
package = checks/'package-child-labor-question-standalone-draft.json'
paths = set()
for entry in json.loads(package.read_text())['entries']:
    v = entry['values']
    if entry['kind'] == 'document_version':
        paths.update(v[k] for k in ('original_path', 'readable_path') if v.get(k))
    elif entry['kind'] == 'archive_view':
        paths.update(v[k] for k in ('index_path', 'manifest_path') if v.get(k))
added = existing = 0
for relative in sorted(paths):
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError(relative)
    src, dest = source/p, stage/'data'/p
    if dest.exists():
        if src.exists() and dest.read_bytes() != src.read_bytes():
            raise ValueError('collision '+relative)
        existing += 1
    elif src.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        added += 1
    else:
        raise FileNotFoundError(relative)
target = stage/'data/practices/package-child-labor-question-standalone-draft.json'
if target.exists() and target.read_bytes() != package.read_bytes():
    raise ValueError('package collision')
if not target.exists():
    shutil.copyfile(package, target)
print('STAGED', len(paths), 'EXISTING', existing, 'ADDED', added, 'SHA256', hashlib.sha256(target.read_bytes()).hexdigest())
