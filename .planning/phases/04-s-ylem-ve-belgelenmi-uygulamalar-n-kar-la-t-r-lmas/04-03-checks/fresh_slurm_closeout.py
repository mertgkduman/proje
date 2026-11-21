"""Verify available regression evidence and run independent 04-03 audits."""
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote

from fresh_gate import CONTRACT, EVENTS, HERE, ROOT, core, identity

TAXONOMY = 'test_completion_coverage.CompletionCoverageTest.test_same_taxonomy_sourced_revision_round_trip'
OUT = Path('/tmp/gsd-04-03-tracer-preview')
ASSETS = {'index.html', 'records.json', 'records.sqlite3'}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_regression(contract, current, *, allow_pending_taxonomy=False):
    entries = [json.loads(line) for line in EVENTS.read_text().splitlines(keepends=True) if line.endswith("\n")]
    starts = {entry['batch']: entry for entry in entries if entry['event'] == 'batch_start'}
    passed = set()
    for end in entries:
        if end['event'] != 'batch_end' or end['exit_code'] != 0 or end['timed_out'] or not end['identity_ok']:
            continue
        batch = end['batch']
        start = starts[batch]
        ids = start['ids']
        results = [entry for entry in entries if entry['event'] == 'test' and entry['batch'] == batch]
        require(ids and len(ids) == len(results) == end['outcomes'], f'{batch}: test count mismatch')
        require({entry['test_id'] for entry in results if entry['outcome'] == 'success'} == set(ids), f'{batch}: failed test')
        require(len(set(ids)) == len(ids) and not passed.intersection(ids), f'{batch}: duplicate test credit')
        require((HERE / f'fresh-{batch}.exit').read_text().strip() == '0', f'{batch}: no true exit code')
        require('OK' in (HERE / start['log']).read_text().splitlines(), f'{batch}: no successful test log')
        for record in (start['identity'], end['identity']):
            core_record = core(record)
            release_files = core_record.pop('release_files', None)
            require(core_record == current, f'{batch}: source or canonical release mismatch')
            if 'fixture' in record:
                require(record == contract['identity'], f'{batch}: recorded fixture mismatch')
            if release_files is not None:
                expected = json.loads((ROOT / 'data/releases' / current['release'] / 'manifest.json').read_text())['files']
                require(release_files == expected, f'{batch}: actual release bytes mismatch')
        if TAXONOMY in ids:
            require(ids == [TAXONOMY] and end.get('allocation') == 'slurm', 'taxonomy evidence must be isolated')
            require((HERE / 'taxonomy-slurm-supervisor.exit').read_text().strip() == '0', 'taxonomy supervisor exit missing')
        passed.update(ids)
    expected_ids = set(contract['ids'])
    pending = expected_ids - passed
    unknown = passed - expected_ids
    if allow_pending_taxonomy and pending == {TAXONOMY} and not unknown:
        require(any(entry['event'] == 'external_test_pending' and entry['ids'] == [TAXONOMY] for entry in entries),
                'isolated taxonomy handoff missing')
        return len(passed)
    require(not pending and not unknown, f'Test coverage mismatch: {len(pending)} outstanding, {len(unknown)} unknown')
    return len(passed)


def run(job, name, args, marker=None):
    log = HERE / f'closeout-{job}-{name}.log'
    with log.open('x', encoding='utf-8') as stream:
        code = subprocess.call([sys.executable, *args], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
        stream.flush()
        os.fsync(stream.fileno())
    with (HERE / f'closeout-{job}-{name}.exit').open('x') as stream:
        stream.write(f'{code}\n')
        stream.flush()
        os.fsync(stream.fileno())
    require(code == 0, f'{name}: exit {code}')
    if marker:
        require(any(line.startswith(marker) for line in log.read_text().splitlines()), f'{name}: marker missing')


class RelativeSources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs if key == 'href' and value and value.startswith('../../'))


def preview_bundle(root):
    releases = list((root / 'releases').iterdir())
    require(len(releases) == 1, 'expected one preview release')
    release = releases[0]
    manifest_path = release / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    require(manifest.get('preview') is True and manifest['release_id'] == release.name, 'invalid preview manifest')
    require(set(manifest['files']) == ASSETS, 'incomplete preview release')
    require(all(sha(release / name) == checksum for name, checksum in manifest['files'].items()), 'preview bytes changed')
    report = (release / 'index.html').read_text()
    for view in ('party', 'comparison'):
        require(f'id="{view}-practice-tracer-relation-id"' in report, f'tracer missing: {view}')
    parser = RelativeSources()
    parser.feed(report)
    require(parser.links and all((release / unquote(link.split('#')[0])).is_file() for link in parser.links), 'missing local source link')
    return release, sha(manifest_path), len(parser.links)


def main():
    job = os.environ['SLURM_JOB_ID']
    contract = json.loads(CONTRACT.read_text())
    before = identity()
    require(before == core(contract['identity']), 'contract no longer matches current code/release')
    count = verify_regression(contract, before, allow_pending_taxonomy=True)
    print(f'Regression evidence at audit start: {count}/{len(contract["ids"])}', flush=True)
    require(not OUT.exists() and not OUT.is_symlink(), f'Preview path already exists: {OUT}')
    with tempfile.TemporaryDirectory(prefix='gsd-04-03-pycache-') as cache:
        run(job, 'build', ['-X', f'pycache_prefix={cache}', '-m', 'compileall', '-q', 'src', 'tests'])
    run(job, 'tracer', ['src/arsiv.py', 'practice-preview', '--input', 'data/practices/04-tracer.json',
                         '--inventory', 'data/practices/04-inventory.json', '--out', str(OUT)], 'PRACTICE_PREVIEW_OK ')
    release, manifest_sha, local_links = preview_bundle(OUT)
    artifact = ROOT / 'data/.staging' / f'gsd-04-03-tracer-preview-{job}'
    shutil.copytree(OUT, artifact)
    copied, copied_sha, copied_links = preview_bundle(artifact)
    require((copied.name, copied_sha, copied_links) == (release.name, manifest_sha, local_links), 'copied preview differs')
    print(f'Preserved audited preview: {copied}', flush=True)
    run(job, 'phase2', ['src/arsiv.py', 'audit', '--release', 'current', '--phase', '2'], f'PHASE2_AUDIT_OK {before["release"]}')
    run(job, 'phase3-complete', ['src/arsiv.py', 'audit', '--release', 'current', '--phase', '3', '--stage', 'complete'],
        f'PHASE3_AUDIT_OK {before["release"]}')
    require(identity() == before, 'canonical identity changed during closeout')
    result = dict(job=job, audits_ok=True, regression_credited_at_start=count,
                  regression_required=len(contract['ids']), source_test_fingerprint=before['fingerprint'],
                  canonical_release=before['release'], canonical_manifest=before['manifest'],
                  canonical_pointer=before['pointer'], preview_path=str(artifact),
                  preview_release=release.name, preview_manifest_sha256=manifest_sha, local_links=local_links)
    with (HERE / f'closeout-{job}.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    print('04-03 build, tracer and canonical audits passed', flush=True)


if __name__ == '__main__':
    main()
