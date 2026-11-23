"""Bağımsız kalıcı önizleme, değişmezlik ve görünürlük kontrolü."""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

checks = Path(__file__).resolve().parent
root = checks.parents[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
canon = lambda row: json.dumps(row, ensure_ascii=False, sort_keys=True)
package = checks / '4114-first-five-draft.json'
review = checks / '4114-first-five-review-draft.json'
assert sha(package) == '22e0a4d6b0e9753b3b8ad397d0ab5a7e8d975b02767c3a6debe20463454b102c'
assert sha(review) == '0e1caab64c6e770218b1ff272cd15aca1c32b7366c3c2396342e5050a59393a8'
old = root / 'data/practices/04-dem.json'
old_review = root / 'data/practices/04-dem-review.json'
assert sha(old) == 'a2abfd368da20d88a3296cf72cedc42a3faf0f6ae92930901c6b5ae13b12b32b'
assert sha(old_review) == 'e1f2512884d7bf10669be84c65ca726623d18227faee83482864db9b0bdf8426'
base, new = (json.loads(p.read_text()) for p in (old, package))
for key in ('entries', 'scope_inventory'):
    assert {canon(r) for r in base[key]} <= {canon(r) for r in new[key]}
for key, rows in base['practice_records'].items():
    assert {canon(r) for r in rows} <= {canon(r) for r in new['practice_records'][key]}
before_review, after_review = (json.loads(p.read_text()) for p in (old_review, review))
for key, rows in before_review.items():
    assert {canon(r) for r in rows} <= {canon(r) for r in after_review[key]}
receipt = json.loads((checks / 'dem-4114-five-62483862.json').read_text())
folder = Path(receipt['preview'])
assert folder.is_relative_to(root / 'data/.staging')
manifest = json.loads((folder / 'manifest.json').read_text())
assert manifest['renderer_version'] == 31
for name, expected in manifest['files'].items():
    assert sha(folder / name) == expected, name
snapshot = json.loads((folder / 'records.json').read_text())
events = {r['id'] for r in new['practice_records']['practice_event']}
assert len(events) == 27
assert events <= {r['id'] for r in snapshot['practice_event']}
db = sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro', uri=True)
assert all(db.execute('select 1 from practice_event where id=?', (e,)).fetchone() for e in events)
db.close()
html = (folder / 'index.html').read_text()
for prefix in ('party', 'comparison'):
    for n in range(1, 6):
        candidate = f'0406-4114-madde{n}-candidate'
        finding = f'0406-4114-madde{n}-finding'
        start = html.index(f'id=\"{prefix}-unmatched-{candidate}\"')
        end = html.index('</article>', start)
        assert f'data-finding-id=\"{finding}\"' in html[start:end]
    for kind, candidate, finding in (
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
result = {'job': 62483862, 'checked_at': datetime.now(timezone.utc).isoformat(),
          'package_sha256': sha(package), 'review_sha256': sha(review),
          'preview': str(folder), 'manifest_sha256': sha(folder / 'manifest.json'),
          'renderer_version': 31, 'event_count': len(events),
          'checks': ['old package and review monotonic', 'manifest files', '27 events SQLite and JSON',
                     'new and earlier findings in both HTML views'], 'status': 'passed'}
(checks / 'dem-4114-five-62483862-independent.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
