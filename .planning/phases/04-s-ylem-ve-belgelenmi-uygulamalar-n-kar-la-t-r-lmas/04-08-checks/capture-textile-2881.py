"""Archive the 10/2881 motion, 104th sitting and the separate 7/29149 exchange."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_exists, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/yeni-yol')
stem = '0408-textile-2881'
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
    ('register.html', 'register', '10/2881 Meclis araştırması esas kaydı', None, 'TBMM',
     'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/3851a66e-d9a0-4163-86d9-0197d0cb34ae',
     '9fd3ae5c18b74d7a1872328143a01f74b6abbbba18efabc94393ce5814065266', (
        ('number','10/2881 esas numarası',None,'10 / 2881'),
        ('day','Başkanlığa geliş tarihi',None,'02/07/2025'),
        ('sponsor','Önerge sahibi milletvekilleri',None,'Mersin Milletvekili Mehmet Emin Ekmen ve 21 Milletvekili'),
        ('pending','23 Kasım erişiminde esas kaydının durumu',None,'G&#xFC;ndemde'),
     )),
    ('signed-2881.pdf', 'signed', '10/2881 on sayfa imzalı önerge', '2025-07-02', 'TBMM',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T10/WebOnergeMetni/98284e17-4110-42df-846c-cb35430b1dc9.pdf',
     '906c068f1b94f067387ffcb74a0639cec9b76d52a9180a59f49cd9ddad7505de', (
        ('number','İmzalı önerge numarası',0,'10/2881'),
        ('scope','Gerekçede finansman, ihracat kayıpları ve istihdam etkileri',8,'ihracat kay1plarmm ve istihdam tizerindeki'),
        ('first-value','Ön yazıda 2023 hazır giyim ihracatı',0,'19 ,3 milyar dolarhk ihracat'),
        ('rationale-value','Özet gerekçede 2023 hazır giyim ihracatı',2,'2023 yilmda %9 kil9illme ile 19 .2'),
        ('signer','Son sayfada Mersin imza satırı',9,'MEHMET EMİN EKMEN MERSİN'),
     )),
    ('floor.html','floor','2 Temmuz 104. Birleşim tam tutanağı','2025-07-02','TBMM',
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/104/Tam/1252814c-e8f1-40c6-ae66-f1d33b9950b8.html',
     '84c36043d410905c0227bc2ed17339ecd2fbc94fe0a58c6d0f40ea5afe57a679', (
        ('agenda','Birinci grup gündem önerisinin son cümlesi',None,'görüşmelerin 2 Temmuz 2025 Çarşamba günkü birleşimde yapılması önerilmiştir.'),
        ('role','Başkanın Ekmen’e grup adına söz vermesi',None,'YENİ YOL Partisi Grubu adına Mersin Milletvekili Sayın Mehmet Emin Ekmen.'),
        ('export','Ekmen’in 2023 hazır giyim ihracatı açıklaması',None,'2023 yılında 19,3 milyar dolarlık ihracatıyla'),
        ('vote','Yeni Yol önerisinin oylama sonucu',None,'Öneriyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Kabul edilmemiştir.'),
     )),
    ('agenda-107.html','collected','9 Temmuz 180 numaralı Gelen Kâğıtlar','2025-07-09','TBMM',
     'https://tbmm.gov.tr/Gundem/GelenKagitDetay/8628b7bb-058a-427c-972a-0197eeca4359',
     'f7368c50bae859f57733380f0b47cb0ed0898d286796720183bfa41513c2235e', (
        ('filed','Meclis araştırması önergeleri 26. sıra',None,'(10/2881) (Başkanlığa geliş tarihi:2.07.2025)'),
     )),
    ('question-reg.html','question-register','7/29149 yazılı soru ve yanıt sicili',None,'TBMM',
     'https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/e89f9794-ad0a-4a97-adee-019759024ed4',
     'b6985ef3286cc953b63eebb9c5395d362b19c074070aba9498a59306a6036ecc', (
        ('number','7/29149 esas numarası',None,'7 / 29149'),
        ('filed','Başkanlığa geliş tarihi',None,'04.06.2025'),
        ('day','Cevap bildiriliş tarihi',None,'09.07.2025'),
        ('late','TBMM cevap durum alanı',None,'S&#xFC;resi Ge&#xE7;tikten Sonra Cevapland&#x131;'),
     )),
    ('signed-29149.pdf','question','7/29149 imzalı yazılı soru','2025-06-04','TBMM',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/ef9dc092-3914-4fc4-8aaf-93aa0c3f5e31.pdf',
     '96509197fdd3056d73b6452193a6468396d0e9cf00c3e47720a26811ad7bf6fc', (
        ('request','4 Haziran imzalı yazılı cevap istemi',0,'cevaplandırılmasını saygılarımla arz ederim. 04/06/2025'),
        ('role','Soru sahibinin belge üzerindeki sıfatları',0,'Mehmet Emin EKMEN\nMersin Milletvekili\nDEVA Partisi Genel Başkan Yardımcısı'),
        ('counts','Konkordato sayısı ve il dağılımı sorusu',1,'konkordato ilan eden firma sayısı kaçtır?'),
        ('financing','Destek programları sorusu',1,'planlanan destek programları nelerdir?'),
        ('debt','Onuncu soru, borç yapılandırması',2,'firmaların borç yapılandırma süreçlerinde'),
     )),
    ('reply-29149.pdf','reply','7/29149 Ticaret Bakanlığı cevabı',None,'Ticaret Bakanlığı',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/6fda729d-d11b-4aa5-a49b-62c3a5bde292.pdf',
     '13e9a115616c248a340f2beeeffded65d167cb6fc7f9a51079dd64ac1fca0b4b', (
        ('number','Ticaret Bakanlığı kapakta soru kimliği',0,'Konu : Soru Önergesi (7/29149)'),
        ('tariff','Birinci ek sayfa, ithalat önlemleri',1,'hazır giyim ürünlerinin ithalatında yaklaşık olarak %51 oranında gümrük vergisi tesis edilmiştir.'),
        ('aggregate','İkinci ek sayfa, sektörler üstü ihracat desteği',2,'2024 yılında 17,6 milyar TL ödeme yapılmış'),
        ('kosgeb','Üçüncü ek sayfa, emek yoğun sektörlerin KOBİ desteği',3,'çalışan başına aylık 2 bin 500 TL geri ödemesiz destek sağlanmaktadır.'),
        ('bankruptcy','Üçüncü ek sayfa, konkordato verisi sınırı',3,'konkordato başvurularına ilişkin olarak Bakanlığımızda tutulan herhangi bir kayıt bulunmamakta'),
        ('sector','Dördüncü ek sayfa, MERSİS sektör sınırı',4,'sistemde sektörlere göre veriler tutulmamaktadır.'),
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
    add('document', id=doc, party_id='yeni-yol', title=title, source_kind='official')
    add('document_version', id=version, document_id=doc, original_url=url, final_url=url, document_date=day,
        date_precision='day' if day else 'unknown', date_unknown_reason=None if day else (
            'Bu nüshada belge tarihi ile sicildeki cevap bildiriliş günü ayrı değerlendirildi.' if label == 'reply'
            else 'Dinamik TBMM esas kaydının ilk yayın günü bilinmiyor.'),
        version_label='TBMM özgün kaynak nüshası.', accessed_at=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        verified_at=now, mime='application/pdf' if fmt == 'pdf' else 'text/html', sha256=digest,
        original_path=obj, readable_path=readable)
    add('source_attribution', version_id=version, publisher=publisher, author={'signed':'Mehmet Emin Ekmen ve 21 milletvekili','question':'Mehmet Emin Ekmen','reply':'Ömer Bolat'}.get(label),
        kind='official', published_at=day, date_precision='day' if day else 'unknown', social_handle=None, public_url=url,
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
        earlier, authority, remark, vote = (anchor[-1] for anchor in anchors)
        start = text.index(earlier)
        speaker = text.index(authority, start)
        approach = text.index(remark, speaker)
        decision = text.index(vote, approach)
        following = text.index('Sayın Ateş', decision)
        assert 0 < decision - approach < 30000 and following - decision < 500
    for suffix, section, index, exact in anchors:
        passage = f'{doc}-{suffix}'
        manual = fmt == 'pdf' and not pdf_page_text(root / obj, index).strip()
        if manual:
            assert pdf_page_exists(root / obj, index) and not pdf_page_text(root / obj, index).strip()
        else:
            text = pdf_page_text(root / obj, index) if fmt == 'pdf' else html_source_text(raw)
            assert exact in text, (label, suffix)
        add('passage', id=passage, version_id=version, exact=exact, prefix=None, suffix=None, article=None,
            section=section, pdf_page_index=index, printed_page=None)
        if manual:
            add('manual_passage', passage_id=passage, checked_at=now,
                method='Özgün PDF sayfası Poppler görüntüsünde okundu.',
                reason='İmza veya cevap pasajı taranmış görselden kontrol edildi.')
(checks / 'textile-2881-source-records.json').write_text(json.dumps(dict(party_id='yeni-yol', entries=entries), ensure_ascii=False, indent=2) + '\n')
(stage / 'textile-2881-source-paths').write_text('\n'.join(sorted(map(str, paths))) + '\n')
print(len(entries), len(paths))
