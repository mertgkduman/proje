"""Archive debate, grain prices, payment announcements and the original policy statement."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_exists, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/saadet')
stem = '0411-hububat'
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def store(relative, content):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == content
    else:
        path.write_bytes(content)
    paths.add(path)


sources = (
    ('arikan-tv5.html', 'statement', '10 Haziran Arıkan hububat grup açıklaması', '2026-06-10', 'TV5',
     'https://www.tv5.com.tr/mahmut-arikan-anayasa-yeni-donemin-siyasi-kapisi-yapilmak-isteniyor',
     '3f0b1fb8e5c7e84302b9be141194e521574578675b3aa23dabfd0eb760033bec', (
         ('day', 'TV5 haberinin yayın tarihi', None, '2026-06-10T13:57:00+03:00'),
         ('delivery', 'Arıkan’ın teslim anında ödeme açıklaması', None, 'TMO ürün bedelini 45 gün sonra değil, teslimde ödeyecek.'),
         ('quote', 'Arıkan’ın teslim anında ödeme ifadesi', None, 'teslimde ödeyecek'),
         ('cost', 'Arıkan’ın yaklaşık maliyet örneği', None, '24 lira açıklarsa çiftçi ancak maliyetini karşılayabilecek.'),
     )),
    ('price.html', 'price', '2 Haziran Bakanlık hububat alım fiyatı ve ödeme duyurusu', '2026-06-02', 'Tarım ve Orman Bakanlığı',
     'https://www.tarimorman.gov.tr/Haber/7092/2026-Yili',
     'c9a58e7cedd1ca403f440fc7835b8272d79a5f2fc683839cd30f7c644d7d2f5b', (
         ('group', 'İkinci grup ürünler için alım fiyatı', None, '2. grup ürünler için'),
         ('wheat', 'İkinci grup buğday ton fiyatı', None, '16.500 TL'),
         ('barley', 'İkinci grup arpa ton fiyatı', None, '12.750 TL'),
         ('support', 'Ortalama verim varsayımıyla ton başı destek eşdeğeri', None, '3.014 TL'),
         ('window', '2 Haziran ilanındaki teslim sonrası ödeme süresi', None, '45 gün içerisinde üreticilerin banka hesaplarına'),
     )),
    ('register.html', 'register', '10/4251 Meclis araştırması esas kaydı', None, 'TBMM',
     'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/a811a383-a3c9-49f8-b0e3-019ed4c70335',
     'ea1ebdc79e7e2cb752315f208afbfaae6b483744c01f034b3fc1eff61cf56505', (
         ('number', '10/4251 esas numarası', None, '10 / 4251'),
         ('day', 'Başkanlığa geliş tarihi', None, '10/06/2026'),
         ('pending', 'TBMM erişiminde açık dosya durumu', None, 'G&#xFC;ndemde'),
     )),
    ('signed-4251.pdf', 'signed', '10/4251 dört sayfa imzalı önerge', '2026-06-10', 'TBMM',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T10/WebOnergeMetni/be0f67fd-5e2a-4717-a037-397eb2a96192.pdf',
     '89b5cccc0478e8012cf5b64b24df7ca18fafe630903dad4df65dd3477cadd760', (
         ('number', 'İmzalı önerge numarası', 0, '10/4251'),
         ('scope', 'Gerekçede fiyat ölçütleri ve maliyet ile üretici geliri ilişkisi', 2, 'üretim maliyetleri ile üretici gelirleri arasındaki ilişkinin'),
     )),
    ('floor.html', 'floor', '10 Haziran 100. Birleşim tam tutanağı', '2026-06-10', 'TBMM',
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/100/Tam/b3917591-905c-4114-ab4d-70a37fd266fa.html',
     '6a870294ea7992b5fa674a5298ba876c9a0c4db52ebab0dd570391b58c08c8c2', (
         ('agenda', 'Yeni Yol imzalı gündem önerisinin son cümlesi', None, 'görüşmelerin 10/6/2026 Çarşamba günkü birleşimde yapılması önerilmiştir.'),
         ('role', 'Birleşim başkanının Yeni Yol adına Şerafettin Kılıç’a söz vermesi', None, 'YENİ YOL Partisi Grubu adına Antalya Milletvekili Sayın Şerafettin Kılıç.'),
         ('days', 'Abdullah Doğru’nun ödeme süresi açıklaması', None, 'yirmi bir günde ödeneceğiyle ilgili'),
         ('vote', 'İlk grup önerisinin sonuç cümlesi', None, 'Öneri kabul edilmemiştir.'),
     )),
    ('pay.html', 'pay', '25 Haziran TMO ilk ödemeler açıklaması', '2026-06-25', 'Tarım ve Orman Bakanlığı',
     'https://www.tarimorman.gov.tr/Haber/7126/',
     '0e954f0afa09640282e55d36411e9b637af345db926a1abcb9dec1b6688aaf9c', (
         ('day', 'Bakanlık duyurusunun günü', None, '25.06.2026'),
         ('start', 'Bakanın ilk ödemelerin aktarılmasını açıklaması', None, 'ilk ödemeleri çiftçilerimizin hesaplarına bugün aktarıyor.'),
         ('rule', 'Bakanın açıkladığı yeni başlangıç günü', None, "21'inci günden itibaren üreticilerimizin hesaplarına"),
     )),
    ('jul.html', 'july', '27 Temmuz Bakanlık hububat alım ve ödeme toplamları', '2026-07-27', 'Tarım ve Orman Bakanlığı',
     'https://vskn.tarimorman.gov.tr/trabzon/Sayfalar/GormeEngellilerDetay.aspx?Liste=Haber&OgeId=147',
     '1981854ab7474ceea1549abee517fe7a068cb3a9de535f682c42afb4a221e5d6', (
         ('day', 'Bakanlık aktarımının yayın günü', None, '27.07.2026'),
         ('amount', 'Bakanın toplam üretici ve ton olarak alım duyurusu', None, '176 bin üreticiden 8,3 milyon ton'),
         ('payment', 'Bakanın o tarihe kadar açıkladığı ödeme toplamı', None, '34,3 milyar lira üreticilerin hesaplarına aktarıldı'),
     )),
    ('aug.html', 'august', '17 Ağustos Bakanlık hububat alım ve ödeme toplamları', '2026-08-17', 'Tarım ve Orman Bakanlığı',
     'https://www.tarimorman.gov.tr/Haber/7228/',
     '106b3d41286554b9686ad4f2919090f61c26a5e13d88103c80c4fa420b345dd0', (
         ('day', 'Bakanlık yayım günü', None, '17.08.2026'),
         ('amount', 'Hasat sezonundan bu yana bildirilen alım miktarı', None, '11,5 milyon ton ürün alındı.'),
         ('payment', 'Bakanın o tarihe kadar açıkladığı yaklaşık ödeme', None, '120 milyar lira ödeme yapıldığını açıkladı'),
     )),
)
for filename, label, title, day, publisher, url, digest, anchors in sources:
    path = stage / filename
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == digest
    fmt = 'pdf' if filename.endswith('.pdf') else 'html'
    doc = f'{stem}-{label}'
    version = f'{doc}-v1'
    obj = f'objects/{digest}/' + ('original.pdf' if fmt == 'pdf' else 'original.html.bin')
    readable = f'objects/{digest}/readable.html'
    store(obj, raw)
    store(readable, readable_bytes(raw, fmt, legacy=False))
    add('document', id=doc, party_id='saadet', title=title, source_kind='journalism' if label == 'statement' else 'official')
    add('document_version', id=version, document_id=doc, original_url=url, final_url=url, document_date=day,
        date_precision='day' if day else 'unknown', date_unknown_reason=None if day else 'Dinamik TBMM esas kaydının ilk yayın günü bilinmiyor.',
        version_label='TBMM özgün kaynak nüshası.', accessed_at=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        verified_at=now, mime='application/pdf' if fmt == 'pdf' else 'text/html', sha256=digest,
        original_path=obj, readable_path=readable)
    add('source_attribution', version_id=version, publisher=publisher, author='Bülent Kaya ve 19 milletvekili' if label=='signed' else None,
        kind='journalism' if label == 'statement' else 'official', published_at=day, date_precision='day' if day else 'unknown', social_handle=None, public_url=url,
        basis='Kurum duyurusu, Meclis işlemi veya konuya ilişkin tarihli konuşma aktarımı.')
    if fmt == 'html':
        view = build_view(raw, url, root, fetch_assets=False)
        view['version_id'] = version
        validate_view(root, view)
        manifest = root / view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent / name for name in json.loads(manifest.read_bytes())['files'])
        add('archive_view', **view)
    if label == 'floor':
        text = html_source_text(raw)
        agenda, role, days, vote = (anchor[-1] for anchor in anchors)
        start = text.index(agenda)
        speaker = text.index(role, start)
        timing = text.index(days, speaker)
        decision = text.index(vote, timing)
        assert 0 < decision - timing < 6000
    for suffix, section, index, exact in anchors:
        passage = f'{doc}-{suffix}'
        manual = label == 'signed' and suffix != 'number'
        if manual:
            assert pdf_page_exists(root / obj, index) and not pdf_page_text(root / obj, index).strip()
        else:
            text = pdf_page_text(root / obj, index) if fmt == 'pdf' else html_source_text(raw)
            assert exact in text, (label, suffix)
        add('passage', id=passage, version_id=version, exact=exact, prefix=None, suffix=None, article=None,
            section=section, pdf_page_index=index, printed_page=None)
        if manual:
            add('manual_passage', passage_id=passage, checked_at=now,
                method='Özgün dört imzalı PDF sayfası Poppler görüntüsünde okundu.',
                reason='İmza veya gerekçe pasajı taranmış görselden kontrol edildi.')
(checks / 'hububat-source-records.json').write_text(json.dumps(dict(party_id='saadet', entries=entries), ensure_ascii=False, indent=2) + '\n')
(stage / 'hububat-source-paths').write_text('\n'.join(sorted(map(str, paths))) + '\n')
print(len(entries), len(paths))
