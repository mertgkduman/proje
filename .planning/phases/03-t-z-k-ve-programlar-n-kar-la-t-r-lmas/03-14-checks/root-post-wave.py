"""Read-only release spot checks and the configured post-wave code gate."""
import datetime
import hashlib
import json
import pathlib
import re
import sqlite3
import subprocess
import traceback

ROOT = pathlib.Path('/hpc/group/pfisterlab/mg551/storage/proje')
OUT = ROOT / '.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-14-checks'
GSD = '/hpc/home/mg551/.codex/gsd-core/bin/gsd-tools.cjs'
RID = 'b513965558094e338a941be90a1960a4'
BASE = 'ae42ae1897864fda810b033ce3ac1e8f'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def gate(name, command, timeout):
    log = OUT / ('root-' + name + '.log')
    with log.open('wb') as output:
        run = subprocess.run(['node', GSD, 'run-with-timeout', str(timeout), '--',
                              'bash', '-c', command], cwd=ROOT,
                             stdin=subprocess.DEVNULL, stdout=output,
                             stderr=subprocess.STDOUT, check=False)
    (OUT / ('root-' + name + '.exit')).write_text(str(run.returncode) + '\n')
    text = log.read_text(errors='replace')
    counts = re.findall(r'TESTS_OK count=(\d+)', text)
    result = {'command': command, 'timeout_seconds': timeout,
              'exit': run.returncode, 'log': str(log),
              'test_count': int(counts[-1]) if counts else None}
    print(json.dumps({name: result}), flush=True)
    return result


result = {'release': RID, 'base_plan_13_release': BASE,
          'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
try:
    bundle = ROOT / 'data/releases' / RID
    old_bundle = ROOT / 'data/releases' / BASE
    manifest, records = read(bundle / 'manifest.json'), read(bundle / 'records.json')
    old_manifest, old = read(old_bundle / 'manifest.json'), read(old_bundle / 'records.json')
    assert read(ROOT / 'data/current.json')['release_id'] == RID
    assert (manifest['renderer_version'], manifest['data_schema_version'],
            manifest['comparison_synthesis_contract_version'],
            manifest['comparison_taxonomy_version'], manifest['comparison_stage']) == (18, 6, 2, 4, 'complete')
    assert manifest['phase2_delivery'] == old_manifest['phase2_delivery']
    selected = {table: [item for item in records[table] if item['taxonomy_version'] == 4]
                for table in ['comparison_topic', 'comparison_row', 'comparison_synthesis']}
    assert [len(selected[t]) for t in selected] == [305, 4935, 854]
    assert len({r['party_id'] for r in selected['comparison_row']}) == 9
    assert not any(r['state'] == 'not_researched' for r in selected['comparison_row'])
    assert {s['topic_id'] for s in selected['comparison_synthesis']} == {t['topic_id'] for t in selected['comparison_topic']}
    preserved = {}
    for table in ['document', 'document_version', 'source_attribution', 'archive_view',
                  'passage', 'manual_passage', 'party_identity_revision', 'scope_party']:
        before = {canonical(x) for x in old[table]}
        after = {canonical(x) for x in records[table]}
        assert before <= after, table
        preserved[table] = {'before': len(before), 'after': len(after), 'lost': 0}
    original_checks = []
    for version in records['document_version']:
        rel = pathlib.Path(version['original_path'])
        candidates = [bundle / rel, ROOT / 'data' / rel]
        path = next((x for x in candidates if x.is_file()), None)
        assert path is not None, version['id']
        actual = sha(path)
        assert actual == version['sha256'], version['id']
        original_checks.append({'version_id': version['id'], 'sha256': actual})
    expected = {
        'src/arsiv.py': '72a15137b0d8e4b7890aefd95ae5f61574393dd57383fdfca6630f4f1d0f552b',
        'tests/test_comparison_content.py': 'e3061c430356095f079f0149a5bba494936b610ac0ecb08c2457cccae4caf9ba',
        'src/rapor_v16.css': 'bbf86a55a6134df843aa7acd8644b27daf6039e89239700d08e5b3addbd9c389',
        'src/rapor_v17.py': '471b4396b20c6793a28bae1b998be9604b99746e2bd8d3c995103f40d49b7e3e',
    }
    actual_hashes = {name: sha(ROOT / name) for name in expected}
    assert actual_hashes == expected
    with sqlite3.connect('file:' + str(bundle / 'records.sqlite3') + '?mode=ro', uri=True) as conn:
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert not conn.execute('PRAGMA foreign_key_check').fetchall()
    receipts = {}
    for name in ['final-publish', 'final-check-backfill', 'final-check-synthesis',
                 'final-audit-3', 'final-audit-2', 'content-final']:
        stem = pathlib.Path('/tmp') / ('gsd-0314-' + name)
        assert stem.with_suffix('.exit').read_text().strip() == '0', name
        receipts[name] = {'exit': 0, 'log_sha256': sha(stem.with_suffix('.log'))}
    result.update({'static_checks': 'passed', 'selected_counts': {t: len(v) for t, v in selected.items()},
                   'phase2_delivery_unchanged': True, 'preserved_tables': preserved,
                   'original_versions_checked': original_checks,
                   'code_and_frozen_hashes': actual_hashes, 'executor_receipts': receipts})
    print('ROOT_STATIC_CHECKS_OK', flush=True)
    result['build'] = gate('build', 'python3 -m compileall -q src tests', 300)
    assert result['build']['exit'] == 0
    result['test'] = gate('tests', 'python3 tests/run.py', 1800)
    assert result['test']['exit'] == 0
    assert result['test']['test_count'] and result['test']['test_count'] > 27
    result['status'] = 'passed'
except BaseException as error:
    result['status'] = 'failed'
    result['error'] = repr(error)
    result['traceback'] = traceback.format_exc()
    print(result['traceback'], flush=True)
finally:
    result['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (OUT / 'root-post-wave.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'root-post-wave.exit').write_text('0\n' if result['status'] == 'passed' else '1\n')
raise SystemExit(0 if result['status'] == 'passed' else 1)
