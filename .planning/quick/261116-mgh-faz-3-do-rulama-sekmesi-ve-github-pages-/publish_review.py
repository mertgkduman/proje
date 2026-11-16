"""Publish the user-approved review through the ordinary immutable archive API."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src'))
import arsiv

OUT = Path(__file__).resolve().parent
BASE = '3a3021c8e81749c3834462d1a0d81231'


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def main():
    assert arsiv.current() == BASE
    base_dir = arsiv.DATA / 'releases' / BASE
    before = {p.name: digest(p) for p in base_dir.iterdir() if p.is_file()}
    print(timestamp(), 'Opening ordinary workspace; checking all historical releases', flush=True)
    work = arsiv.open_workspace('/tmp')
    save('publication-progress.json', {'stage': 'workspace_ready', 'workspace': str(work), 'at': timestamp()})
    print(timestamp(), 'Workspace ready', work, flush=True)
    acceptance = json.loads((arsiv.DATA / 'comparisons/03-human-acceptance.json').read_text())
    arsiv.record(work, 'review', acceptance)
    print(timestamp(), 'Publishing renderer24 with user acceptance', flush=True)
    release = arsiv.publish_release(work, refresh=True)
    folder = arsiv.DATA / 'releases' / release
    old = json.loads((base_dir / 'records.json').read_text())
    new = json.loads((folder / 'records.json').read_text())
    for name in old:
        if name == 'release_id':
            continue
        if name == 'review':
            assert all(row in new[name] for row in old[name])
            assert len(new[name]) == len(old[name]) + 1
            assert acceptance in new[name]
        else:
            assert old[name] == new[name], name
    assert before == {p.name: digest(p) for p in base_dir.iterdir() if p.is_file()}
    manifest = json.loads((folder / 'manifest.json').read_text())
    assert manifest['renderer_version'] == 24
    assert manifest['comparison_stage'] == 'complete'
    assert manifest['comparison_completion_revision_id'] == json.loads((base_dir / 'manifest.json').read_text())['comparison_completion_revision_id']
    save('publication.json', {'release_id': release, 'base_release': BASE, 'published_at': timestamp(),
                            'renderer_version': 24, 'ordinary_publish_audit': 'passed',
                            'phase_one_gate': 'passed', 'phase_two_gate': 'passed', 'phase_three_complete_gate': 'passed',
                            'research_tables_unchanged': True, 'base_files_unchanged': before,
                            'acceptance_id': acceptance['id'], 'manifest': manifest})
    save('publication-progress.json', {'stage': 'complete', 'release_id': release, 'at': timestamp()})
    print(timestamp(), 'PUBLISHED', release, flush=True)


if __name__ == '__main__':
    main()
