"""Yedi yeni bulguyu doğrulanmış Faz 4 başlığına taşı; önceki satırlar değişmez."""
import json
from pathlib import Path
here = Path(__file__).resolve().parent
source = here/'101831-combined-draft.json'
target = here/'101831-dossier-compatible-draft.json'
package = json.loads(source.read_text())
ids = {'0406-hakkari-rounds-result','0406-hakkari-rounds-link','0406-hakkari-dispute-finding','0406-101831-submission-f','0406-101831-outcome-f','0406-101831-relation-f','0406-101831-debate-f'}
changed = set()
for entry in package['entries']:
    if entry['kind'] == 'finding' and entry['values']['id'] in ids:
        assert entry['values']['heading'] == 'Söylem ve uygulama'
        entry['values']['heading'] = 'Belgelenmiş uygulamalar'
        changed.add(entry['values']['id'])
assert changed == ids
assert not target.exists()
target.write_text(json.dumps(package, ensure_ascii=False, indent=2)+'\n')
print('DOSSIER_HEADING_ONLY', len(changed))
