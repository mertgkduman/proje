import json
import re
import sys
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import pdf_page_text

root = Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas')
pdf = Path('data/objects/6554ec05b00d37f62159e1d722f4464ff8b32569ddf7455108530cc772747da2/original.pdf')
topics = {r['values']['topic_id'] for r in json.loads(Path('data/comparisons/03-taxonomy.json').read_text())['records'] if r['kind']=='comparison_topic' and r['values']['domain']=='program'}
pages = [pdf_page_text(pdf,i) for i in range(83)]
bad = []
for n, line in enumerate((root/'03-13-specs.tsv').read_text().splitlines(),1):
    page, topic, kind, anchor, summary = line.split('|')
    if topic not in topics or kind not in ('principle','target','instrument'):
        bad.append((n,topic,'unknown topic or field'))
        continue
    text = pages[int(page)-1]
    pattern = re.escape(anchor).replace(r'\ ',r'\s+')
    match = re.search(pattern,text,re.IGNORECASE)
    if not match:
        bad.append((n,page,topic,anchor))
    elif '--show' in sys.argv:
        start = max([m.end() for m in re.finditer(r'[.!?](?=\s)',text[:match.start()])] or [0])
        tail = re.search(r'[.!?](?=\s|$)',text[match.end():])
        end = match.end() + tail.end() if tail else len(text)
        print(n, topic, summary, '\n', text[start:end].strip(), '\n')
if bad:
    print(*bad,sep='\n')
    raise SystemExit(1)
print('ANCHORS_OK')
