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
package, review = here / 'sivas-1568-dem-draft.json', here / 'sivas-1568-dem-review-draft.json'
assert mod.sha(package) == '78a74803dcde3d0f24c8b546f9f5fb5b41994da1f25126818a5e522fa48a18f7'
assert mod.sha(review) == '94234dad20e2b4402819ed834f907872040fd3d03ba614fe47cd0640f0966a1d'
before = json.loads((root / 'data/practices/04-dem.json').read_text())
after = json.loads(package.read_text())
canon = lambda row: json.dumps(row, sort_keys=True, ensure_ascii=False)
for key in ('entries', 'scope_inventory'):
    assert {canon(x) for x in before[key]} <= {canon(x) for x in after[key]}
scope_id = 'practice-32598cee77548f2dce224908e63dc9005f9de70be0fff59b0b4990064ad650ae'
prior_scope = next(x for x in before['practice_records']['practice_scope_v2'] if x['id'] == scope_id)
updated_scope = next(x for x in after['practice_records']['practice_scope_v2'] if x['id'] == scope_id)
assert updated_scope == dict(prior_scope, boundary_reason=prior_scope['boundary_reason']+' Ayrıca 2 Temmuz 2024 10/1568 esas kaydı ve 6131 grup gündemi incelendi; aynı günkü açıklamanın saat sırası ve esas dosya sonucu açıktır.')
for key, rows in before['practice_records'].items():
    retained = [x for x in rows if key != 'practice_scope_v2' or x['id'] != scope_id]
    assert {canon(x) for x in retained} <= {canon(x) for x in after['practice_records'][key]}
mod.main(package, review, 'dem-sivas-1568', '0406-sivas-1568-event', '0406-sivas-2024-2879-relation', '')
receipt = json.loads((here / f'dem-sivas-1568-{job}.json').read_text())
folder = Path(receipt['preview'])
assert json.loads((folder / 'manifest.json').read_text())['renderer_version'] == 31
records = json.loads((folder / 'records.json').read_text())
db = sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro', uri=True)
events = {x['id'] for x in after['practice_records']['practice_event']}
assert len(events) == 76
assert events <= {x['id'] for x in records['practice_event']}
assert all(db.execute('select 1 from practice_event where id=?', (x,)).fetchone() for x in events)

assert len([x for x in records['practice_relation'] if x['party_id']=='dem']) == 11
for number in ('2879', '2880'):
    row = db.execute('select event_id, result_finding_id from practice_relation where id=?', (f'0406-sivas-2024-{number}-relation',)).fetchone()
    assert row == (f'0406-sivas-{number}-event', None if number == '2879' else '0406-sivas-2024-2880-calendar-result')
    assert db.execute('select state, relation_id from practice_candidate_revision where candidate_id=?', (f'0406-sivas-{number}-candidate',)).fetchone() == ('eligible', f'0406-sivas-2024-{number}-relation')
db.close()
html = (folder / 'index.html').read_text()
for prefix in ('party', 'comparison'):
    start = html.index(f'id="{prefix}-unmatched-0406-sivas-1568-candidate"')
    end = html.index('</article>', start)
    assert 'data-finding-id="0406-sivas-1568-finding"' in html[start:end]
    for number in ('2879', '2880'):
        start = html.index(f'id="{prefix}-practice-0406-sivas-2024-{number}-relation"')
        end = html.index('</article>', start)
        assert f'data-finding-id="0406-sivas-2024-{number}-explanation"' in html[start:end]
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
    for number in ('2883',):
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
print('SEVENTY_SIX_EVENTS_AND_FINDINGS_BOTH_VIEWS_OK', flush=True)
