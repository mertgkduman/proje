"""Continue task 2 only after its frozen input check succeeds."""
import datetime
import json
import os
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

root = Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas')
checks = root / '03-11-checks'
token, host, owner = uuid.uuid4().hex, socket.gethostname(), os.getpid()
expected_base = sys.argv[1]
(checks / 'program2-pipeline.run.json').write_text(json.dumps(dict(
    started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), host=host,
    owner_pid=owner, owner_token=token, expected_base=expected_base,
    action='wait for frozen check then task 2 pipeline')) + '\n')

def run(name, argv, marker=None):
    logfile = checks / (name + '.log')
    with logfile.open('wb') as log:
        child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
        (checks / (name + '.run.json')).write_text(json.dumps(dict(
            started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), host=host,
            owner_pid=owner, child_pid=child.pid, owner_token=token, argv=argv)) + '\n')
        code = child.wait()
    (checks / (name + '.exit')).write_text(str(code) + '\n')
    content = logfile.read_text(errors='replace')
    if code or marker and marker not in content:
        raise RuntimeError(f'{name} failed: exit={code}, expected marker={marker!r}')
    return content.strip()

def check_sha():
    result = subprocess.run(['sha256sum', '-c', str(checks / 'program2.sha256')],
                            stdin=subprocess.DEVNULL, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError('Frozen input SHA changed: ' + result.stdout + result.stderr)

try:
    while not (checks / 'program2-final-check.exit').exists():
        time.sleep(10)
    if (checks / 'program2-final-check.exit').read_text().strip() != '0' or 'COMPARISON_INPUT_OK' not in (checks / 'program2-final-check.log').read_text():
        raise RuntimeError('Final comparison-check did not pass; workspace not opened')
    subprocess.run(['bash', '/tmp/gsd-03-root-pin.sh'], check=True, stdin=subprocess.DEVNULL)
    check_sha()
    if json.loads(Path('data/current.json').read_text())['release_id'] != expected_base:
        raise RuntimeError('Current release changed before workspace creation')
    workspace = run('program2-workspace', ['python3', 'src/arsiv.py', 'workspace', '--scratch', '/tmp']).splitlines()[-1]
    if not workspace.startswith('/tmp/proje-work-'):
        raise RuntimeError('Unexpected workspace path: ' + workspace)
    check_sha()
    run('program2-load', ['python3', 'src/arsiv.py', 'comparison-load', '--workspace', workspace,
                          '--input', 'data/comparisons/03-saadet-program-2.json'], 'COMPARISON_LOAD_OK')
    check_sha()
    release = run('program2-publish', ['python3', 'src/arsiv.py', 'publish', '--workspace', workspace, '--refresh']).splitlines()[-1]
    if len(release) != 32 or any(c not in '0123456789abcdef' for c in release):
        raise RuntimeError('Unexpected release ID: ' + release)
    if json.loads(Path('data/current.json').read_text())['release_id'] != release:
        raise RuntimeError('Published release is not current')
    check_sha()
    run('program2-audit', ['python3', 'src/arsiv.py', 'audit', '--release', 'current', '--phase', '3', '--stage', 'partial'], 'PHASE3_AUDIT_OK')
    run('program2-report', ['python3', str(root / '03-08-checks/report-check.py'), release,
                             'data/comparisons/03-saadet-program-2.json'], 'REPORT_LINK_CHECK_OK')
    run('program2-report-previous', ['python3', str(root / '03-08-checks/report-check.py'), release,
                                      'data/comparisons/03-saadet-program-1.json'], 'REPORT_LINK_CHECK_OK')
    run('program2-phase2-audit', ['python3', 'src/arsiv.py', 'audit', '--release', 'current', '--phase', '2'], 'PHASE2_AUDIT_OK')
    check_sha()
    (checks / 'program2-pipeline.result.json').write_text(json.dumps(dict(status='pass', workspace=workspace,
        release=release, owner_pid=owner, owner_token=token, host=host)) + '\n')
except Exception as exc:
    (checks / 'program2-pipeline.result.json').write_text(json.dumps(dict(status='failed', error=str(exc),
        owner_pid=owner, owner_token=token, host=host)) + '\n')
    sys.exit(1)
