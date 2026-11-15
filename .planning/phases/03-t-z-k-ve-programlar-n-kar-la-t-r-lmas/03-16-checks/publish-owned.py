"""Publish exactly one reviewed local refresh; caller owns job and logs."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'src'))
import arsiv

expected_base = '27033583248b4951b3fe8e5fd6d77b9f'
if arsiv.current() != expected_base:
    raise SystemExit('Current changed; reconcile before publishing')
payload = json.loads((ROOT / 'data/comparisons/03-source-review.json').read_text(encoding='utf-8'))
work = None
try:
    work = arsiv.open_workspace()
    arsiv.load_comparison(work, payload)
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
