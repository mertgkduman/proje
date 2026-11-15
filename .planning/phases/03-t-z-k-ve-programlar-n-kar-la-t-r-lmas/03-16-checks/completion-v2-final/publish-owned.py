"""Perform the one authorized production-local refresh in an owned workspace."""
import json
from pathlib import Path
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'src'))
import arsiv

base = '85b1a453ce2346a8ad0df325a2b73ae9'
if arsiv.current() != base:
    raise SystemExit('Current changed; reconcile before publication')
payload = json.loads((ROOT / 'data/comparisons/03-completion-review-v2.json').read_text(encoding='utf-8'))
work = None
try:
    work = arsiv.open_workspace()
    print('WORKSPACE', work, flush=True)
    arsiv.load_comparison(work, payload)
    print('COMPARISON_LOAD_OK', flush=True)
    release = arsiv.publish_release(work, refresh=True)
    print('REVIEWED_RELEASE_OK', release, flush=True)
finally:
    if work is not None:
        try:
            arsiv.assert_lock(work)
        except (OSError, ValueError):
            pass
        else:
            (arsiv.DATA / '.write.lock').unlink()
