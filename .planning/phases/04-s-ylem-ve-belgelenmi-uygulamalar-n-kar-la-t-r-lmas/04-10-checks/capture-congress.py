import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/emep')
checks = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks')
entries = []
specs = [
    ('cumhuriyet', '04010-emep-2023-cumhuriyet', 'https://www.cumhuriyet.com.tr/turkiye/yeni-emep-genel-baskani-seyit-aslan-cumhuriyete-konustu-karanliga-2155888', '2023-12-26', 'journalism', 'Cumhuriyet', 'Cengiz Karagöz', 'Seyit Aslan, yeni genel başkan seçildi.'),
    ('emep', '04010-emep-2023-party', 'https://www.emep.org/emepin-10-kongresinde-genel-baskan-seyit-aslan-oldu', '2023-12-25', 'party', 'Emek Partisi', 'Emep (site metadata)', 'Genel Başkan Seyit Aslan oldu'),
]
for filename, ident, url, date, kind, publisher, author, exact in specs:
    capture = Path('/tmp/gsd-0410-' + filename + '-2023.html')
    raw = capture.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert exact in html_source_text(raw)
    obj = root / 'objects' / digest
    obj.mkdir(parents=True, exist_ok=True)
    for name, data in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        path = obj / name
        if path.exists():
            assert path.read_bytes() == data
        else:
            path.write_bytes(data)
    view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
    view['version_id'] = ident + '-v1'
    validate_view(root, view)
    access = datetime.fromtimestamp(capture.stat().st_mtime, timezone.utc).isoformat(timespec='seconds')
    rows = [
        ('document', dict(id=ident, party_id='emep', title='EMEP 10. Kongresinde Seyit Aslan genel başkan seçimi', source_kind=kind)),
        ('document_version', dict(id=ident+'-v1', document_id=ident, original_url=url, final_url=url, document_date=date, version_label=date+' yayın tarihli haber', accessed_at=access, verified_at=datetime.now(timezone.utc).isoformat(timespec='seconds'), mime='text/html', sha256=digest, original_path='objects/'+digest+'/original.html.bin', readable_path='objects/'+digest+'/readable.html', date_precision='day', date_unknown_reason=None)),
        ('archive_view', view),
        ('passage', dict(id=ident+'-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='Genel başkan seçimi', pdf_page_index=None, printed_page=None)),
        ('source_attribution', dict(version_id=ident+'-v1', kind='journalism' if kind=='journalism' else 'party_publication', publisher=publisher, author=author, social_handle=None, published_at=date, date_precision='day', public_url=url, basis='Haber metni ve yayıncı/tarih künyesi özgün HTML baytlarında okundu; yayın tarihi kongre tarihi değildir.')),
    ]
    entries.extend(dict(kind=k, values=v) for k,v in rows)
    print(ident, digest, view['view_id'])
(checks/'congress-2023-source-draft.json').write_text(json.dumps(dict(status='draft_unvalidated', entries=entries, note='Cumhuriyet 26 Aralık önceki gün ifadesi kongreyi 24 Aralık olarak tarihler; parti duyurusu 25 Aralık. Her iki belge aynı olaya bağlanır.'), ensure_ascii=False, indent=2)+'\n')
