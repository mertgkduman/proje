"""Copy a small, accepted historical release and its actual dependencies."""
import json
from pathlib import Path
import shutil


BASE = '7f816c5afd704cf3a88f2cfd8638528f'


def copy_fixture(source, target):
    source, target = Path(source), Path(target)
    target.mkdir(parents=True)
    release = BASE
    seen = set()
    while release:
        if release in seen:
            raise ValueError('Release ancestry cycle')
        seen.add(release)
        folder = source / 'releases' / release
        shutil.copytree(folder, target / 'releases' / release)
        manifest = json.loads((folder / 'manifest.json').read_text())
        records = json.loads((folder / 'records.json').read_text())
        paths = [v[field] for v in records['document_version']
                 for field in ('original_path', 'readable_path')]
        paths += [view['index_path'] for view in records.get('archive_view', [])]
        for path in paths:
            # Source paths remain confined, just as in the real validator.
            parent = Path(path).parent
            if parent.is_absolute() or '..' in parent.parts:
                raise ValueError('Invalid fixture path')
            shutil.copytree(source / parent, target / parent, dirs_exist_ok=True)
        release = manifest.get('base_release')
    (target / 'current.json').write_text(json.dumps({'release_id': BASE}) + '\n')
