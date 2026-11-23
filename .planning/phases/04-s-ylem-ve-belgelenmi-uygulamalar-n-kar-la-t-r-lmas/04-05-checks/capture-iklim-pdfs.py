import ctypes, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import pdf_libraries, readable_bytes
root = Path('data/practices/sources/tip')
here = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
items = [('teklif', '/tmp/gsd-tip-iklim-teklif.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T2/WebOnergeMetni/c0986a6f-d636-4-4c89-a92f-5db951eeeb09.pdf'.replace('4-4c89', '4c89'), 'eae53f78c8b008900ccfdfbe0977178c85ed71bf07c8d05da4d91426aeb5ec58'), ('komisyon', '/tmp/gsd-tip-iklim-report.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T2/DosyaKomisyonRaporunuVerdi/d929e28a-eafd-472b-a1a7-21fc0232ac33.pdf', '49494200db59e30f3b7f33e9e59bfa82f3c7782d4bf0ad8b6eebe25075065fb0')]
pop, obj, _ = pdf_libraries()
for name, local, url, expected in items:
    path = Path(local); raw = path.read_bytes(); digest = hashlib.sha256(raw).hexdigest(); assert digest == expected
    doc = pop.poppler_document_new_from_file(path.resolve().as_uri().encode(), None, None); assert doc
    pages = pop.poppler_document_get_n_pages(doc); obj.g_object_unref(doc)
    target = root / 'objects' / digest; target.mkdir(parents=True, exist_ok=True)
    for filename, content in (('original.pdf', raw), ('readable.html', readable_bytes(raw, 'pdf'))):
        dest = target / filename
        if dest.exists(): assert dest.read_bytes() == content
        else: dest.write_bytes(content)
    receipt = {'url': url, 'sha256': digest, 'bytes': len(raw), 'pages': pages, 'accessed_at': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(), 'limitations': 'Erişim zamanı indirilen dosyanın son yazım zamanıdır; kaynak henüz tam okunmamış ve paket kapılarına alınmamıştır.'}
    (here / ('iklim-2927-' + name + '-capture.json')).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + chr(10))
    print(name, digest, pages, len(raw))
