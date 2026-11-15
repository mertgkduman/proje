"""Archive the actual API result and compare its captured input epoch."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil

root = Path.cwd()
job = Path('/tmp/proje-v2-api-final-20261115T200402Z')
out = Path(__file__).resolve().parent.parent / 'completion-v2-fix/latest-api-final'
exit_result = json.loads((job / 'exit.json').read_text())
prospective = json.loads((job / 'prospective-inputs.json').read_text())
copy = Path(prospective['copy_root'])
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
copy_changed, current_changed = [], []
for item in prospective['inputs']:
    rel = item['path']
    expected = item['sha256']
    if not (copy / rel).is_file() or sha(copy / rel) != expected:
        copy_changed.append(rel)
    if not (root / rel).is_file() or sha(root / rel) != expected:
        current_changed.append(rel)
for name in ('run.log', 'exit.json'):
    shutil.copyfile(job / name, out / name)
result = {'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'input_count': len(prospective['inputs']), 'copy_changed': copy_changed,
          'current_changed_since_capture': current_changed,
          'exit_code': exit_result['exit_code'], 'test': prospective['test'],
          'git_head_at_capture': prospective['git_head'], 'ended_utc': exit_result['ended_utc']}
(out / 'input-comparison.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
if exit_result['exit_code'] or copy_changed:
    raise SystemExit('API gate failed or its captured input copy changed')
print('API_GATE_OK', json.dumps(result))
