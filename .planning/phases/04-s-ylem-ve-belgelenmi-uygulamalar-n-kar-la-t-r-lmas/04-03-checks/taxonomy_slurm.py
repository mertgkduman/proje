#!/usr/bin/env python3
"""Run the one memory-intensive taxonomy ID in its own allocation."""
import datetime, hashlib, json, os, signal, subprocess, sys, traceback, uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CONTRACT = json.loads((HERE / 'fresh-gate-contract.json').read_text())
EVENTS = HERE / 'fresh-gate-events.jsonl'
TEST = 'test_completion_coverage.CompletionCoverageTest.test_same_taxonomy_sourced_revision_round_trip'
os.chdir(ROOT)

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def event(kind, **kw):
    with EVENTS.open('a', encoding='utf-8') as f:
        f.write(json.dumps(dict(event=kind, time=datetime.datetime.now(datetime.timezone.utc).isoformat(), **kw), sort_keys=True) + '\n')
        f.flush(); os.fsync(f.fileno())
def write(path, value):
    with path.open('w') as f: f.write(str(value) + '\n'); f.flush(); os.fsync(f.fileno())
def identity():
    files = {p: digest(ROOT / p) for p in subprocess.check_output(['git', 'ls-files', 'src', 'tests'], text=True).splitlines()}
    release = json.loads((ROOT / 'data/current.json').read_text())['release_id']
    folder = ROOT / 'data/releases' / release
    manifest_data = json.loads((folder / 'manifest.json').read_text())
    if set(manifest_data['files']) != {'records.sqlite3', 'records.json', 'index.html'}: raise RuntimeError('manifest file set mismatch')
    release_files = {p: digest(folder / p) for p in manifest_data['files']}
    if release_files != manifest_data['files']: raise RuntimeError('release file digest mismatch')
    if release_files['records.sqlite3'] != '9151c3055f2d53572b9b116ac6799b0a6cfa10d0ca9d7431dc6787ad15c68f5b':
        raise RuntimeError('canonical DB baseline mismatch')
    return dict(files=files, fingerprint=hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                release=release, manifest=digest(folder / 'manifest.json'), pointer=digest(ROOT / 'data/current.json'), release_files=release_files)
def main():
    expected = {k: v for k, v in CONTRACT['identity'].items() if k not in ('fixture', 'pending_fixture_manifest')}
    before = identity()
    if {k: before[k] for k in expected} != expected or CONTRACT['ids'].count(TEST) != 1: raise RuntimeError('pre-batch contract mismatch')
    batch = uuid.uuid4().hex
    log = HERE / ('fresh-' + batch + '.log')
    event('batch_start', batch=batch, name=TEST, ids=[TEST], identity=before, log=log.name,
          allocation='slurm', fixture_scope='not used by this test')
    env = dict(os.environ, GATE_BATCH=batch)
    with log.open('w') as f:
        proc = subprocess.Popen([sys.executable, str(HERE / 'fresh_gate.py'), '--child', TEST], stdout=f, stderr=subprocess.STDOUT, env=env, start_new_session=True)
        event('process_start', batch=batch, pid=proc.pid, allocation='slurm')
        try: code = proc.wait(timeout=10800); timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True; os.killpg(proc.pid, signal.SIGTERM)
            try: code = proc.wait(timeout=10)
            except subprocess.TimeoutExpired: os.killpg(proc.pid, signal.SIGKILL); code = proc.wait()
        f.flush(); os.fsync(f.fileno())
    write(HERE / ('fresh-' + batch + '.exit'), code)
    after = identity(); okay = before == after and {k: after[k] for k in expected} == expected
    entries = [json.loads(line) for line in EVENTS.read_text().splitlines()]
    outcomes = [x for x in entries if x['event'] == 'test' and x.get('batch') == batch]
    event('batch_end', batch=batch, exit_code=code, timed_out=timed_out, identity_ok=okay,
          identity=after, outcomes=len(outcomes), allocation='slurm')
    if code or timed_out or not okay or len(outcomes) != 1 or outcomes[0]['test_id'] != TEST or outcomes[0]['outcome'] != 'success':
        raise RuntimeError('taxonomy allocation failed or inconclusive')

if __name__ == '__main__':
    try:
        main(); write(HERE / 'taxonomy-slurm-supervisor.exit', 0)
    except BaseException as exc:
        event('external_supervisor_error', detail=str(exc), traceback=traceback.format_exc())
        write(HERE / 'taxonomy-slurm-supervisor.exit', 1)
        raise
