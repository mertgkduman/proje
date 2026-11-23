"""Artı Siirt'in farklı sonuç sayısını partiye özgü atıflı kayıt olarak hazırla."""
import hashlib, json
from pathlib import Path
from arsiv import html_source_text

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
raw = json.loads((p.parent / '04-05-checks/mdkd-2026-append-draft.json').read_text())['entries']
old, new = '0405-tip-mdkd-siirt', '0406-dem-mdkd-siirt'
out = []
for item in raw:
    kind, v = item['kind'], item['values']
    if kind == 'document' and v.get('id') != old: continue
    if kind == 'document_version' and v.get('document_id') != old: continue
    if kind in ('source_attribution', 'archive_view') and v.get('version_id') != old + '-v1': continue
    if kind == 'passage' and v.get('id') != old + '-tally-p': continue
    if kind not in ('document', 'document_version', 'source_attribution', 'archive_view', 'passage'): continue
    v = json.loads(json.dumps(v, ensure_ascii=False).replace(old, new))
    if kind == 'document': v['party_id'] = 'dem'
    out.append({'kind': kind, 'values': v})
assert len(out) == 5
version = next(x['values'] for x in out if x['kind'] == 'document_version')
path = Path('data/practices/sources/dem') / version['original_path']
assert hashlib.sha256(path.read_bytes()).hexdigest() == version['sha256']
assert next(x['values']['exact'] for x in out if x['kind'] == 'passage') in html_source_text(path.read_bytes())
result = p / '2026-5367-news-source-records.json'
result.write_text(json.dumps({'party_id': 'dem', 'entries': out}, ensure_ascii=False, indent=2) + '\n')
print('NEWS_SOURCE_RECORDS', hashlib.sha256(result.read_bytes()).hexdigest(), len(out))
