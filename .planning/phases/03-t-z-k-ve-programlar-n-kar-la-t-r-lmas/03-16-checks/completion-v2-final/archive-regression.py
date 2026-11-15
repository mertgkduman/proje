"""Archive the terminal full-regression result without modifying its evidence."""
import json
import os
from pathlib import Path
import re
import shutil

job = Path('/tmp/proje-phase3-final-regression-20261115T221331Z')
out = Path(__file__).resolve().parent.parent / 'final-regression'
handshake = json.loads((job / 'handshake.json').read_text())
try:
    os.kill(handshake['supervisor_pid'], 0)
except ProcessLookupError:
    pass
else:
    raise SystemExit('Supervisor still exists; do not archive an incomplete result')
if not (job / 'exit.json').exists() or not (job / 'post-input-integrity.json').exists():
    raise SystemExit('Terminal result or input-integrity result is missing')
for name in ('run.log', 'exit.json', 'post-input-integrity.json', 'handshake.json'):
    shutil.copyfile(job / name, out / name)
result = json.loads((job / 'exit.json').read_text())
integrity = json.loads((job / 'post-input-integrity.json').read_text())
matches = re.findall(r'TESTS_OK count=(\d+)', (job / 'run.log').read_text(errors='replace'))
passed = (result.get('exit_code') == 0 and result.get('status') == 'passed' and matches and
          int(matches[-1]) > 0 and int(matches[-1]) == result.get('test_count') and
          integrity.get('changed') == [] and integrity.get('unchanged_count') == 2255)
(out / 'STATUS.md').write_text(
    '# Pre-production full regression\n\n'
    + ('PASSED' if passed else 'FAILED OR INCOMPLETE')
    + '. The original production current was `85b1a453ce2346a8ad0df325a2b73ae9`; '
      'the suite includes the real isolated v2 adoption and API scenarios. '
      'This is not a post-publication run.\n\n'
    + 'Recorded result: `' + json.dumps(result, sort_keys=True) + '`. '
    + 'Captured input integrity: `' + json.dumps(integrity, sort_keys=True) + '`.\n')
if not passed:
    raise SystemExit('Full regression gate failed or input integrity was not established')
print('FULL_REGRESSION_GATE_OK', result['test_count'])
