"""Archive the two July agenda records for the IYI Party package."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_exists, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/iyi')
stem = '0407-agenda-104'
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
    ('register.html','register-2881','10/2881 tekstil araştırması esas sicili',None,'TBMM',
     'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/3851a66e-d9a0-4163-86d9-0197d0cb34ae',
     '9fd3ae5c18b74d7a1872328143a01f74b6abbbba18efabc94393ce5814065266',(
         ('id','Tekstil araştırmasında esas numarası',None,'10 / 2881'),
         ('day','Tekstil araştırmasında Başkanlığa geliş tarihi',None,'02/07/2025'),
         ('pending','Tekstil araştırmasında sicil durumu',None,'G&#xFC;ndemde'),
     )),
    ('signed-2881.pdf','signed-2881','10/2881 imzalı tekstil araştırması','2025-07-02','TBMM',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T10/WebOnergeMetni/98284e17-4110-42df-846c-cb35430b1dc9.pdf',
     '906c068f1b94f067387ffcb74a0639cec9b76d52a9180a59f49cd9ddad7505de',(
         ('id','İmzalı tekstil araştırmasının kapak numarası',0,'10/2881'),
         ('scope','Tekstil araştırması gerekçesinde ihracat ve istihdam',8,'ihracat kay1plarmm ve istihdam tizerindeki'),
     )),
    ('register-2882.html','register-2882','10/2882 şap araştırması esas sicili',None,'TBMM',
     'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/c5be7c5a-af9d-4d9f-bb19-0197d0d18e59',
     'd4479239f56a8d3dfb95f9a8ec2546c11e5cbefe3ad4c25c47f6c51403249844',(
         ('id','Şap araştırması esas numarası',None,'10 / 2882'),
         ('day','Şap araştırmasında Başkanlığa geliş tarihi',None,'02/07/2025'),
         ('signers','Esas sicilinde Akalın ve 20 milletvekili',None,'Edirne Milletvekili Mehmet Akal&#x131;n ve 20 Milletvekili'),
         ('pending','Şap araştırmasında sicil durumu',None,'G&#xFC;ndemde'),
     )),
    ('signed-2882.pdf','signed-2882','10/2882 imzalı şap araştırması','2025-07-02','TBMM',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T10/WebOnergeMetni/bb1abb59-4233-4141-9ced-6769f9b2fe72.pdf',
     '6184e8293ee649541fcff7792ba5e159a920d4eb5101403f64fab03e456c89cb',(
         ('id','İmzalı şap araştırmasının kapak numarası',0,'10/2882'),
         ('scope','Şap araştırması gerekçesinde Bakanlık kapasitesi',1,'Tarım ve Orman Bakanlığı’nın hastalıkla mücadele kapasitesi'),
         ('signers','Akalın’ın kapak imzasına ek 20 isim içeren tablo',2,'Milletvekili Seçim Bölgesi İmza'),
     )),
    ('agenda-107.html','papers','9 Temmuz 180 sayılı Gelen Kâğıtlar','2025-07-09','TBMM',
     'https://tbmm.gov.tr/Gundem/GelenKagitDetay/8628b7bb-058a-427c-972a-0197eeca4359',
     'f7368c50bae859f57733380f0b47cb0ed0898d286796720183bfa41513c2235e',(
         ('2881','Gelen Kâğıtlarda 26. araştırma önergesi',None,'(10/2881) (Başkanlığa geliş tarihi:2.07.2025)'),
         ('2882','Gelen Kâğıtlarda 27. araştırma önergesi',None,'(10/2882) (Başkanlığa geliş tarihi:2.07.2025)'),
         ('signers','Gelen Kâğıtlarda Akalın ve 20 milletvekili',None,'Edirne Milletvekili Mehmet Akalın ve 20 Milletvekilinin'),
     )),
    ('floor.html','floor','2 Temmuz 104. Birleşim tam tutanağı','2025-07-02','TBMM',
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/104/Tam/1252814c-e8f1-40c6-ae66-f1d33b9950b8.html',
     '84c36043d410905c0227bc2ed17339ecd2fbc94fe0a58c6d0f40ea5afe57a679',(
         ('agenda-2881','Yeni Yol birinci grup gündem önerisi',None,'görüşmelerin 2 Temmuz 2025 Çarşamba günkü birleşimde yapılması önerilmiştir.'),
         ('authority-2881','Başkanın İYİ Parti Grubu adına Yasin Öztürk’e söz vermesi',None,'İYİ Parti Grubu adına Denizli Milletvekili Sayın Yasin Öztürk.'),
         ('branding-2881','Yasin Öztürk’ün markalaşma ve dijitalleşme çağrısı',None,'Tasarım, dijitalleşme ve markalaşma desteklenmeli'),
         ('vote-2881','İlk grup gündem önerisinin reddi',None,'Öneriyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Kabul edilmemiştir.'),
         ('signers-2882','Şap gündem metninde Akalın ve 19 milletvekili',None,'Mehmet Akalın ve 19 milletvekili tarafından, şap hastalığı başta olmak üzere'),
         ('authority-2882','Başkanın İYİ Parti Grubu adına Mehmet Akalın’a söz vermesi',None,'İYİ Parti Grubu adına Edirne Milletvekili Sayın Mehmet Akalın.'),
         ('research-2882','Akalın’ın Bakanlık kapasitesi ve ithalat araştırması çağrısı',None,'Tarım ve Orman Bakanlığının hastalıkla mücadele kapasitesinin, ithalat süreçlerinin'),
         ('vote-2882','İkinci grup gündem önerisinin reddi',None,'Öneriyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Kabul edilmemiştir.'),
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
    add('document', id=doc, party_id='iyi', title=title, source_kind='official')
    add('document_version', id=version, document_id=doc, original_url=url, final_url=url, document_date=day,
        date_precision='day' if day else 'unknown', date_unknown_reason=None if day else (
            'Dinamik TBMM esas kaydının ilk yayın günü bilinmiyor.'),
        version_label='TBMM özgün kaynak nüshası.', accessed_at=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        verified_at=now, mime='application/pdf' if fmt == 'pdf' else 'text/html', sha256=digest,
        original_path=obj, readable_path=readable)
    add('source_attribution', version_id=version, publisher=publisher, author={'signed-2881':'Mehmet Emin Ekmen ve 21 milletvekili','signed-2882':'Mehmet Akalın ve diğer imzacılar'}.get(label),
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
        markers = {row[0]: row[-1] for row in anchors}
        first = text.index(markers['authority-2881'])
        first_position = text.index(markers['branding-2881'], first)
        first_vote = text.index(markers['vote-2881'], first_position)
        second = text.index(markers['signers-2882'], first_vote)
        second_position = text.index(markers['authority-2882'], second)
        second_vote = text.index(markers['vote-2882'], second_position)
        assert 0 < first_vote-first_position < 20000
        assert 0 < second_vote-second_position < 32000
        assert text.index('Sayın Türkoğlu, buyurun.',second_vote)-second_vote < 350
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
(checks / 'agenda-104-source-records.json').write_text(json.dumps(dict(party_id='iyi', entries=entries), ensure_ascii=False, indent=2) + '\n')
(stage / 'agenda-104-source-paths').write_text('\n'.join(sorted(map(str, paths))) + '\n')
print(len(entries), len(paths))
