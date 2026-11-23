"""Bağımsız kalıcı önizleme, değişmezlik ve görünürlük kontrolü."""
import os
JOB_ID = os.environ['SLURM_JOB_ID']
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

checks = Path(__file__).resolve().parent
root = checks.parents[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
canon = lambda row: json.dumps(row, ensure_ascii=False, sort_keys=True)
package = checks / 'sivas-two-dem-draft.json'
review = checks / 'sivas-two-dem-review-draft.json'
assert sha(package) == 'fe9d623bd2293b4b9fd99e61370e8d577f9ae041182522db796545b7c632b7c8'
assert sha(review) == 'af7dcf5f3961a01e900283082e49e32c3a3f521fe3b8f692936cf9efe1f1aaaf'
old = root / 'data/practices/04-dem.json'
old_review = root / 'data/practices/04-dem-review.json'
assert sha(old) == '9cf37562ff02b983dd28a457cd6426168dc9de8f98b06e33ab2dab453b951f56'
assert sha(old_review) == 'f98256dfcb690a39fe179024efdbb6ad2bf31a4e6424658f5cd951b346534d33'
base, new = (json.loads(p.read_text()) for p in (old, package))
for key in ('entries', 'scope_inventory'):
    assert {canon(r) for r in base[key]} <= {canon(r) for r in new[key]}
for key, rows in base['practice_records'].items():
    assert {canon(r) for r in rows} <= {canon(r) for r in new['practice_records'][key]}
before_review, after_review = (json.loads(p.read_text()) for p in (old_review, review))
for key, rows in before_review.items():
    assert {canon(r) for r in rows} <= {canon(r) for r in after_review[key]}
receipt = json.loads((checks / f'dem-sivas-two-{JOB_ID}.json').read_text())
folder = Path(receipt['preview'])
assert folder.is_relative_to(root / 'data/.staging')
manifest = json.loads((folder / 'manifest.json').read_text())
assert manifest['renderer_version'] == 31
for name, expected in manifest['files'].items():
    assert sha(folder / name) == expected, name
snapshot = json.loads((folder / 'records.json').read_text())
events = {r['id'] for r in new['practice_records']['practice_event']}
assert len(events) == 60
assert events <= {r['id'] for r in snapshot['practice_event']}
db = sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro', uri=True)
assert all(db.execute('select 1 from practice_event where id=?', (e,)).fetchone() for e in events)
for n in (*range(1, 21), 'gecici1', 'gecici2', '14-anayasa'):
    for suffix in ('akin-dem', 'koca-grup'):
        event, passage = f'0406-4114-madde{n}-event', f'0406-4114-{suffix}'
        assert any(x['event_id'] == event and x['passage_id'] == passage and x['stage'] == 'action' for x in snapshot['practice_event_evidence'])
        assert db.execute('select 1 from practice_event_evidence where event_id=? and passage_id=? and stage=?', (event, passage, 'action')).fetchone()
db.close()
html = (folder / 'index.html').read_text()
for prefix in ('party', 'comparison'):
    for n in (*range(1, 21), 'gecici1', 'gecici2', '14-anayasa'):
        candidate = f'0406-4114-madde{n}-candidate'
        finding = f'0406-4114-madde{n}-finding'
        start = html.index(f'id=\"{prefix}-unmatched-{candidate}\"')
        end = html.index('</article>', start)
        assert f'data-finding-id=\"{finding}\"' in html[start:end]
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
    for kind, candidate, finding in (
        ("unmatched", "0406-2026-pm-myk-myk-candidate", "0406-2026-pm-myk-myk-finding"),
        ("unmatched", "0406-2026-pm-myk-kadin-candidate", "0406-2026-pm-myk-kadin-finding"),
        ("unmatched", "0406-2026-congress-candidate", "0406-2026-congress-finding"),
        ("unmatched", "0406-dem-teacher-4314-candidate", "0406-dem-teacher-4314-finding"),
        ("unmatched", "0406-nov03-4961-candidate", "0406-nov03-4961-finding"),
        ("unmatched", "0406-nov03-genelgorusme-candidate", "0406-nov03-genelgorusme-finding"),
        ("unmatched", "0406-staj-agenda-candidate", "0406-staj-agenda-finding"),
        ('unmatched', '0406-oct08-yeniyol-candidate', '0406-oct08-yeniyol-finding'),
        ('unmatched', '0406-oct08-dem-candidate', '0406-oct08-dem-finding'),
        ('unmatched', '0406-dem-5472-cebir-candidate', '0406-dem-5472-cebir-finding'),
        ('unmatched', '0406-dem-5472-hisse-candidate', '0406-dem-5472-hisse-finding'),
        ('practice', '0406-hakkari-selection-relation', '0406-hakkari-dispute-finding'),
        ('practice', '0406-101831-relation', '0406-101831-debate-f'),
    ):
        start = html.index(f'id="{prefix}-{kind}-{candidate}"')
        end = html.index('</article>', start)
        assert f'data-finding-id="{finding}"' in html[start:end], (prefix, candidate)
result = {'job': JOB_ID, 'checked_at': datetime.now(timezone.utc).isoformat(),
          'package_sha256': sha(package), 'review_sha256': sha(review),
          'preview': str(folder), 'manifest_sha256': sha(folder / 'manifest.json'),
          'renderer_version': 31, 'event_count': len(events),
          'checks': ['old package and review monotonic', 'manifest files', '60 events SQLite and JSON',
                     'new and earlier findings in both HTML views'], 'status': 'passed'}
(checks / f'dem-sivas-two-{JOB_ID}-independent.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
