"""Bind acceptance facts to the verified immutable release and actual logs."""
import datetime
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[4]
checks = Path(__file__).resolve().parent
release = '85b1a453ce2346a8ad0df325a2b73ae9'
folder = root / 'data/releases' / release
assert json.loads((root / 'data/current.json').read_text())['release_id'] == release
assert (checks / 'final-checks.exit').read_text().strip() == '0'
results = json.loads((checks / 'final-checks-results.json').read_text())
assert results['release_id'] == release and all(x['valid'] for x in results['results'])
manifest = json.loads((folder / 'manifest.json').read_text())
data = json.loads((folder / 'records.json').read_text())
nav = json.loads((root / 'data/comparisons/03-navigation-checks.json').read_text())
probe = json.loads((root / 'data/comparisons/03-probe-record.json').read_text())
preservation = json.loads((checks / 'post-publish-preservation.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert nav['release_id'] == release and nav['report_sha256'] == sha(folder / 'index.html') and nav['records_sha256'] == sha(folder / 'records.json')
assert len(probe['flagged_assumptions']) == 8 and len(probe['prohibitions']) == 3
assert all(x['status'] == 'unresolved' and all(x[k] is None for k in ('verification', 'resolution', 'reason')) for x in probe['flagged_assumptions'])
assert all(x['status'] == 'unresolved' and 'descriptor' not in x for x in probe['prohibitions'])
assert all(x['manifest_matches'] and x['files_match'] for x in preservation['historical_releases'])
assert all(preservation['receipt_hashes_match'].values()) and all(x['matches'] for x in preservation['originals'])
taxonomy = data['comparison_contract'][0]['taxonomy_version']
rows = [r for r in data['comparison_row'] if r['taxonomy_version'] == taxonomy]
row_ids = {r['id'] for r in rows}
fields = [f for f in data['comparison_field'] if f['row_id'] in row_ids]
inventory = [r for r in data['comparison_source_inventory'] if r['taxonomy_version'] == taxonomy]
out = {
    'release_id': release, 'report_path': str((folder / 'index.html').relative_to(root)),
    'manifest_sha256': sha(folder / 'manifest.json'), 'report_sha256': sha(folder / 'index.html'),
    'records_sha256': sha(folder / 'records.json'), 'sqlite_sha256': sha(folder / 'records.sqlite3'),
    'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'versions': {k: manifest.get(k) for k in ('comparison_taxonomy_version', 'comparison_validation_version', 'comparison_completion_version', 'comparison_synthesis_contract_version', 'comparison_view_version', 'renderer_version', 'data_schema_version', 'source_policy_version')},
    'coverage': {'topics': sum(t['taxonomy_version'] == taxonomy for t in data['comparison_topic']),
                 'parties': len(data['scope_party']), 'rows': len(rows), 'fields': len(fields),
                 'syntheses': sum(s['taxonomy_version'] == taxonomy for s in data['comparison_synthesis']),
                 'inventory_sections': len(inventory), 'open_substantive_rows': sum(r['state'] in ('not_researched', 'in_progress') for r in rows),
                 'unmatched_inventory_sections': sum(bool(json.loads(i['unmatched_headings'])) for i in inventory)},
    'documentary_limits': ['DEM, DBP ve Yeni Yol bağımsız tam programları bulunamadı veya erişilemedi',
                           'Yeni Yol tam tüzüğü bulunamadı veya erişilemedi',
                           'DYP 1985 nüshasında basılı 99–100 sayfalar eksik',
                           'Bazı sürümlerin kabulü veya sırası bilinmiyor; aynı SHA taşıyan URLler kopyadır'],
    'source_review': 'data/comparisons/03-source-review.json', 'source_review_kind': 'agent',
    'navigation_evidence': 'data/comparisons/03-navigation-checks.json',
    'probe_record': 'data/comparisons/03-probe-record.json',
    'uat': '.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-UAT.md',
    'final_checks': str((checks / 'final-checks-results.json').relative_to(root)),
    'preservation_evidence': str((checks / 'post-publish-preservation.json').relative_to(root)),
    'historical_receipts': 'sekiz dosya korunmuş; bu sürüm için yeni Faz 2 makbuzu oluşturulmadı',
    'human_uat': 'pending', 'formal_phase_acceptance': 'pending', 'requirements_completed': [],
}
(root / 'data/comparisons/03-acceptance.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('ACCEPTANCE_RECORDED', release, out['coverage'])
