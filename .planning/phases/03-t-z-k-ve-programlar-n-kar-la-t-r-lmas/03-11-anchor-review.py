import re
import sys
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import pdf_page_text

root = Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas')
pdf = Path('data/objects/6718b7ca1b2997d0d1f0e52999c8c5ce852af648be7e83cb26c5a7eef060805c/original.pdf')
pages = [pdf_page_text(pdf, n) for n in range(70)]
for number, line in enumerate((root / '03-11-specs.tsv').read_text().splitlines(), 1):
    page, topic, kind, anchor, summary = line.split('|')
    text = pages[int(page)-1]
    pattern = re.escape(anchor).replace(r'\ ', r'\s+')
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        print(f'MISSING {number} page={page} {topic}: {anchor}')
        continue
    end = re.search(r'\.(?=\s|$)', text[match.end():])
    end = match.end() if anchor.endswith('.') else match.end() + end.end() if end else match.end()
    quote = text[match.start():end].replace('\n', ' ')
    print(f'{number:02} {page} {topic} [{kind}] {quote} | {summary}')
