#!/usr/bin/env python3
"""Fresh sequential regression; no interrupted or earlier results are credited."""
import collections, datetime, hashlib, json, os, signal, subprocess, sys, traceback, unittest, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
CONTRACT = HERE / 'fresh-gate-contract.json'
EVENTS = HERE / 'fresh-gate-events.jsonl'
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tests')]
os.chdir(ROOT)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, content):
    with path.open('w', encoding='utf-8') as f:
        f.write(content); f.flush(); os.fsync(f.fileno())

def event(kind, **kw):
    record = dict(event=kind, time=datetime.datetime.now(datetime.timezone.utc).isoformat(), **kw)
    with EVENTS.open('a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + '\n'); f.flush(); os.fsync(f.fileno())

def identity():
    paths = subprocess.check_output(['git', 'ls-files', 'src', 'tests'], text=True).splitlines()
    files = {p: digest(ROOT / p) for p in paths}
    release = json.loads((ROOT / 'data/current.json').read_text())['release_id']
    folder = ROOT / 'data/releases' / release
    manifest_data = json.loads((folder / 'manifest.json').read_text())
    if {p: digest(folder / p) for p in manifest_data['files']} != manifest_data['files']: raise RuntimeError('canonical release file digest mismatch')
    if digest(folder / 'records.sqlite3') != '9151c3055f2d53572b9b116ac6799b0a6cfa10d0ca9d7431dc6787ad15c68f5b': raise RuntimeError('canonical DB baseline mismatch')
    if (ROOT / 'data/.write.lock').exists(): raise RuntimeError('canonical writer lock present')
    return dict(files=files, fingerprint=hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                release=release, manifest=digest(ROOT / 'data/releases' / release / 'manifest.json'),
                pointer=digest(ROOT / 'data/current.json'))

def core(record):
    return {k: v for k, v in record.items() if k not in ('fixture', 'pending_fixture_manifest')}

def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite): yield from flatten(item)
        else: yield item

def load(ids):
    suite = unittest.defaultTestLoader.loadTestsFromNames(ids)
    found = [t.id() for t in flatten(suite)]
    if found != ids or not ids or len(ids) != len(set(ids)):
        raise RuntimeError('loader mismatch: ' + repr(found))
    return suite

class Result(unittest.TextTestResult):
    def record(self, test, outcome, detail=None):
        event('test', batch=os.environ['GATE_BATCH'], test_id=test.id(), outcome=outcome, detail=detail)
    def addSuccess(self, test): super().addSuccess(test); self.record(test, 'success')
    def addFailure(self, test, err): super().addFailure(test, err); self.record(test, 'failure', self._exc_info_to_string(err, test))
    def addError(self, test, err): super().addError(test, err); self.record(test, 'error', self._exc_info_to_string(err, test))
    def addSkip(self, test, reason): super().addSkip(test, reason); self.record(test, 'skip', reason)
    def addExpectedFailure(self, test, err): super().addExpectedFailure(test, err); self.record(test, 'expected_failure')
    def addUnexpectedSuccess(self, test): super().addUnexpectedSuccess(test); self.record(test, 'unexpected_success')

def main():
    now = identity()
    raw_ids = [t.id() for t in flatten(unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_*.py'))]
    multiplicity = {k: v for k, v in collections.Counter(raw_ids).items() if v > 1}
    discovered = list(dict.fromkeys(raw_ids))
    if not discovered: raise RuntimeError('discovery invalid')
    if CONTRACT.exists():
        contract = json.loads(CONTRACT.read_text())
        if now != core(contract['identity']) or discovered != contract['ids'] or multiplicity != contract['discovery_duplicates']: raise RuntimeError('contract identity or discovery mismatch')
    else:
        contract = dict(identity=now, ids=discovered, discovery_duplicates=multiplicity, raw_discovery_count=len(raw_ids), timeout=10800, earlier_credits=0)
        write(CONTRACT, json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    if os.environ.get('GATE_DISCOVERY_ONLY') == '1':
        return
    events = [json.loads(s) for s in EVENTS.read_text().splitlines()] if EVENTS.exists() else []
    started = {e['batch']: e for e in events if e['event'] == 'batch_start'}
    ended = {e['batch']: e for e in events if e['event'] == 'batch_end'}
    abandoned = {e['batch'] for e in events if e['event'] == 'batch_abandoned'}
    for b in started.keys() - ended.keys() - abandoned:
        process = next((e for e in events if e['event'] == 'process_start' and e['batch'] == b), None)
        if b != 'fd0afd4cd1ea4ded872bc86118b9dd2c': raise RuntimeError('unreconciled prior batch: ' + b)
        event('batch_abandoned', batch=b, reason='prior host and supervisor disappeared; no recorded batch exit or credit')
    credited = set()
    merge_fixture_sha = None
    for b, end in ended.items():
        if end['exit_code'] == 0 and not end['timed_out'] and end['identity_ok']:
            outcomes = [e for e in events if e['event'] == 'test' and e['batch'] == b]
            ids = started[b]['ids']
            if core(started[b]['identity']) != now or core(end['identity']) != now: raise RuntimeError('historic batch identity mismatch')
            log = HERE / ('fresh-' + b + '.log')
            exit_file = HERE / ('fresh-' + b + '.exit')
            if not log.is_file() or not exit_file.is_file() or exit_file.read_text().strip() != '0': raise RuntimeError('historic batch evidence missing')
            if 'fixture' in end['identity'] and (end['identity'] != contract['identity'] or started[b]['identity'] != contract['identity']): raise RuntimeError('historic fixture binding mismatch')
            if len(outcomes) != len(ids) or {e['test_id'] for e in outcomes if e['outcome'] == 'success'} != set(ids) or credited.intersection(ids):
                raise RuntimeError('invalid or duplicate credit')
            credited.update(ids)
            if end.get('merge_fixture_sha256'):
                merge_fixture_sha = end['merge_fixture_sha256']
            if started[b]['name'].endswith('.test_public_replay_preserves_accepted_r1_as_pending') and merge_fixture_sha != '444aecf81f9c0f33033f45eb16a95adcb8ecd6085d8c4db7a3c233c5d1bed601': raise RuntimeError('historic replay provenance missing')
    groups = {}
    for test_id in discovered:
        module = test_id.split('.')[0]
        isolated = module in ('test_practice_preview', 'test_practice_public_replay_negative', 'test_practice_pending_integration') or test_id.endswith('.test_same_taxonomy_sourced_revision_round_trip')
        key = test_id if isolated else module
        groups.setdefault(key, []).append(test_id)
    groups = sorted(groups.items(), key=lambda x: (0 if x[0].endswith('.test_public_merge_preserves_accepted_r1_as_pending') else
                                                  1 if x[0].endswith('.test_public_replay_preserves_accepted_r1_as_pending') else
                                                  4 if x[0].endswith('.test_same_taxonomy_sourced_revision_round_trip') else
                                                  2 if x[0].startswith('test_practice_') else 3, x[0]))
    event('supervisor_start', discovered=len(discovered), credited=len(credited))
    for name, ids in groups:
        ids = [x for x in ids if x not in credited]
        if not ids: continue
        if os.environ.get('GATE_EXTERNAL_TAXONOMY') == '1' and name.endswith('.test_same_taxonomy_sourced_revision_round_trip'):
            event('external_test_pending', name=name, ids=ids, reason='separate Slurm allocation required')
            continue
        if identity() != core(contract['identity']): raise RuntimeError('pre-batch identity mismatch')
        is_replay = name.endswith('.test_public_replay_preserves_accepted_r1_as_pending')
        if is_replay: raise RuntimeError('uncached replay requires a new bound merge; reconcile manually')
        load(ids)
        batch = uuid.uuid4().hex
        log = HERE / ('fresh-' + batch + '.log')
        event('batch_start', batch=batch, name=name, ids=ids, identity=now, log=log.name)
        env = dict(os.environ, GATE_BATCH=batch)
        with log.open('w', encoding='utf-8') as f:
            proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--child', *ids], stdout=f, stderr=subprocess.STDOUT, env=env, start_new_session=True)
            event('process_start', batch=batch, pid=proc.pid)
            try: code = proc.wait(timeout=contract['timeout']); timed_out = False
            except subprocess.TimeoutExpired:
                timed_out = True; os.killpg(proc.pid, signal.SIGTERM)
                try: code = proc.wait(timeout=10)
                except subprocess.TimeoutExpired: os.killpg(proc.pid, signal.SIGKILL); code = proc.wait()
            f.flush(); os.fsync(f.fileno())
        write(HERE / ('fresh-' + batch + '.exit'), str(code) + '\n')
        after = identity(); okay = after == core(contract['identity'])
        current = [json.loads(s) for s in EVENTS.read_text().splitlines()]
        outcomes = [e for e in current if e['event'] == 'test' and e['batch'] == batch]
        event('batch_end', batch=batch, exit_code=code, timed_out=timed_out, identity_ok=okay, identity=after, outcomes=len(outcomes),
              merge_fixture_sha256=merge_fixture_sha if name.endswith('.test_public_merge_preserves_accepted_r1_as_pending') else None)
        if code != 0 or timed_out or not okay or len(outcomes) != len(ids) or {e['test_id'] for e in outcomes if e['outcome'] == 'success'} != set(ids): raise RuntimeError('batch failed or inconclusive: ' + name)
        credited.update(ids)
    if credited != set(discovered): raise RuntimeError('coverage incomplete')
    event('coverage_complete', total=len(credited), identity=identity())

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--child':
        result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(load(sys.argv[2:]))
        sys.exit(0 if result.wasSuccessful() and not result.skipped and not result.expectedFailures else 1)
    try: main()
    except BaseException as exc:
        event('supervisor_error', detail=str(exc), traceback=traceback.format_exc()); raise
