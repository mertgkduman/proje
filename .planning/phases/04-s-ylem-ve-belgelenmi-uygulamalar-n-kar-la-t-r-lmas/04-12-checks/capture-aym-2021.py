"""Preserve the visual Resmî Gazete copy of the 2021 accounts decision."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import pdf_page_text, readable_bytes

checks, stage = map(Path, sys.argv[1:])
source = stage/'rg2021.pdf'
root = Path('data/practices/sources/demokrat')
raw = source.read_bytes()
digest = sha256(raw).hexdigest()
assert digest == '1d13096b536d818fc328dbf69c413c4088cded2e0befe5854d38c2b4a262eaa3'
doc = '0412-aym-2021-hesap'
version = doc+'-v1'
url = 'https://www.resmigazete.gov.tr/eskiler/2025/03/20250314-15.pdf'
original, readable = (f'objects/{digest}/{filename}' for filename in ('original.pdf','readable.html'))
now = datetime.now(timezone.utc).isoformat()
paths = []
for rel, body in ((original,raw),(readable,readable_bytes(raw,'pdf',legacy=False))):
    path = root/rel
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes()==body
    else:
        path.write_bytes(body)
    paths.append(path)
assert not any(char.isalpha() for i in range(3) for char in pdf_page_text(root/original,i))
entries = []


def add(table, **row):
    entries.append(dict(kind=table,values=row))


add('document', id=doc, party_id='demokrat', title='Demokrat Parti 2021 kesin hesabı, AYM E.2022/42 K.2024/116', source_kind='official')
add('document_version', id=version, document_id=doc, original_url=url, final_url=url,
    document_date='2024-12-25', date_precision='day', date_unknown_reason=None, version_label='Resmî Gazete’de yayımlanmış özgün karar.',
    mime='application/pdf', accessed_at=datetime.fromtimestamp((stage/'rg-pdf.raw').stat().st_mtime, timezone.utc).isoformat(),
    verified_at=now, sha256=digest, original_path=original, readable_path=readable)
add('source_attribution', version_id=version, publisher='Resmî Gazete', author='Anayasa Mahkemesi', kind='official',
    published_at='2025-03-14', date_precision='day', social_handle=None, public_url=url,
    basis='Karar veren kurum, karar tarihi ve 32841 sayılı yayım künyesi ilk sayfada.')
for name, section, index, exact in (
    ('identity','İlk sayfa, E.2022/42 ve K.2024/116 karar künyesi',0, 'Karar Sayısı : 2024/116'),
    ('year','İlk sayfa, inceleme konusu',0,'Demokrat Partinin 2021 yılı kesin hesabının incelenmesidir.'),
    ('submission','Esas incelemesi, §3 parti çizelgelerinin Mahkemeye sunulması',0,
     'Demokrat Partinin Anayasa Mahkemesine verdiği 2021 yılı kesin hesap çizelgeleri'),
    ('review','Esas incelemesi, §3 Sayıştay raporunun hazırlanması',0,'Sayıştay Başkanlığınca hazırlanıp Raportör Burak FIRAT tarafından Heyete sunulan esas inceleme raporu'),
    ('merit','Son sayfa IV. sonuç, 25 Aralık 2024 oybirliği',2,'Partiler Kanunu’na uygun olduğuna 25/12/2024 tarihinde OYBİRLİĞİYLE karar verildi.'),
    ('balance','Son sayfa IV. sonuç, bilgi ve belge sınırı',2,'eldeki bilgi ve belgelere göre doğru, denk'),
):
    pid=doc+'-'+name
    add('passage',id=pid,version_id=version,exact=exact,prefix=None,suffix=None,article=None,
        section=section,pdf_page_index=index,printed_page=None)
    add('manual_passage',passage_id=pid,checked_at=now,method='Resmî Gazete PDF’si Poppler görüntüsünden sayfa bazında okundu.',
        reason='İlk sayfada yalnız kontrol karakterleri çıkıyor. Son iki sayfada metin katmanı bulunmadı. Üç özgün sayfa görsel okundu.')
out=checks/'aym-2021-source-records.json'
with out.open('x') as handle:
    handle.write(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0412-aym-2021-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),sha256(out.read_bytes()).hexdigest())
