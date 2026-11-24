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
package, review = here / 'sivas-2879-dem-draft.json', here / 'sivas-2879-dem-review-draft.json'
assert mod.sha(package) == 'ee7b2a10cee56b2c8ee4babf59fb8f2589597eab1103a8337a93e47593a18ee2'
assert mod.sha(review) == 'd2eac1dbbaa3fd198644cc3443afff90cdeb729e840fcfb1493261a0b6cbc39d'
before = json.loads((root / 'data/practices/04-dem.json').read_text())
after = json.loads(package.read_text())
canon = lambda row: json.dumps(row, sort_keys=True, ensure_ascii=False)
for key in ('entries', 'scope_inventory'):
    assert {canon(x) for x in before[key]} <= {canon(x) for x in after[key]}
scope_id = 'practice-32598cee77548f2dce224908e63dc9005f9de70be0fff59b0b4990064ad650ae'
prior_scope = next(x for x in before['practice_records']['practice_scope_v2'] if x['id'] == scope_id)
updated_scope = next(x for x in after['practice_records']['practice_scope_v2'] if x['id'] == scope_id)
assert updated_scope == dict(prior_scope, boundary_reason=prior_scope['boundary_reason']+' Ayrıca 1 Temmuz 2025 10/2879 başvurusu incelendi; önceki söylem ve dosya sonucu araştırması açıktır.')
for key, rows in before['practice_records'].items():
    retained = [x for x in rows if key != 'practice_scope_v2' or x['id'] != scope_id]
    assert {canon(x) for x in retained} <= {canon(x) for x in after['practice_records'][key]}
mod.main(package, review, 'dem-sivas-2879', '0406-sivas-2879-event', '0406-2025-224-relation', '')
receipt = json.loads((here / f'dem-sivas-2879-{job}.json').read_text())
folder = Path(receipt['preview'])
assert json.loads((folder / 'manifest.json').read_text())['renderer_version'] == 31
records = json.loads((folder / 'records.json').read_text())
db = sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro', uri=True)
events = {x['id'] for x in after['practice_records']['practice_event']}
assert len(events) == 75
assert events <= {x['id'] for x in records['practice_event']}
assert all(db.execute('select 1 from practice_event where id=?', (x,)).fetchone() for x in events)
db.close()
html = (folder / 'index.html').read_text()
for prefix in ('party', 'comparison'):
    start = html.index(f'id="{prefix}-unmatched-0406-sivas-2879-candidate"')
    end = html.index('</article>', start)
    assert 'data-finding-id="0406-sivas-2879-finding"' in html[start:end]
    for n in (*range(1, 21), 'gecici1', 'gecici2', '14-anayasa'):
        candidate = f'0406-4114-madde{n}-candidate'
        finding = f'0406-4114-madde{n}-finding'
        a = html.index(f'id=\"{prefix}-unmatched-{candidate}\"')
        b = html.index('</article>', a)
        assert f'data-finding-id=\"{finding}\"' in html[a:b]
    start = html.index(f'id="{prefix}-unmatched-0406-sap-2882-candidate"')
    end = html.index('</article>', start)
    assert 'data-finding-id="0406-sap-2882-finding"' in html[start:end]
    start = html.index(f'id="{prefix}-unmatched-0406-textile-2881-candidate"')
    end = html.index('</article>', start)
    assert 'data-finding-id="0406-textile-2881-finding"' in html[start:end]
    for number in ('8', '9', '10', '11'):
        start = html.index(f'id="{prefix}-unmatched-0406-iklim-102-{number}-candidate"')
        end = html.index('</article>', start)
        assert f'data-finding-id="0406-iklim-102-{number}-finding"' in html[start:end]
    for number in ('5', '6', '7'):
        start = html.index(f'id="{prefix}-unmatched-0406-iklim-101-{number}-candidate"')
        end = html.index('</article>', start)
        assert f'data-finding-id="0406-iklim-101-{number}-finding"' in html[start:end]
    for number in ('12', '13'):
        start = html.index(f'id="{prefix}-unmatched-0406-iklim-103-{number}-candidate"')
        end = html.index('</article>', start)
        assert f'data-finding-id="0406-iklim-103-{number}-finding"' in html[start:end]
    for number in ('14', '15', '16'):
        start = html.index(f'id="{prefix}-unmatched-0406-iklim-103-{number}-candidate"')
        end = html.index('</article>', start)
        assert f'data-finding-id="0406-iklim-103-{number}-finding"' in html[start:end]
    for number in ('2880', '2883'):
        start = html.index(f'id="{prefix}-unmatched-0406-sivas-{number}-candidate"')
        end = html.index('</article>', start)
        assert f'data-finding-id="0406-sivas-{number}-finding"' in html[start:end]
    for name in ('17', '18', 'gecici1', 'gecici2', '19', '20'):
        start = html.index(f'id="{prefix}-unmatched-0406-iklim-gk-{name}-candidate"')
        end = html.index('</article>', start)
        assert f'data-finding-id="0406-iklim-gk-{name}-finding"' in html[start:end]
    for name in ('akin', 'kordu', 'koca'):
        start = html.index(f'id="{prefix}-unmatched-0406-iklim-final-candidate"')
        end = html.index('</article>', start)
        assert f'data-finding-id="0406-iklim-final-{name}-finding"' in html[start:end]
    for kind, item, finding in (
        ('unmatched', '0406-2026-pm-myk-myk-candidate', '0406-2026-pm-myk-myk-finding'),
        ('unmatched', '0406-2026-pm-myk-kadin-candidate', '0406-2026-pm-myk-kadin-finding'),
        ('unmatched', '0406-2026-congress-candidate', '0406-2026-congress-finding'),
        ('unmatched', '0406-dem-teacher-4314-candidate', '0406-dem-teacher-4314-finding'),
        ('unmatched', '0406-nov03-4961-candidate', '0406-nov03-4961-finding'),
        ('unmatched', '0406-nov03-genelgorusme-candidate', '0406-nov03-genelgorusme-finding'),
        ('unmatched', '0406-staj-agenda-candidate', '0406-staj-agenda-finding'),
        ('unmatched', '0406-oct08-dem-candidate', '0406-oct08-dem-finding'),
        ('unmatched', '0406-oct08-yeniyol-candidate', '0406-oct08-yeniyol-finding'),
        ('practice', '0406-hakkari-selection-relation', '0406-hakkari-dispute-finding'),
        ('practice', '0406-101831-relation', '0406-101831-debate-f'),
    ):
        start = html.index(f'id="{prefix}-{kind}-{item}"')
        end = html.index('</article>', start)
        assert f'data-finding-id="{finding}"' in html[start:end]
print('SEVENTY_FIVE_EVENTS_AND_FINDINGS_BOTH_VIEWS_OK', flush=True)
