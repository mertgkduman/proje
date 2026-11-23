"""DEM için ortak TBMM baytlarına partiye özgü kaynak kimlikleri bağlar."""
import json
from pathlib import Path
from arsiv import html_source_text

c = Path(__file__).resolve().parent
root = c.parents[3]
source = json.loads((c.parent / '04-08-checks/nov03-genelgorusme-source-records.json').read_text())
old, new = '0408-nov03-genelgorusme-', '0406-nov03-genelgorusme-'
allowed = {'floor', 'register', 'signed'}
allowed_passages = {'floor-call', 'floor-vote', 'register-number', 'register-date', 'register-status', 'signed-number'}
entries = []
for entry in source['entries']:
    v = entry['values']
    identity = v.get('id', v.get('version_id', v.get('passage_id', '')))
    suffix = identity.removeprefix(old)
    if not identity.startswith(old) or not any(suffix == x or suffix.startswith(x + '-') for x in allowed):
        continue
    if entry['kind'] == 'passage' and suffix not in allowed_passages:
        continue
    if entry['kind'] == 'manual_passage':
        continue
    rewritten = json.loads(json.dumps(entry, ensure_ascii=False).replace(old, new))
    if rewritten['kind'] == 'document':
        rewritten['values']['party_id'] = 'dem'
    entries.append(rewritten)
raw = (root / 'data/practices/sources/dem/objects/43f76c014493808d974aed00ce23152667132f1862f387bde6f788524a17357b/original.html.bin').read_bytes()
text = html_source_text(raw)
for suffix, exact, section in (
    ('floor-dem-role', 'DEM PARTİ GRUBU ADINA İBRAHİM AKIN (İzmir)', 'İbrahim Akın’ın DEM Grup sıfatı'),
    ('floor-dem-call', 'Denetlenebilir ve herkesin bu süreç içerisinde söz ve karar süreçlerine katıldığı bir yapıyı kurmadan bu meseleyi çözmek mümkün değildir.', 'İbrahim Akın’ın denetim ve katılım çağrısı'),
):
    assert exact in text
    entries.append({'kind': 'passage', 'values': {'id': new + suffix, 'version_id': new + 'floor-v1', 'exact': exact, 'prefix': None, 'suffix': None, 'article': None, 'section': section, 'pdf_page_index': None, 'printed_page': None}})
(c / 'nov03-dem-source-records.json').write_text(json.dumps({'party_id': 'dem', 'entries': entries}, ensure_ascii=False, indent=2) + '\n')
print('NOV03_DEM_SOURCE_RECORDS_OK', len(entries))
