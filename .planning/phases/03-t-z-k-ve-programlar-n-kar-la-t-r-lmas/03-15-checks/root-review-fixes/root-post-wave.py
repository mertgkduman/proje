"""Root release spot checks and the configured post-wave regression gate."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import time
import traceback
from urllib.parse import urldefrag

ROOT = Path('/hpc/group/pfisterlab/mg551/storage/proje')
EVIDENCE = ROOT / '.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-15-checks'
OUT = EVIDENCE / 'root-review-fixes'
GSD = '/hpc/home/mg551/.codex/gsd-core/bin/gsd-tools.cjs'
RID = '27033583248b4951b3fe8e5fd6d77b9f'
BASE = 'b513965558094e338a941be90a1960a4'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def function(source, name):
    return ast.dump(next(n for n in ast.parse(source).body
                         if isinstance(n, ast.FunctionDef) and n.name == name))


def gate(name, command, timeout, environment):
    log = OUT / ('root-' + name + '.log')
    with log.open('wb') as stream:
        run = subprocess.run(['node', GSD, 'run-with-timeout', str(timeout), '--',
                              'bash', '-c', command], cwd=ROOT, env=environment,
                             stdin=subprocess.DEVNULL, stdout=stream,
                             stderr=subprocess.STDOUT, check=False)
    (OUT / ('root-' + name + '.exit')).write_text(str(run.returncode) + '\n')
    counts = re.findall(r'TESTS_OK count=(\d+)', log.read_text(errors='replace'))
    result = {'command': command, 'timeout_seconds': timeout, 'exit': run.returncode,
              'log': str(log), 'test_count': int(counts[-1]) if counts else None}
    print(json.dumps({name: result}), flush=True)
    return result


# Do not start even the build until the parent has durably recorded this PID.
for _ in range(100):
    run_record = read(OUT / 'root-post-wave.run.json')
    if run_record.get('pid') == os.getpid():
        break
    time.sleep(.1)
else:
    raise RuntimeError('Parent PID/input handshake missing')

result = {'release': RID, 'data_base': BASE, 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'git_head': run_record['git_head'], 'run_token': run_record['token']}
try:
    assert read(ROOT / 'data/current.json')['release_id'] == RID
    assert not (ROOT / 'data/.write.lock').exists()
    bundle, old_bundle = [ROOT / 'data/releases' / x for x in (RID, BASE)]
    manifest, records = read(bundle / 'manifest.json'), read(bundle / 'records.json')
    old_manifest, old_records = read(old_bundle / 'manifest.json'), read(old_bundle / 'records.json')
    assert (manifest['renderer_version'], manifest['data_schema_version'],
            manifest['comparison_taxonomy_version'], manifest['comparison_stage'],
            manifest['comparison_synthesis_contract_version']) == (22, 6, 4, 'complete', 2)
    assert manifest['phase2_delivery'] == old_manifest['phase2_delivery']
    assert {k: v for k, v in records.items() if k != 'release_id'} == {
        k: v for k, v in old_records.items() if k != 'release_id'}
    assert sha(bundle / 'records.sqlite3') == sha(old_bundle / 'records.sqlite3')
    selected = {name: [r for r in records[name] if r['taxonomy_version'] == 4]
                for name in ('comparison_topic', 'comparison_row', 'comparison_synthesis')}
    assert [len(selected[n]) for n in selected] == [305, 4935, 854]
    assert len({r['party_id'] for r in selected['comparison_row']}) == 9
    assert not any(r['state'] == 'not_researched' for r in selected['comparison_row'])
    originals = []
    for version in records['document_version']:
        path = ROOT / 'data' / version['original_path']
        assert sha(path) == version['sha256'], version['id']
        originals.append({'version_id': version['id'], 'sha256': version['sha256']})
    frozen = {'src/rapor_v17.py': '471b4396b20c6793a28bae1b998be9604b99746e2bd8d3c995103f40d49b7e3e',
              'src/rapor_v18.py': 'cec0e1cfac3b1d3943c1155d4b784d5b2a65ac6015c54d8615976f085cdbd5df',
              'src/rapor_v19.py': read(EVIDENCE / 'publish-run.json')['inputs']['src/rapor.py'],
              'src/rapor_v16.css': 'bbf86a55a6134df843aa7acd8644b27daf6039e89239700d08e5b3addbd9c389',
              'src/rapor_v19.css': read(EVIDENCE / 'publish-run.json')['inputs']['src/rapor_v19.css'],
              'src/rapor_v20.py': '2cceca388f5d4c418491763e7bd8529cb491e770f989d42b55beb8ff614f7ace',
              'src/rapor_v21.py': 'd24789b22c1b0d0cb11c13aa1d50ac114e0492087df0fdaf8d209bef296b4bd7'}
    assert {name: sha(ROOT / name) for name in frozen} == frozen
    audit_inputs = read(EVIDENCE / 'audits-v22-inputs.json')
    assert {name: sha(ROOT / name) for name in audit_inputs['hashes']} == audit_inputs['hashes']
    receipts = {}
    nav = read(ROOT / 'data/comparisons/03-navigation-checks.json')
    assert (nav['release_id'], nav['report_sha256'], nav['records_sha256']) == (
        RID, sha(bundle / 'index.html'), sha(bundle / 'records.json'))
    assert {(r['scheme'], r['width']) for r in nav['results']} == {
        (scheme, width) for scheme in ('file', 'http') for width in (360, 1365)}
    for row in nav['results']:
        assert row['checks'] == '1' * 19 and row['archiveExcerptFound']
        assert urldefrag(row['requested'])[0] == urldefrag(row['actual'])[0]
        assert '/releases/' + RID + '/index.html' in row['actual']
        assert row['archiveActual'] == row['archiveRequested'] == row['archiveUrl']
    for row in nav['historical_reproduction']:
        assert row['reproduced'] and sha(ROOT / 'data/releases' / row['release_id'] / 'index.html') == row['html_sha256']
    for row in nav['screenshots']:
        assert sha(ROOT / row['file']) == row['sha256']
    assert "ROOT / '.planning" not in (ROOT / 'tests/test_comparison_navigation.py').read_text()
    assert (ROOT / 'tests/comparison_navigation.cjs').is_file()
    with sqlite3.connect('file:' + str(bundle / 'records.sqlite3') + '?mode=ro', uri=True) as conn:
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert not conn.execute('PRAGMA foreign_key_check').fetchall()
    hooks = []
    for check in ('verify.schema-drift', 'verify.codebase-drift', 'ui.safety-gate'):
        run = subprocess.run(['node', GSD, 'check', check, '03', '--raw'], cwd=ROOT, text=True, capture_output=True)
        value = json.loads(run.stdout)
        assert run.returncode == 0 and not value.get('block', False), (check, value)
        hooks.append({'query': check, 'exit': run.returncode, 'result': value})
    result.update(static_checks='passed', selected_counts={k: len(v) for k, v in selected.items()},
                  source_records_identical_to_base=True, sqlite_identical_to_base=True,
                  phase2_delivery_unchanged=True, original_versions_checked=originals,
                  frozen_hashes=frozen, audit_receipts=receipts, wave_post_hooks=hooks,
                  exact_file_navigation=True, screenshots_reviewed_by_root=['screenshots-v22/navigation-row-360.png', 'screenshots-v22/navigation-topic-1365.png'])
    print('ROOT_STATIC_CHECKS_OK', flush=True)
    environment = dict(os.environ)
    environment.update(NAV_REPORT=str(bundle / 'index.html'), NAV_RECORDS=str(bundle / 'records.json'),
                       NAV_EVIDENCE=str(OUT / 'root-regression-navigation.json'), ARSIV_MODULE=str(ROOT / 'src/arsiv.py'))
    result['build'] = gate('build', 'python3 -m compileall -q src tests', 300, environment)
    assert result['build']['exit'] == 0
    result['test'] = gate('tests', run_record['test_command'], run_record['timeout_seconds'], environment)
    assert result['test']['exit'] == 0
    assert result['test']['test_count'] and result['test']['test_count'] > 27
    audit_run = read(EVIDENCE / 'audits-v22-run.json')
    assert audit_run['release'] == RID
    for name, marker in [('phase2', 'PHASE2_AUDIT_OK'), ('phase3', 'PHASE3_AUDIT_OK')]:
        job = audit_run['runs'][name]
        assert Path(job['exit']).read_text().strip() == '0', name
        log = Path(job['log'])
        assert marker + ' ' + RID in log.read_text(), name
        receipts[name] = {'exit': 0, 'log': str(log), 'log_sha256': sha(log)}
    result['audit_receipts'] = receipts
    assert {name: sha(ROOT / name) for name in run_record['code_hashes']} == run_record['code_hashes']
    assert read(ROOT / 'data/current.json')['release_id'] == RID
    result['status'] = 'passed'
except BaseException as error:
    result.update(status='failed', error=repr(error), traceback=traceback.format_exc())
    print(result['traceback'], flush=True)
finally:
    result['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (OUT / 'root-post-wave.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'root-post-wave.exit').write_text('0\n' if result['status'] == 'passed' else '1\n')
raise SystemExit(0 if result['status'] == 'passed' else 1)
