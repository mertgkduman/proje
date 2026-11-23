"""1 Temmuz görüşmesi için ortak baytlı ve DEM kimlikli kaynak kayıtları."""
import hashlib
import json
from pathlib import Path

from arsiv import pdf_page_text

checks = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas')
reference = json.loads((checks / '04-08-checks/fund-july-source-records.json').read_text())
source = Path('data/practices/sources/dem')
accepted = {'floor-agenda', 'floor-dem-role', 'floor-dem-support', 'floor-quorum1', 'floor-quorum2', 'floor-decision'}
entries = []
for entry in reference['entries']:
    kind, values = entry['kind'], entry['values']
    ident = values.get('id', values.get('version_id', ''))
    if kind in ('document', 'document_version', 'source_attribution') and ident in ('0408-fund-july-floor', '0408-fund-july-floor-v1'):
        pass
    elif kind == 'passage' and ident.removeprefix('0408-fund-july-') in accepted:
        pass
    else:
        continue
    converted = json.loads(json.dumps(entry, ensure_ascii=False).replace('0408-fund-july-', '0406-fund-july-'))
    if kind == 'document':
        converted['values']['party_id'] = 'dem'
    entries.append(converted)

version = next(x['values'] for x in entries if x['kind'] == 'document_version')
pdf = source / version['original_path']
assert hashlib.sha256(pdf.read_bytes()).hexdigest() == version['sha256']
for entry in entries:
    if entry['kind'] == 'passage':
        v = entry['values']
        assert v['exact'] in pdf_page_text(str(pdf.resolve()), v['pdf_page_index']), v['id']

out = checks / '04-06-checks/july-fund-source-records.json'
out.write_text(json.dumps({'party_id': 'dem', 'entries': entries}, ensure_ascii=False, indent=2) + '\n')
print('JULY_SOURCE_RECORDS', len(entries), hashlib.sha256(out.read_bytes()).hexdigest())
