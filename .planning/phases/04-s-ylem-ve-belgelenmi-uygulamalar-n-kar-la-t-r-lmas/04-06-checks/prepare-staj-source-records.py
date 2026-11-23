"""Ortak resmî baytları DEM kaynak kimlikleriyle, taslak olarak kaydet."""
import json
from pathlib import Path

here = Path(__file__).resolve().parent
source = here.parent / '04-08-checks/staj-agenda-source-records.json'
records = json.loads(source.read_text())['entries']
versions = {'0408-staj-agenda-inquiry-v1', '0408-staj-agenda-inquiry-register-v1',
            '0408-staj-agenda-floor-v1', '0408-staj-agenda-summary-v1'}
sha_set = {r['values']['sha256'] for r in records if r['kind'] == 'document_version'
           and r['values']['id'] in versions}
documents = {r['values']['document_id'] for r in records if r['kind'] == 'document_version'
             and r['values']['id'] in versions}
exclude = {'0408-staj-agenda-floor-role', '0408-staj-agenda-floor-supports'}
passages = {r['values']['id'] for r in records if r['kind'] == 'passage'
            and r['values']['version_id'] in versions and r['values']['id'] not in exclude}
selected = []
for row in records:
    kind, val = row['kind'], row['values']
    keep = ((kind == 'document' and val['id'] in documents) or
            (kind == 'document_version' and val['id'] in versions) or
            (kind == 'source_attribution' and val['version_id'] in versions) or
            (kind == 'archive_view' and val['source_sha256'] in sha_set) or
            (kind == 'passage' and val['id'] in passages) or
            (kind == 'manual_passage' and val['passage_id'] in passages))
    if keep:
        text = json.dumps(row, ensure_ascii=False).replace('0408-staj-agenda-', '0406-staj-agenda-')
        item = json.loads(text)
        if kind == 'document':
            item['values']['party_id'] = 'dem'
        selected.append(item)
floor = '0406-staj-agenda-floor-v1'
for suffix, exact, section in (
    ('dem-role', 'DEM PARTİ GRUBU ADINA MEHMET ZEKİ İRMEZ (Şırnak) - Teşekkürler Sayın Başkan.', 'DEM grubu adına konuşmacı'),
    ('dem-call', 'Bunun için acilen bir araştırma komisyonu kurulmalı ve bu bir fırsattır.', 'Araştırma komisyonu çağrısı'),
):
    selected.append({'kind': 'passage', 'values': {'id': '0406-staj-agenda-floor-' + suffix,
        'version_id': floor, 'exact': exact, 'prefix': None, 'suffix': None, 'article': None,
        'section': section, 'pdf_page_index': None, 'printed_page': None}})
raw = (here.parents[3] / 'data/practices/sources/dem/objects/a1a7038f7af34b3ca15ec0f5603d19b41b7df64468ec04160234c4752377c522/original.html.bin').read_text(encoding='windows-1254')
for row in selected[-2:]:
    assert row['values']['exact'] in raw
out = {'party_id': 'dem', 'entries': selected}
path = here / 'staj-agenda-source-records.json'
path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print('source entries', len(selected), path)
