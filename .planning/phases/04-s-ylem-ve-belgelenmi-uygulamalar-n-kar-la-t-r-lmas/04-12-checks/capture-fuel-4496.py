"""Archive the 2/4496 statement, filing and official lapse passages."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path(sys.argv[1])
root = Path('data/practices/sources/demokrat')
case = '0412-fuel-4496'
party = 'demokrat'
reading_path = checks / 'fuel-4496-sources' / 'reading.json'
reading = json.loads(reading_path.read_bytes())
party_reading = json.loads((reading_path.parent / reading['party_source_ref']).read_bytes())
party_item = next(row for row in party_reading['examined'] if row['position'] == reading['party_position'])
sources = {row['original_path']: row for row in reading['sources']}
sources[party_item['original_path']] = dict(party_item, retrieved_at_utc=party_item['accessed_at'])
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
specs = {
    'party': ('party-news-web/150.html.bin', '2022-06-22', 'Neslihan Çevik’in 22 Haziran akaryakıt açıklaması',
              [('request', None, 'ikişer aylık periyotlarla piyasayı'),
               ('passage-request', None, 'ivedilikle TBMM'),
               ('prior-filing', None, 'bir kanun teklifi sunduk.')]),
    'signed': ('tbmm-2-4496-imzali.pdf', '2022-06-16', '2/4496 esas numaralı imzalı teklif',
               [('cover', 0, 'Gereğini Saygılarımla Arz Ederim. 16/06/2022'),
                ('assignment', 0, '17 Haziran 2022 Esas No: 2/4496'),
                ('term', 3, 'her seferinde iki ayı aşmamak üzere'),
                ('transition', 3, 'yayımı tarihini izleyen iki aylık süre boyunca')]),
    'arrival': ('tbmm-20220621-gelen.html.bin', '2022-06-21', 'TBMM 105. birleşim gelen kâğıtlar',
                [('arrival', None, '16.06.2022')]),
    'registry': ('tbmm-2-4496-sicil.html.bin', None, '2/4496 teklif sicili',
                 [('registry', None, '2 / 4496')]),
    'term-cover': ('tbmm-28-1-1-kapak.pdf', '2023-06-02', '28. dönem 1. birleşim tutanak kapağı',
                   [('opening', 0, '2 Haziran 2023 Cuma')]),
    'term-leaf': ('tbmm-28-1-1-hukumsuz-p203.pdf', '2023-06-02', 'Hükümsüz sayılan milletvekili teklifleri listesi',
                  [('lapse', 0, '4213 2/4496'),
                   ('heading', 0, 'HÜKÜMSÜZ SAYILAN MİLLETVEKİLİ TEKLİFLERİ')]),
}
sections = {
    'request': 'Parti açıklamasında iki aylık EPDK düzenleme çağrısı',
    'passage-request': 'Teklifin Meclisten geçirilmesi çağrısı',
    'prior-filing': 'Sözcünün daha önceki teklif sunuşuna değinmesi',
    'cover': 'İmzalı teklifin 16 Haziran tarihli sunuş yazısı',
    'assignment': 'Teklifin 17 Haziran komisyon sevk kaşesi',
    'term': '2/4496 madde 1, iki ayı aşmayan fiyat yetkisi önerisi',
    'transition': '2/4496 madde 2, önerilen geçici madde 8',
    'arrival': 'TBMM gelen kâğıtlarda 2/4496 Başkanlığa geliş günü',
    'registry': 'Teklif sicilinde 2/4496 esas numarası',
    'opening': '28. dönem ilk birleşiminin tarihi',
    'lapse': 'Hükümsüz teklifler tablosunda 4213. sıra',
    'heading': 'Basılı 203. sayfanın hükümsüz teklifler başlığı',
}
entries = []


def add(table, **values):
    entries.append({'kind': table, 'values': values})


for role, (filename, day, title, anchors) in specs.items():
    is_party = role == 'party'
    src = checks / filename if is_party else reading_path.parent / filename
    row = sources[filename]
    raw = src.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest == row['sha256']
    url = row['url']
    final = row.get('retrieved_url', url)
    fmt = 'pdf' if filename.endswith('.pdf') else 'html'
    obj = root / 'objects' / digest
    obj.mkdir(parents=True, exist_ok=True)
    original = obj / ('original.pdf' if fmt == 'pdf' else 'original.html.bin')
    readable = obj / 'readable.html'
    if role == 'arrival':
        # The outer TBMM page is UTF-8, with an embedded Windows-1254 declaration.
        raw.decode('utf-8', errors='strict')
    for target, blob in ((original, raw), (readable, readable_bytes(raw, fmt, legacy=role == 'arrival'))):
        if target.exists():
            assert target.read_bytes() == blob, target
        else:
            target.write_bytes(blob)
    doc = case + '-' + role
    version = doc + '-v1'
    add('document', id=doc, party_id=party, title=title, source_kind='party' if is_party else 'official')
    add('document_version', id=version, document_id=doc, original_url=url, final_url=final,
        document_date=day, date_precision='day' if day else 'unknown',
        date_unknown_reason=None if day else 'Güncel sicil görünümünün ilk yayımlanma günü bilinmiyor.',
        version_label=title,
        accessed_at=row['retrieved_at_utc'], verified_at=now, mime='application/pdf' if fmt == 'pdf' else 'text/html',
        sha256=digest, original_path=str(original.relative_to(root)), readable_path=str(readable.relative_to(root)))
    add('source_attribution', version_id=version, kind='party_publication' if is_party else 'official',
        publisher=row['publisher'], author='Neslihan Çevik' if is_party else None, social_handle=None,
        published_at=day, date_precision='day' if day else 'unknown', public_url=url, basis=row['reading'])
    if fmt == 'html':
        view = build_view(raw, final, root, fetch_assets=False,
                          http_charset='utf-8' if role == 'arrival' else None)
        view['version_id'] = version
        validate_view(root, view)
        add('archive_view', **view)
    for suffix, page, exact in anchors:
        pid = doc + '-' + suffix + '-p'
        content = html_source_text(raw) if page is None else pdf_page_text(src, page)
        assert exact in content, (role, suffix)
        add('passage', id=pid, version_id=version, exact=exact, prefix=None, suffix=None,
            article={'term': '1', 'transition': '2'}.get(suffix),
            section=sections[suffix], pdf_page_index=page,
            printed_page='203' if role == 'term-leaf' else ('1' if role == 'term-cover' else None))

with (checks / 'fuel-4496-source-draft.json').open('x') as fh:
    json.dump({'entries': entries}, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
print('DEMOCRAT_4496_SOURCE_CAPTURE_OK', len(entries))
