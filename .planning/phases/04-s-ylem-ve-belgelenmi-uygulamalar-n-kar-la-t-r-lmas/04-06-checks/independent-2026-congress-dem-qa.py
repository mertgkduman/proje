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
package = checks / '2026-congress-dem-draft.json'
review = checks / '2026-congress-dem-review-draft.json'
assert sha(package) == '5412ce22c2f8d6456658ac5a46c9420d611ee169b8dad2642e69f703c56684c6'
assert sha(review) == '2d85e13d3f84fb7ed18ebc53112a3ef2d616205b1e92768dd648804e1ffa0ea6'
old = root / 'data/practices/04-dem.json'
old_review = root / 'data/practices/04-dem-review.json'
assert sha(old) == 'af249fce72f3d37a197b087d725a2a8094ef3bf6ef9c94c5c6c8c4b5574d652d'
assert sha(old_review) == '8888877de623335b07f47d6b6be109cdddb54ed7c88a0bf155a3b5496c534bce'
base, new = (json.loads(p.read_text()) for p in (old, package))
for key in ('entries', 'scope_inventory'):
    assert {canon(r) for r in base[key]} <= {canon(r) for r in new[key]}
for key, rows in base['practice_records'].items():
    assert {canon(r) for r in rows} <= {canon(r) for r in new['practice_records'][key]}
before_review, after_review = (json.loads(p.read_text()) for p in (old_review, review))
for key, rows in before_review.items():
    assert {canon(r) for r in rows} <= {canon(r) for r in after_review[key]}
receipt = json.loads((checks / f'dem-2026-congress-{JOB_ID}.json').read_text())
folder = Path(receipt['preview'])
assert folder.is_relative_to(root / 'data/.staging')
manifest = json.loads((folder / 'manifest.json').read_text())
assert manifest['renderer_version'] == 31
for name, expected in manifest['files'].items():
    assert sha(folder / name) == expected, name
snapshot = json.loads((folder / 'records.json').read_text())
events = {r['id'] for r in new['practice_records']['practice_event']}
assert len(events) == 49
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
    for kind, candidate, finding in (
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
          'checks': ['old package and review monotonic', 'manifest files', '49 events SQLite and JSON',
                     'new and earlier findings in both HTML views'], 'status': 'passed'}
(checks / f'dem-2026-congress-{JOB_ID}-independent.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
