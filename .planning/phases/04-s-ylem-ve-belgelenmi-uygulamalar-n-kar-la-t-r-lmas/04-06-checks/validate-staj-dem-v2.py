"""10/4625 dilimini gerçek üç kapı ve görünürlük kontrolünden geçir."""
import importlib.util
import json
import os
import sqlite3
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[3]
job = os.environ['SLURM_JOB_ID']
spec = importlib.util.spec_from_file_location('tracer', here / 'tracer-validation.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
package, review = here / 'staj-dem-v2-draft.json', here / 'staj-dem-v2-review-draft.json'
assert mod.sha(package) == 'a2abfd368da20d88a3296cf72cedc42a3faf0f6ae92930901c6b5ae13b12b32b'
assert mod.sha(review) == 'e1f2512884d7bf10669be84c65ca726623d18227faee83482864db9b0bdf8426'
before = json.loads((root / 'data/practices/04-dem.json').read_text())
after = json.loads(package.read_text())
canon = lambda row: json.dumps(row, sort_keys=True, ensure_ascii=False)
for key in ('entries', 'scope_inventory'):
    assert {canon(x) for x in before[key]} <= {canon(x) for x in after[key]}
for key, rows in before['practice_records'].items():
    assert {canon(x) for x in rows} <= {canon(x) for x in after['practice_records'][key]}
mod.main(package, review, 'dem-staj-agenda-v2', '0406-staj-agenda-event', '0406-2025-224-relation', '')
receipt = json.loads((here / f'dem-staj-agenda-v2-{job}.json').read_text())
folder = Path(receipt['preview'])
assert json.loads((folder / 'manifest.json').read_text())['renderer_version'] == 31
records = json.loads((folder / 'records.json').read_text())
db = sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro', uri=True)
events = {x['id'] for x in after['practice_records']['practice_event']}
assert len(events) == 22
assert events <= {x['id'] for x in records['practice_event']}
assert all(db.execute('select 1 from practice_event where id=?', (x,)).fetchone() for x in events)
db.close()
html = (folder / 'index.html').read_text()
for prefix in ('party', 'comparison'):
    for kind, item, finding in (
        ('unmatched', '0406-staj-agenda-candidate', '0406-staj-agenda-finding'),
        ('unmatched', '0406-oct08-dem-candidate', '0406-oct08-dem-finding'),
        ('unmatched', '0406-oct08-yeniyol-candidate', '0406-oct08-yeniyol-finding'),
        ('practice', '0406-hakkari-selection-relation', '0406-hakkari-dispute-finding'),
        ('practice', '0406-101831-relation', '0406-101831-debate-f'),
    ):
        start = html.index(f'id="{prefix}-{kind}-{item}"')
        end = html.index('</article>', start)
        assert f'data-finding-id="{finding}"' in html[start:end]
print('TWENTY_TWO_EVENTS_AND_FINDINGS_BOTH_VIEWS_OK', flush=True)
