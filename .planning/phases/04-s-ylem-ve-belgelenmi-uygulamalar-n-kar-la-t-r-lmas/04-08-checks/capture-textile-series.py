"""Archive the two İHKİB editions and their year-comparison tables."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import pdf_page_text, readable_bytes

checks, staging = map(Path, sys.argv[1:])
root = Path('data/practices/sources/yeni-yol')
now = datetime.now(timezone.utc).isoformat()
entries, paths, reads = [], [], []


def add(table, **values):
    entries.append(dict(kind=table, values=values))


sources = (
    (2023, 4, '5', '19.316.151 -9,2%', '7e53bf28e7c05fdce5d168502e342302a616dacbe09208c35b41ae8dbd26a8a7',
     'https://www.ihkib.org.tr/content/files/uploads/49/2023-4-hazirgiyim-ve-konfeksiyon-sektoru-ocak-aralik-donemsel-bilgi-notu.pdf'),
    (2024, 3, '4', '19.242.984 -9,20 17.920.376', '7b8c2e90394b4f27564c39f131890764cc83a9a30663bef3a6982098dfa304c8',
     'https://ihkib.org.tr/content/files/uploads/49/2024-4-hazirgiyim-ve-konfeksiyon-sektoru-ocak-aralik-donemsel-bilgi-notu.pdf'),
)
for year, index, printed, row, expected, url in sources:
    source = staging / f'ihkib-{year}.pdf'
    raw = source.read_bytes()
    assert sha256(raw).hexdigest() == expected and raw.startswith(b'%PDF-')
    original = f'objects/{expected}/original.pdf'
    readable = f'objects/{expected}/readable.html'
    for relative, content in ((original, raw), (readable, readable_bytes(raw, 'pdf', legacy=False))):
        dest = root / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            assert dest.read_bytes() == content
        else:
            dest.write_bytes(content)
        paths.append(dest)
    doc = f'0408-textile-series-{year}'
    version = f'{doc}-v1'
    publisher = 'İstanbul Hazır Giyim ve Konfeksiyon İhracatçıları Birliği'
    title = f'İHKİB {year} Ocak–Aralık hazır giyim ve konfeksiyon ihracat değerlendirmesi'
    add('document', id=doc, party_id='yeni-yol', title=title, source_kind='official')
    accessed = datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat()
    add('document_version', id=version, document_id=doc, original_url=url, final_url=url,
        document_date=None, date_precision='unknown', date_unknown_reason='Kapakta kapsanan yıl yazıyor. Yayım günü ayrı.',
        version_label='İHKİB’nin özgün dönem PDF’si.', accessed_at=accessed, verified_at=now,
        mime='application/pdf', sha256=expected, original_path=original, readable_path=readable)
    add('source_attribution', version_id=version, publisher=publisher, author=None, kind='official',
        published_at=None, date_precision='unknown', social_handle=None, public_url=url,
        basis='İHKİB’nin kendi sitesindeki rapor, tablo kaynağı İhracatçı Birlikleri Kayıtları.')
    selected = []
    for page_index in (3, 4, 5, 6):
        text = pdf_page_text(root / original, page_index)
        assert text
        selected.append(dict(pdf_page_index=page_index, characters=len(text), text_sha256=sha256(text.encode()).hexdigest()))
    text = pdf_page_text(root / original, index)
    for field, exact, title in (('value', row, f'{year} raporunda 2023 sütununu içeren sektör satırı'),
                                ('unit', 'Birim: 1000 $', f'{year} raporu sektör tablosunun birimi')):
        assert exact in text
        add('passage', id=f'{doc}-{field}', version_id=version, exact=exact, prefix=None, suffix=None,
            article=None, section=title, pdf_page_index=index, printed_page=printed)
    reads.append(dict(edition_year=year, publisher=publisher, public_url=url, sha256=expected, accessed_at=accessed,
        selected_pages=selected, optical_table_index=index, printed_page=printed, complete_body_read=False))
record = dict(party_id='yeni-yol', entries=entries)
for name, contents in (('textile-series-source-records.json', record), ('textile-series-readings.json', reads)):
    with (checks / name).open('x') as out:
        out.write(json.dumps(contents, indent=2, ensure_ascii=False) + '\n')
(staging / 'textile-series-source-paths').write_text('\n'.join(map(str, paths)) + '\n')
print('TEXTILE_SERIES_SOURCE_TABLES_OK', len(entries), sum(p['characters'] for r in reads for p in r['selected_pages']))
