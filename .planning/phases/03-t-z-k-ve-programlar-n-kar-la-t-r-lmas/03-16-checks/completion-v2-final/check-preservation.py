"""Compare historical files, receipts, originals and views with prospective hashes."""
import datetime
import hashlib
import json
from pathlib import Path

root = Path.cwd()
here = Path(__file__).resolve().parent
prospective = json.loads((here / 'prospective.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
groups = {
    'historical_releases': {p: v for p, v in prospective['file_sha256'].items() if p.startswith('data/releases/')},
    'receipts_and_delivery_inputs': {p: v for p, v in prospective['file_sha256'].items() if p.startswith('data/deliveries/')},
    'raw_originals': prospective['raw_original_sha256'],
    'archive_views': prospective['view_sha256'],
    'frozen_renderer': {'src/rapor_v22.py': '2dd45306ab671aa40e4ff937529a563e748a8e813e6cc6674622cd1ff714268e'},
}
result = {'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'groups': {}}
for name, files in groups.items():
    errors = [p for p, digest in files.items() if not (root / p).is_file() or sha(root / p) != digest]
    result['groups'][name] = {'files': len(files), 'matches': not errors, 'mismatches': errors}
result['release_count'] = len(prospective['release_chain'])
result['source_version_references'] = len(prospective['document_version_references'])
(here / 'preservation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
if not all(group['matches'] for group in result['groups'].values()):
    raise SystemExit('Preservation mismatch')
print('PRESERVATION_OK', json.dumps({k: v['files'] for k, v in result['groups'].items()}))
