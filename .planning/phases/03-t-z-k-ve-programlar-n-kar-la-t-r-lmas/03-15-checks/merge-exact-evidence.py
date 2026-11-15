"""Gerçek değişmez dosya testi çıktısına önceki bağımsız kanıtları iliştir."""
import json
from pathlib import Path
from urllib.parse import urldefrag

root = Path('/hpc/group/pfisterlab/mg551/storage/proje')
checks = root / '.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-15-checks'
old = json.loads((checks / 'instrumented-navigation-checks.json').read_text())
new = json.loads((checks / 'exact-browser-evidence.json').read_text())
assert (checks / 'exact-browser.exit').read_text().strip() == '0'
assert new['release_id'] == old['release_id'] and new['report_sha256'] == old['report_sha256']
assert len(new['results']) == 4
for result in new['results']:
    assert result['checks'] == '1' * 19 and result['archiveExcerptFound']
    assert urldefrag(result['actual'])[0] == urldefrag(result['requested'])[0]
    assert '/releases/' + new['release_id'] + '/index.html' in result['actual']
    assert result['archiveActual'] == result['archiveRequested']
for key in ('audits', 'historical_reproduction', 'screenshots', 'audit_input_records', 'check_descriptions'):
    new[key] = old[key]
new['superseded_instrumented_evidence'] = str((checks / 'instrumented-navigation-checks.json').relative_to(root))
new['test_helper'] = 'tests/comparison_navigation.cjs'
(root / 'data/comparisons/03-navigation-checks.json').write_text(json.dumps(new, ensure_ascii=False, indent=2) + '\n')
print('EXACT_EVIDENCE_OK', new['release_id'])
