import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import pdf_page_text

root = Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas')
pdf = Path('data/objects/6718b7ca1b2997d0d1f0e52999c8c5ce852af648be7e83cb26c5a7eef060805c/original.pdf')
transitions = {
    15: [(None, 2)],
    35: [('2.3.6', 1)],
    36: [('2.3.7', 2)],
    37: [('2.3.8', 1)],
    38: [('2.3.9', 2)],
    42: [('2.3.12', 1)],
    43: [('2.3.14', 2)],
    48: [('2.5', 1)],
    70: [(None, 2)],
}
owner = 1
output = []
for page in range(1, 71):
    text = pdf_page_text(pdf, page - 1)
    lines = text.splitlines(keepends=True)
    offset = 0
    for index, line in enumerate(lines, 1):
        for marker, target in transitions.get(page, []):
            if marker is None and index == 1 or marker is not None and re.match(r'^' + re.escape(marker) + r'(?:\s|$)', line.strip()):
                owner = target
        if not line.strip():
            offset += len(line)
            continue
        output.append({'id': f'PDF{page:02d}-L{index:03d}', 'pdf_page_index': page - 1,
                       'printed_page': str(page), 'owner': owner, 'offset': offset, 'text': line.rstrip('\n')})
        offset += len(line)
inventory = {'version_id': '0209-saadet-current-program-v1', 'source_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
             'status': 'source-read-section-and-line-ownership-reviewed', 'lines': output}
sections = json.loads(Path('data/comparisons/03-source-inventory.json').read_text())['sections']
positions = []
overrides = {24: 'Ekonomive Kalkınma', 65: 'Türkiye’nin Batı ve Diğer Aktörleile İlişkileri', 67: 'Türkiye -ABD İlişkileri'}
for number, section in enumerate((s for s in sections if s['version_id'] == inventory['version_id']), 1):
    page = int(re.search(r'PDF\s+(\d+)', section['page_range']).group(1))
    label = overrides.get(number, re.sub(r'^\d+(?:\.\d+)*\.?\s+', '', section['section']))
    pattern = re.escape(label).replace(r'\ ', r'\s+')
    text = pdf_page_text(pdf, page - 1)
    after = positions[-1][1] + 1 if positions and positions[-1][0] == page - 1 else 0
    match = re.compile(pattern, re.IGNORECASE).search(text, after)
    if not match:
        print('HEADING_UNMATCHED', number, page, section['section'])
    else:
        start = text.rfind('\n', 0, match.start()) + 1
        before = text[:start]
        numeric = re.search(r'(?m)^\d+(?:\.\d+)*\.?\s*$', before)
        candidates = list(re.finditer(r'(?m)^\d+(?:\.\d+)*\.?[ \t]*$', before))
        if candidates and not before[candidates[-1].end():].strip():
            start = candidates[-1].start()
        if number == 31:
            start = text.index('2.2.7')
        positions.append((page - 1, start, number, section['section']))
for line in output:
    preceding = [x for x in positions if (x[0], x[1]) <= (line['pdf_page_index'], line['offset'])]
    line['section_id'] = f'INV-{preceding[-1][2]:03d}' if preceding else 'FRONT-MATTER'
    if preceding:
        n = preceding[-1][2]
        line['owner'] = 1 if n <= 23 or n in (42, 44, 48, 49) or 56 <= n <= 79 else 2
inventory['sections'] = [{'id': f'INV-{number:03d}', 'section': name, 'pdf_page_index': page, 'offset': offset,
                          'owner': 1 if number <= 23 or number in (42, 44, 48, 49) or 56 <= number <= 79 else 2,
                          'line_ids': [line['id'] for line in output if line['section_id'] == f'INV-{number:03d}']}
                         for page, offset, number, name in positions]
(root / '03-11-line-inventory-draft.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n')
print(len(output), 'lines', {part: sum(x['owner'] == part for x in output) for part in (1, 2)})
