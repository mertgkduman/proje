import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import pdf_page_text

base = Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas')
pdf = Path('data/objects/6554ec05b00d37f62159e1d722f4464ff8b32569ddf7455108530cc772747da2/original.pdf')
version = '0210-demokrat-program-archive-v1'
pages = [pdf_page_text(pdf, i) for i in range(83)]
source = [s for s in json.loads(Path('data/comparisons/03-source-inventory.json').read_text())['sections'] if s['version_id'] == version]
lines = []
for page, text in enumerate(pages, 1):
    owner = 1 if page <= 30 or 55 <= page <= 56 or page >= 77 else 2
    offset = 0
    for n, line in enumerate(text.splitlines(keepends=True), 1):
        if line.strip():
            lines.append(dict(id=f'PDF{page:02d}-L{n:03d}', pdf_page_index=page-1,
                              printed_page=str(page+6) if 3 <= page <= 82 and page not in (8,24,30) else None,
                              offset=offset, owner=owner, text=line.rstrip('\n')))
        offset += len(line)
sections = []
for n, section in enumerate(source, 1):
    match = re.search(r'PDF(?: indeksi)?\s+(\d+)', section['page_range'])
    assert match, section
    page = int(match.group(1)) + ('indeksi' in section['page_range'])
    owner = 1 if page <= 30 or 55 <= page <= 56 or page >= 77 else 2
    sections.append(dict(id=f'INV-{n:03d}', section=section['section'], pdf_page=page, owner=owner,
                         page_line_ids=[x['id'] for x in lines if x['pdf_page_index']==page-1]))
coverage = dict(version_id=version, source_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
                note='Tüm metin satırları sayfa ve görev sahibiyle atanmıştır; envanter başlıkları sayfa düzeyinde bağlantılıdır. Başlıksız önsöz/sunuş ve devamlar da satır listesine dahildir.',
                pages=[dict(pdf_page=i+1, owner=(1 if i+1 <= 30 or 55 <= i+1 <= 56 or i+1 >= 77 else 2),
                            text_lines=sum(x['pdf_page_index']==i for x in lines)) for i in range(83)],
                sections=sections, lines=lines)
coverage['zero_text_layer_visual_review'] = [
    dict(id='PDF01-IMG-COVER',pdf_page=1,owner=1,classification='ön kapak',method='Poppler-glib/Cairo ile özgün sayfa görsel okuması',content='Parti programı kapağı; demokrasi, eğitimde ayrımcılık ve temsil ilkelerini yineleyen görsel metin.'),
    dict(id='PDF08-IMG-FOREWORD-1',pdf_page=8,printed_page='14',owner=1,classification='önsöz devamı',method='Poppler-glib/Cairo ile özgün sayfa görsel okuması',content='Önceki sayfadan devam eden Senato, anayasal denetim ve seçim barajı önerileri.'),
    dict(id='PDF08-IMG-FOREWORD-2',pdf_page=8,printed_page='14',owner=1,classification='önsöz kapanışı',method='Poppler-glib/Cairo ile özgün sayfa görsel okuması',content='Programın hazırlanması ve okura sunuluşuna ilişkin kapanış paragrafı.'),
    dict(id='PDF24-IMG-BLANK',pdf_page=24,owner=1,classification='boş',method='Poppler-glib/Cairo ile özgün sayfa görsel okuması',content='Görünür metin veya görsel içerik yok.'),
    dict(id='PDF30-IMG-BLANK',pdf_page=30,owner=1,classification='boş',method='Poppler-glib/Cairo ile özgün sayfa görsel okuması',content='Görünür metin veya görsel içerik yok.'),
    dict(id='PDF83-IMG-COVER',pdf_page=83,owner=1,classification='arka kapak',method='Poppler-glib/Cairo ile özgün sayfa görsel okuması',content='Programın ekonomi, güvenlik ve gençlik ifadelerini yineleyen arka kapak; ekonomi tekrarı görev 2 çapraz incelemesine aktarılır.')]
assert {x['pdf_page'] for x in coverage['zero_text_layer_visual_review']}=={x['pdf_page'] for x in coverage['pages'] if not x['text_lines']}
(base/'03-13-line-inventory-draft.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
print('INVENTORY_OK',len(sections),'sections',len(lines),'lines',*[sum(x['owner']==i for x in lines) for i in (1,2)])
