"""Record only completed and independently checked local v2 acceptance facts."""
import datetime
import hashlib
import json
from pathlib import Path

root = Path.cwd()
here = Path(__file__).resolve().parent
job = Path('/tmp/proje-v2-production-focused-20261115')
pub = Path('/tmp/proje-v2-production-publish-20261115')
assert json.loads((pub / 'exit.json').read_text())['exit_code'] == 0
assert json.loads((job / 'exit.json').read_text())['exit_code'] == 0
results = json.loads((job / 'results.json').read_text())
assert all(r['valid'] for r in results['results'])
release = results['release_id']
assert json.loads((root / 'data/current.json').read_text())['release_id'] == release
assert not (root / 'data/.write.lock').exists()
folder = root / 'data/releases' / release
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
manifest = json.loads((folder / 'manifest.json').read_text())
data = json.loads((folder / 'records.json').read_text())
nav = json.loads((job / 'navigation-evidence.json').read_text())
assert nav['release_id'] == release and nav['report_sha256'] == sha(folder / 'index.html') and nav['records_sha256'] == sha(folder / 'records.json')
assert len(nav['results']) == 4 and all(r['checks'] == '1' * 19 and r['archiveExcerptFound'] for r in nav['results'])
assert sha(folder / 'index.html') == '60bafd3b384e020800a01b00a0c58beaf0392d1587d69e372c44667e4186cf3f'
preservation = json.loads((here / 'preservation.json').read_text())
assert all(x['matches'] for x in preservation['groups'].values())
probe = json.loads((root / 'data/comparisons/03-probe-record.json').read_text())
assert len(probe['flagged_assumptions']) == 8 and len(probe['prohibitions']) == 3
assert all(x['status'] == 'unresolved' and all(x[k] is None for k in ('verification', 'resolution', 'reason')) for x in probe['flagged_assumptions'])
assert all(x['status'] == 'unresolved' and 'descriptor' not in x for x in probe['prohibitions'])
taxonomy = data['comparison_contract'][0]['taxonomy_version']
rows = [r for r in data['comparison_row'] if r['taxonomy_version'] == taxonomy]
row_ids = {r['id'] for r in rows}
fields = [f for f in data['comparison_field'] if f['row_id'] in row_ids]
inventory = [r for r in data['comparison_source_inventory'] if r['taxonomy_version'] == taxonomy]
old = json.loads((root / 'data/comparisons/03-acceptance.json').read_text())
old.update(release_id=release, report_path=str((folder / 'index.html').relative_to(root)),
           manifest_sha256=sha(folder / 'manifest.json'), report_sha256=sha(folder / 'index.html'),
           records_sha256=sha(folder / 'records.json'), sqlite_sha256=sha(folder / 'records.sqlite3'),
           checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
           versions={k: v for k, v in manifest.items() if k.endswith('_version') or k.startswith('comparison_completion_')},
           coverage={'topics': sum(t['taxonomy_version'] == taxonomy for t in data['comparison_topic']),
                     'parties': len(data['scope_party']), 'rows': len(rows), 'fields': len(fields),
                     'syntheses': sum(s['taxonomy_version'] == taxonomy for s in data['comparison_synthesis']),
                     'inventory_sections': len(inventory), 'open_substantive_rows': sum(r['state'] in ('not_researched', 'in_progress') for r in rows),
                     'unmatched_inventory_sections': sum(bool(json.loads(i['unmatched_headings'])) for i in inventory)},
           final_checks=str((here / 'focused-results.json').relative_to(root)),
           preservation_evidence=str((here / 'preservation.json').relative_to(root)),
           source_review='data/comparisons/03-completion-review-v2.json',
           historical_source_review='data/comparisons/03-source-review.json',
           source_review_kind='agent', human_uat='pending', formal_phase_acceptance='pending', requirements_completed=[])
(root / 'data/comparisons/03-navigation-checks.json').write_text(json.dumps(nav, ensure_ascii=False, indent=2) + '\n')
(root / 'data/comparisons/03-acceptance.json').write_text(json.dumps(old, ensure_ascii=False, indent=2) + '\n')
print('ACCEPTANCE_RECORDED', release, old['coverage'])
