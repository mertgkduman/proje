#!/usr/bin/env python3
"""Durable, sequential resumption of the interrupted Wave 1 unittest run."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / 'WAVE-1-TEST-RESUME.json').read_text())
EVENTS = HERE / 'resumed-test-events.jsonl'
RUN = os.environ.get('WAVE_RUN_ID', uuid.uuid4().hex)
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tests')]
os.chdir(ROOT)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def event(kind, **values):
    record = dict(event=kind, timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  run_id=RUN, release=CONTRACT['release_id'],
                  source_fingerprint=CONTRACT['code_fingerprint'], **values)
    with EVENTS.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + '\n')
        stream.flush()
        os.fsync(stream.fileno())

def identity():
    paths = subprocess.check_output(['git', 'ls-files', 'src', 'tests'], text=True).splitlines()
    actual = {p: digest(ROOT / p) for p in paths}
    fingerprint = hashlib.sha256(json.dumps(actual, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    release = json.loads((ROOT / 'data/current.json').read_text())['release_id']
    manifest = digest(ROOT / 'data/releases' / release / 'manifest.json')
    mismatches = {p: {'expected': CONTRACT['source_file_sha256'].get(p), 'actual': actual.get(p)}
                  for p in sorted(set(actual) | set(CONTRACT['source_file_sha256']))
                  if actual.get(p) != CONTRACT['source_file_sha256'].get(p)}
    result = dict(release=release, manifest_sha256=manifest, code_fingerprint=fingerprint, changed_files=mismatches)
    if (mismatches or fingerprint != CONTRACT['code_fingerprint'] or release != CONTRACT['release_id']
            or manifest != CONTRACT['manifest_sha256']):
        raise RuntimeError('identity mismatch: ' + json.dumps(result, sort_keys=True))
    return result

def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item

def loader_check(ids):
    suite = unittest.defaultTestLoader.loadTestsFromNames(ids)
    found = [test.id() for test in flatten(suite)]
    if found != ids or len(found) != len(set(found)) or not found:
        raise RuntimeError('loader mismatch: expected=' + repr(ids) + ' found=' + repr(found))
    return suite

class Result(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        event('test', test_id=test.id(), outcome='success', batch=os.environ['WAVE_BATCH'])
    def addFailure(self, test, err):
        super().addFailure(test, err)
        event('test', test_id=test.id(), outcome='failure', batch=os.environ['WAVE_BATCH'], detail=self._exc_info_to_string(err, test))
    def addError(self, test, err):
        super().addError(test, err)
        event('test', test_id=test.id(), outcome='error', batch=os.environ['WAVE_BATCH'], detail=self._exc_info_to_string(err, test))
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        event('test', test_id=test.id(), outcome='skip', batch=os.environ['WAVE_BATCH'], detail=reason)
    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        event('test', test_id=test.id(), outcome='expected_failure', batch=os.environ['WAVE_BATCH'])
    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        event('test', test_id=test.id(), outcome='unexpected_success', batch=os.environ['WAVE_BATCH'])

def read_events():
    if not EVENTS.exists():
        return []
    return [json.loads(line) for line in EVENTS.read_text().splitlines()]

def main():
    all_ids = CONTRACT['all_test_ids']
    passed = CONTRACT['passed_test_ids']
    remaining = CONTRACT['remaining_test_ids']
    batches = CONTRACT['module_batches']
    heavy = CONTRACT['isolated_heavy_test']
    listed = [x for ids in batches.values() for x in ids] + [heavy]
    if (len(all_ids) != len(set(all_ids)) or len(passed) != len(set(passed)) or
        set(passed) & set(remaining) or set(passed) | set(remaining) != set(all_ids) or
        len(listed) != len(set(listed)) or set(listed) != set(remaining)):
        raise RuntimeError('invalid contract accounting')
    if digest(HERE / CONTRACT['original_full_log']) != CONTRACT['original_full_log_sha256']:
        raise RuntimeError('original log hash mismatch')
    identity()
    discovered = [t.id() for t in flatten(unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_*.py'))]
    if len(discovered) != len(set(discovered)) or set(discovered) != set(all_ids):
        raise RuntimeError('discovery mismatch')
    event('supervisor_start', discovered=len(discovered), original_successes=len(passed), remaining=len(remaining))
    # Recover an interrupted batch only after its process has disappeared and
    # the release and all tracked files still match the pre-batch identity.
    events = read_events()
    ended = {(e['run_id'], e['batch']) for e in events if e['event'] == 'batch_end'}
    for start in [e for e in events if e['event'] == 'batch_start' and (e['run_id'], e['batch']) not in ended]:
        key = (start['run_id'], start['batch'])
        process = next((e for e in events if e['event'] == 'process_start' and (e['run_id'], e['batch']) == key), None)
        if process and Path('/proc', str(process['pid'])).exists():
            raise RuntimeError('interrupted batch process still exists: ' + str(process['pid']))
        identity()
        event('batch_recovered_after_interruption', original_run_id=key[0], batch=key[1], identity_ok=True,
              detail='No batch-end event; process absent; matching identity verified on recovery. Exit unknown.')
    valid_runs = {(e['run_id'], e['batch']) for e in events if e['event'] == 'batch_end' and e['identity_ok']}
    valid_runs.update((e['original_run_id'], e['batch']) for e in read_events()
                      if e['event'] == 'batch_recovered_after_interruption' and e['identity_ok'])
    credited = {e['test_id'] for e in events if e['event'] == 'test' and e['outcome'] == 'success'
                and (e['run_id'], e['batch']) in valid_runs and e['test_id'] in remaining}
    for name, original in list(batches.items()) + [('isolated_heavy', [heavy])]:
        ids = [x for x in original if x not in credited]
        if not ids:
            continue
        identity()
        loader_check(ids)
        batch = name + '-' + uuid.uuid4().hex[:8]
        env = dict(os.environ, WAVE_RUN_ID=RUN, WAVE_BATCH=batch)
        log = HERE / ('resume-' + batch + '.log')
        event('batch_start', batch=batch, ids=ids, count=len(ids), log=log.name)
        with log.open('w', encoding='utf-8') as stream:
            proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--child', *ids],
                                    stdout=stream, stderr=subprocess.STDOUT, env=env, start_new_session=True)
            event('process_start', batch=batch, pid=proc.pid, count=len(ids))
            try:
                code = proc.wait(timeout=CONTRACT['per_batch_timeout_seconds'])
                timed_out = False
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    code = proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    code = proc.wait()
            event('process_exit', batch=batch, pid=proc.pid, exit_code=code, timed_out=timed_out)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            identity()
            identity_ok = True
            mismatch = None
        except Exception as exc:
            identity_ok = False
            mismatch = str(exc)
        current = [e for e in read_events() if e.get('run_id') == RUN and e.get('batch') == batch and e['event'] == 'test']
        successes = [e['test_id'] for e in current if e['outcome'] == 'success']
        event('batch_end', batch=batch, exit_code=code, timed_out=timed_out, identity_ok=identity_ok,
              mismatch=mismatch, successes=len(successes), expected=len(ids))
        if not identity_ok or code != 0 or timed_out or len(current) != len(ids) or set(successes) != set(ids):
            raise RuntimeError('batch did not pass completely: ' + batch)
        credited.update(successes)
    if set(passed) | credited != set(all_ids):
        raise RuntimeError('coverage incomplete')
    identity()
    event('coverage_complete', total=len(all_ids), original_successes=len(passed), resumed_successes=len(credited), remaining=0)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--child':
        suite = loader_check(sys.argv[2:])
        result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
        sys.exit(0 if result.wasSuccessful() and not result.skipped and not result.expectedFailures else 1)
    try:
        main()
    except BaseException as exc:
        event('supervisor_error', detail=str(exc), traceback=traceback.format_exc())
        raise
