import json
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path(__file__).resolve().parent
sources = checks / 'tezkere-1310-sources'
root = Path('data/practices/sources/emep')
reading = json.loads((sources / 'reading.json').read_text())
assert all((sources / ref).is_file() for ref in reading['source_review_refs'])
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
entries = []

source_specs = [
    ('emep-4265.html.bin', 'party', '2021-10-26', 'Selma Gürkan’ın 26 Ekim tezkere açıklaması'),
    ('tbmm-27-5-11.pdf', 'floor', '2021-10-26', 'TBMM 27. dönem 5. yasama yılı 11. birleşim'),
    ('tbmm-kanun-ve-karar-sicili.pdf', 'registry', None, 'TBMM Kanun ve Karar Sicili 1310 kaydı'),
    ('resmi-gazete-31642-fihrist.html.bin', 'gazette-index', '2021-10-28', '28 Ekim 2021 Resmî Gazete fihristi'),
    ('resmi-gazete-31642-karar-1310.pdf', 'gazette', '2021-10-28', '31642 sayılı Resmî Gazete’de 1310 sayılı karar'),
]
passage_specs = {
    'party': [
        ('scope', None, None, 'Parti açıklamasında tezkerenin konusu',
         'Irak ve Suriye’ye sınır ötesi operasyon konusunda Cumhurbaşkanına verilen yetkinin iki yıl daha uzatılmasına dair tezkere Meclise sunuldu.'),
        ('request', None, None, 'Selma Gürkan’ın oylama öncesi çağrısı',
         'Özellikle bugün tezkereye hayır demek'),
    ],
    'floor': [
        ('opening', 59, '60', '26 Ekim birleşiminin açılış saati', 'Açılma Saati: 15.00'),
        ('procedure', 82, '83', 'Danışma Kurulu görüşme usulü önerisi sonrası 3/1704’ün okunması',
         'Birinci sırada yer alan, (3/1704) esas numaralı Cumhurbaşkanlığı Tezkeresi’ni okutuyorum:'),
        ('term', 83, '84', '3/1704 tarih ve iki yıllık süre',
         'itibaren iki yıl uzatılmasına ilişkin Cumhurbaşkanlığı tezkeresi (3/1704)'),
        ('vote', 107, '108', 'Başkanın 3/1704 kabulünü açıklaması',
         'Tezkereyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Kabul edilmiştir.'),
    ],
    'registry': [
        ('number', 94, '88', 'TBMM karar tablosunda 1310', '35 27 5 11 26.10.2021 1310'),
    ],
    'gazette-index': [
        ('index', None, None, '28 Ekim 2021 fihristinde 1310',
         '1310 Türkiye’nin Millî Güvenliğine Yönelik Ayrılıkçı Hareketler'),
    ],
    'gazette': [
        ('publication', 0, '1', 'Resmî Gazete yayım tarihi ve sayısı',
         '28 Ekim 2021 PERŞEMBE\nResmî Gazete\nTBMM KARARI\nSayı : 31642'),
        ('term', 1, '2', 'Kararın son cümlesinde süre ve kabul günü',
         '30/10/2021 tarihinden itibaren iki yıl uzatılması Genel Kurulun 26/10/2021 tarihli 11’inci Birleşiminde kabul edilmiştir.'),
    ],
}


def add(table, **values):
    entries.append({'kind': table, 'values': values})


for filename, role, day, title in source_specs:
    source = sources / filename
    review = next(row for row in reading['sources'] if row['original_path'] == filename)
    url = review['url']
    final = review.get('retrieved_url', url)
    raw = source.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest == review['sha256']
    fmt = 'pdf' if filename.endswith('.pdf') else 'html'
    obj = root / 'objects' / digest
    obj.mkdir(parents=True, exist_ok=True)
    original = obj / ('original.pdf' if fmt == 'pdf' else 'original.html.bin')
    readable = obj / 'readable.html'
    for target, data in ((original, raw), (readable, readable_bytes(raw, fmt, legacy=False))):
        if target.exists():
            assert target.read_bytes() == data, target
        else:
            target.write_bytes(data)

    doc = '0410-tezkere-1310-' + role
    version = doc + '-v1'
    is_party = role == 'party'
    add('document', id=doc, party_id='emep', title=title, source_kind='party' if is_party else 'official')
    add(
        'document_version', id=version, document_id=doc, original_url=url, final_url=final,
        document_date=day, date_precision='day' if day else 'unknown',
        date_unknown_reason=None if day else 'Yasama Bülteni derlemesinin kesin yayım günü bu nüshada doğrulanamadı.',
        version_label=title, accessed_at=review['retrieved_at_utc'], verified_at=now,
        mime='application/pdf' if fmt == 'pdf' else 'text/html',
        sha256=digest, original_path=str(original.relative_to(root)), readable_path=str(readable.relative_to(root)),
    )
    add(
        'source_attribution', version_id=version, kind='party_publication' if is_party else 'official',
        publisher='Emek Partisi' if is_party else review['publisher'],
        author='Selma Gürkan' if is_party else None, social_handle=None,
        published_at=day, date_precision='day' if day else 'unknown',
        public_url=url, basis=review['reading'],
    )
    if fmt == 'html':
        view = build_view(raw, final, root, fetch_assets=False, http_charset='utf-8')
        view['version_id'] = version
        validate_view(root, view)
        add('archive_view', **view)

    for suffix, page, printed, section, exact in passage_specs[role]:
        pid = doc + '-' + suffix + '-p'
        content = html_source_text(raw) if page is None else pdf_page_text(source, page)
        optical = role == 'gazette' and page == 1
        if optical:
            assert not content.strip(), (role, page)
        else:
            assert exact in content, (role, page, exact)
        add(
            'passage', id=pid, version_id=version, exact=exact, prefix=None, suffix=None,
            article=None, section=section, pdf_page_index=page, printed_page=printed,
        )
        if optical:
            add(
                'manual_passage', passage_id=pid, checked_at=now,
                method='Özgün Resmî Gazete PDF sayfası Poppler ve Cairo ile görselleştirilerek okundu.',
                reason='İkinci sayfanın metin katmanı boş. Kararın son cümlesi ve tutanak kabul pasajı karşılaştırıldı.',
            )

out = checks / 'tezkere-1310-source-draft.json'
with out.open('x') as fh:
    json.dump({'entries': entries}, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
print('TEZKERE_1310_SOURCE_CAPTURE_OK', len(entries))
