"""Yalnız gerçek başarılı test/audit çıktılarından yayın kanıtını tamamla."""
import hashlib
import json
import sys
from pathlib import Path

root = Path('/hpc/group/pfisterlab/mg551/storage/proje')
sys.path.insert(0, str(root / 'src'))
from arsiv import render_comparison_snapshot
from rapor_v17 import render_report as v17
from rapor_v18 import render_report as v18
from rapor_v19 import render_report as v19

checks = root / '.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-15-checks'
evidence = root / 'data/comparisons/03-navigation-checks.json'
data = json.loads(evidence.read_text())
release = json.loads((root / 'data/current.json').read_text())['release_id']
assert data['release_id'] == release
assert (checks / 'final-navigation.exit').read_text().strip() == '0'
assert (checks / 'final-code-navigation.exit').read_text().strip() == '0'
assert (checks / 'final-code-report.exit').read_text().strip() == '0'
assert len(data['results']) == 4 and all(r['checks'] == '1' * 19 for r in data['results'])
audits = {}
for name, marker in [('phase2-optimized', 'PHASE2_AUDIT_OK'), ('phase3-partial-retry', 'PHASE3_AUDIT_OK')]:
    assert (checks / (name + '.exit')).read_text().strip() == '0'
    output = (checks / (name + '.log')).read_text()
    assert marker + ' ' + release in output
    audits[name] = {'result': marker, 'log': str((checks / (name + '.log')).relative_to(root))}
historical = []
for identity, renderer in [('a828140c2fb649b5b8d0cef32b42769e', v17),
                           ('4da93e2c64914eecb875c66cca14ea57', v18),
                           ('b513965558094e338a941be90a1960a4', v18),
                           ('61b127ba1cb1479e9e6f55e6a6f40f5e', v19)]:
    folder = root / 'data/releases' / identity
    actual = (folder / 'index.html').read_bytes()
    rebuilt = render_comparison_snapshot(json.loads((folder / 'records.json').read_text()), renderer).encode()
    assert rebuilt == actual
    historical.append({'release_id': identity, 'html_sha256': hashlib.sha256(actual).hexdigest(), 'reproduced': True})
images = []
for image in sorted((checks / 'screenshots-final').glob('*.png')):
    images.append({'file': str(image.relative_to(root)), 'sha256': hashlib.sha256(image.read_bytes()).hexdigest()})
assert len(images) == 4
data.update(audits=audits, historical_reproduction=historical, screenshots=images,
            audit_input_records=['.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-15-checks/final-code-runs.json',
                                 '.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-15-checks/phase3-partial-retry-run.json'],
            check_descriptions=['direct hash and target focus', 'open summary, quotation and source',
              'quotation and summary colors', 'comparison to dossier', 'dossier to comparison',
              'history back', 'history forward', 'source version, locator and local archive',
              'source history back and citation focus', 'source history forward', 'no horizontal overflow',
              'malformed hash has no effect', 'status-only scope proof link', 'scope target focus',
              'unique DOM IDs', 'horizontal-tab up key left to browser', 'nine-party fixed order',
              'summary first and methods closed', 'horizontal tab keyboard and ARIA state'])
evidence.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
print('EVIDENCE_OK', release)
