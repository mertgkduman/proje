"""Read-only replay of the exact failed candidate, with bounded memory."""
import datetime
import hashlib
import json
from pathlib import Path
import resource
import threading
import time
import traceback

import arsiv


DATA = Path('/tmp/tmphj4lx7ev/data')
RELEASE = 'a87bc0aadf3546f0b46ff376c6b6a622'
INPUTS = Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-fix/latest-api-final/prospective-inputs.json')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def snapshot():
    manifest = json.loads(INPUTS.read_text())
    copy_root = Path(manifest['copy_root'])
    failures = []
    for item in manifest['inputs']:
        path = copy_root / item['path']
        if not path.is_file() or digest(path) != item['sha256']:
            failures.append(item['path'])
    folder = DATA / 'releases' / RELEASE
    return {'inputs_count': len(manifest['inputs']), 'input_mismatches': failures,
            'candidate_sha256': {p.name: digest(p) for p in sorted(folder.iterdir()) if p.is_file()},
            'current_sha256': digest(DATA / 'current.json')}


def emit(**values):
    print(json.dumps(values, ensure_ascii=False, sort_keys=True), flush=True)


def main():
    before = snapshot()
    emit(stage='before', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), snapshot=before)
    if before['inputs_count'] != 2251 or before['input_mismatches'] or len(before['candidate_sha256']) != 4:
        raise RuntimeError('Unexpected retained inputs or candidate files')
    limit = 4 * 1024 ** 3
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    stop = threading.Event()
    start = time.monotonic()

    def sample():
        while not stop.wait(30):
            emit(stage='running', elapsed_seconds=round(time.monotonic() - start, 2),
                 peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

    monitor = threading.Thread(target=sample, daemon=True)
    monitor.start()
    arsiv.DATA = DATA
    error = None
    try:
        result = arsiv.audit_release(RELEASE)
        if result != RELEASE:
            raise AssertionError('Unexpected release returned')
    except BaseException:
        error = traceback.format_exc()
    finally:
        stop.set()
        monitor.join()
    elapsed = time.monotonic() - start
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    after = snapshot()
    emit(stage='after', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         elapsed_seconds=round(elapsed, 3), peak_rss_kib=peak, rlimit_as_bytes=limit,
         snapshot=after, unchanged=after == before, error=error)
    if error or after != before:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
