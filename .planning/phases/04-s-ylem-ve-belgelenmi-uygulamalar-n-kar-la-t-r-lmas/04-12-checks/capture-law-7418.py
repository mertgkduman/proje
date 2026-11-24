"""Archive the passages used in the 7418 comparison."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path(sys.argv[1])
root = Path('data/practices/sources/demokrat')
case = '0412-law-7418'
party = 'demokrat'
reading_path = checks / 'law-7418-sources' / 'reading.json'
reading = json.loads(reading_path.read_bytes())
party_reading = json.loads((reading_path.parent / reading['party_source_ref']).read_bytes())
party_item = next(row for row in party_reading['examined'] if row['position'] == reading['party_listing_position'])
sources = {row['original_path']: row for row in reading['sources']}
sources[party_item['original_path']] = dict(
    party_item, retrieved_at_utc=party_item['accessed_at'],
    reading='Parti sayfası 6 Ekim tarihini, açıklama gövdesi 5 Ekim tarihini ve Neslihan Çevik’e atfı içeriyor.',
)
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
specs = {
    'party': ('party-news-web/126.html.bin', '2022-10-06', 'Neslihan Çevik’in 5 Ekim tarihli 2/4471 açıklaması',
              [('request', None, 'bu yasaya karşı durmaya'), ('article29', None, 'Halkı yanıltıcı bilgiyi alenen yayma'),
               ('headline', None, 'ilk iki maddesi'), ('body', None, 'ilk maddesi de kabul edildi.')]),
    'floor': ('tbmm-27-6-7.pdf', '2022-10-13', 'TBMM 27. dönem 6. yasama yılı 7. birleşim',
              [('article29', 27, '29’uncu madde kabul\nedilmiştir.'),
               ('bill', 61, 'Teklif kabul edilmiş ve kanunlaşmıştır.')]),
    'law': ('resmi-gazete-31987-kanun-7418.html.bin', '2022-10-18', '7418 sayılı kanunun Resmî Gazete yayımı',
            [('publication', None, '18 Ekim 2022'), ('article29', None, 'MADDE 217/A- (1)'),
             ('commencement', None, 'b) Diğer hükümleri yayımı tarihinde,')]),
    'court-index': ('resmi-gazete-32469-fihrist.html.bin', '2024-02-23', 'Resmî Gazete 32469 fihristi',
                    [('docket', None, '8/11/2023 Tarihli ve E: 2022/129, K: 2023/189 Sayılı Kararı')]),
    'court': ('resmi-gazete-32469-aym-2023-189.pdf', '2024-02-23', 'AYM E.2022/129, K.2023/189 kararı',
              [('header', 0, '23 Şubat 2024 CUMA\nResmî Gazete\nANAYASA MAHKEMESİ KARARI\nSayı : 32469'),
               ('review', 7, '217/A maddesinin Anayasa’ya aykırı olmadığına ve iptal talebinin REDDİNE'),
               ('stay', 7, 'talebinin REDDİNE 8/11/2023 tarihinde OYBİRLİĞİYLE karar verilmiştir.')]),
}
sections = {
    'request': 'Parti sözcüsünün 2/4471’e karşı çağrısı',
    'article29': '2/4471 ve 7418’in 29. maddesi',
    'headline': 'Parti sayfasının ilk iki maddeye ilişkin sunuşu',
    'body': '5 Ekim açıklamasının ilk madde ifadesi',
    'bill': '2/4471 teklifinin tamamının kabulü',
    'publication': '7418’in yayım günü',
    'commencement': '7418 madde 39(b) yürürlük hükmü',
    'docket': 'E.2022/129 K.2023/189 fihrist kaydı',
    'header': 'AYM kararının Resmî Gazete başlığı',
    'review': 'AYM V. Hükümde iptal istemi',
    'stay': 'AYM IV. Bölümde yürürlüğün durdurulması istemi',
}
entries = []


def add(table, **values):
    entries.append({'kind': table, 'values': values})


for role, (filename, day, title, anchors) in specs.items():
    src = checks / filename if role == 'party' else reading_path.parent / filename
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
    for target, blob in ((original, raw), (readable, readable_bytes(raw, fmt, legacy=False))):
        if target.exists():
            assert target.read_bytes() == blob, target
        else:
            target.write_bytes(blob)
    doc = case + '-' + role
    version = doc + '-v1'
    is_party = role == 'party'
    add('document', id=doc, party_id=party, title=title, source_kind='party' if is_party else 'official')
    add('document_version', id=version, document_id=doc, original_url=url, final_url=final,
        document_date=day, date_precision='day', date_unknown_reason=None, version_label=title,
        accessed_at=row['retrieved_at_utc'], verified_at=now, mime='application/pdf' if fmt == 'pdf' else 'text/html',
        sha256=digest, original_path=str(original.relative_to(root)), readable_path=str(readable.relative_to(root)))
    add('source_attribution', version_id=version, kind='party_publication' if is_party else 'official',
        publisher=row['publisher'], author='Neslihan Çevik' if is_party else None, social_handle=None,
        published_at=day, date_precision='day', public_url=url, basis=row['reading'])
    if fmt == 'html':
        view = build_view(raw, final, root, fetch_assets=False)
        view['version_id'] = version
        validate_view(root, view)
        add('archive_view', **view)
    for suffix, page, exact in anchors:
        pid = doc + '-' + suffix + '-p'
        content = html_source_text(raw) if page is None else pdf_page_text(src, page)
        if role == 'court' and page == 7:
            assert not content.strip()
            add('manual_passage', passage_id=pid, checked_at=now,
                method='Özgün Resmî Gazete PDF’sinin sekizinci sayfası Poppler ve Cairo üzerinden görsel okundu.',
                reason='Sekizinci sayfanın metin katmanı boş. E.2022/129 K.2023/189 aynı sayının fihristinde kayıtlı.')
        else:
            assert exact in content, (role, suffix)
        add('passage', id=pid, version_id=version, exact=exact, prefix=None, suffix=None,
            article='29' if suffix == 'article29' else None, section=sections[suffix],
            pdf_page_index=page, printed_page=None)
with (checks / 'law-7418-source-draft.json').open('x') as fh:
    json.dump({'entries': entries}, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
print('DEMOCRAT_7418_SOURCE_CAPTURE_OK', len(entries))
