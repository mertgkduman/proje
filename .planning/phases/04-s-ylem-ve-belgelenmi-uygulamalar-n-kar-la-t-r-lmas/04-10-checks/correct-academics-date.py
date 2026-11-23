import json
from pathlib import Path

p = Path(__file__).parent
x = json.loads((p / 'academics-37207-union-draft.json').read_text())
r = next(row for row in x['practice_records']['practice_relation'] if row['id'] == '0410-academics-37207-relation')
assert r['temporal_context'] == 'Programın 2023 arşivi ile 2025 soru ve yanıtı ayrı tarihlerdir.'
r['temporal_context'] = 'Programın 2023 arşivi, 2025 soru ve 2026 yanıtı ayrı tarihlerdir.'
(p / 'academics-37207-corrected-union-draft.json').write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')
