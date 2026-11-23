"""Archive two distinct TBMM agricultural proposals and their institutional context."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_exists, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path,sys.argv[1:])
root = Path('data/practices/sources/demokrat')
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def store(relative, content):
    path = root/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes() == content
    else:
        path.write_bytes(content)
    paths.add(path)


sources = (
    (
        'signed-3485.pdf',
        'signed-3485',
        '2/3485 imzalı kanun teklifi',
        '2026-01-20',
        None,
        'TBMM',
        'official',
        'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T2/WebOnergeMetni/ce930adf-176c-4496-b0fe-3395a3a990be.pdf',
        '4f42dc58166d91edcbb976a7df6c5daa690d1c126b726dc563dec8f817ac8cc3',
        (
            ('id', 'Kapakta esas numarası ve sevk günü', 0, 'Tarih: 21-1-2026 Esas No:2/3485'),
            ('sender', 'Kapakta imza ve seçim çevresi', 0, 'Haydar ALTINTAŞ\nİzmir Milletvekili'),
            ('clearance', 'Madde 2, borcu yoktur belgesi', 4, 'için "borcu yoktur" belgesi şartı aranamaz.'),
            ('term', 'Madde 3, borç vadesi', 4, 'üzere faizsiz şekilde belirlenecek uzun vadeye yayılır.'),
            ('disaster', 'Madde 4, zarar tespiti', 4, 'yan, zarar tespit ve telafi mekanizmalan'),
        ),
    ),
    (
        '3485.html',
        'register-3485',
        '2/3485 TBMM teklif sicili',
        None,
        None,
        'TBMM',
        'official',
        'https://tbmm.gov.tr/Yasama/KanunTeklifi/e9390837-f03e-4bde-956e-019bdbdc69e8',
        '8e194063a4e607530b800ec63b6012b9b8654f69d7848fe239db25aabdccf3ff',
        (
            ('id', 'Esas numarası', None, '<td>2 / 3485</td>'),
            ('filed', 'Başkanlığa geliş tarihi', None, '<td>20/01/2026</td>'),
            ('referred', 'Komisyon giriş tarihi', None, '<td>21/01/2026</td>'),
            ('pending', 'Komisyon işlem alanı', None, '<td>Komisyonda</td>'),
            ('membership', 'İlk imza tablosunda milletvekili ve parti', None, 'Haydar ALTINTA&#x15E;\n\n                                            </a>\n                                        </td>\n                                        <td>DEMOKRAT PART&#x130;</td>'),
        ),
    ),
    (
        'signed-3970.pdf',
        'signed-3970',
        '2/3970 imzalı kanun teklifi',
        '2026-10-21',
        None,
        'TBMM',
        'official',
        'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T2/WebOnergeMetni/d5bcabf6-79ab-47ae-ad1c-8480d551ba06.pdf',
        '177c8b1b2d57046ee1d82b69dc5719cd843e1b433316f5f0ccee274ca3af810a',
        (
            ('id', 'Kapakta 21 Ekim imza ve 23 Ekim sevk', 0, 'Gereğini arz ederim. 21.10.2026'),
            ('stamp', 'İkinci sayfa Genel Evrak kaşesi', 1, '22 Ekim 2026'),
            ('floor', 'Madde 1, bütçe ödeneğinin alt sınırı', 4, 'Gayrisafi Yurt İçi Hasılanın yüzde birinden az olamaz.'),
            ('advance', 'Madde 1, ekim ve dikim öncesi avans', 4, 'Tahsis edilen destekleme tutarlarının en az yüzde ellisi, üretim takvimi esas alınarak ekim ve dikim döneminden önce üreticilere avans olarak ödenir.'),
            ('tax', 'Madde 2, girdi vergisi istisnası', 4, 'motorin ve gübre teslimleri, Katma Değer Vergisi ile Özel Tüketim Vergisinden müstesnadır.'),
            ('guard', 'Madde 2, destekleme ödemesine ilişkin koruma', 4, 'haczedilemez, devir ve temlik edilemez, üzerine ihtiyati tedbir veya bloke konulamaz.'),
        ),
    ),
    (
        '3970.html',
        'register-3970',
        '2/3970 TBMM teklif sicili',
        None,
        None,
        'TBMM',
        'official',
        'https://tbmm.gov.tr/Yasama/KanunTeklifi/2fac46c3-762b-4883-a105-01a16387607c',
        '98e76e7eb7b3572c06e2a8b8cec08e643be8f8d70d1b742ab652243719541068',
        (
            ('id', 'Esas numarası', None, '<td>2 / 3970</td>'),
            ('filed', 'Başkanlığa geliş tarihi', None, '<td>22/10/2026</td>'),
            ('referred', 'Komisyon giriş tarihi', None, '<td>23/10/2026</td>'),
            ('pending', 'Komisyon işlem alanı', None, '<td>Komisyonda</td>'),
            ('membership', 'İlk imza tablosunda milletvekili ve parti', None, 'Haydar ALTINTA&#x15E;\n\n                                            </a>\n                                        </td>\n                                        <td>DEMOKRAT PART&#x130;</td>'),
        ),
    ),
    (
        'agenda-oct.html',
        'agenda-3970',
        'TBMM Gelen Kâğıtlar 16, 23 Ekim 2026',
        '2026-10-23',
        '2026-10-23',
        'TBMM',
        'official',
        'https://tbmm.gov.tr/Gundem/GelenKagitDetay/ef13e007-e5e7-44da-a2b1-01a167d32d03',
        '72b8f3d437709e4126b993b3d2ebb31d436f97400020ab222fe8fa8c5cc6243f',
        (
            ('filed', 'Milletvekili teklifleri birinci sıra', None, 'Teklifi (2/3970) (Tarım, Orman ve K&ouml;yişleri ile Plan ve B&uuml;t&ccedil;e Komisyonlarına)'),
        ),
    ),
    (
        'ministry-credit.html',
        'ministry',
        'Ardahan İl Müdürlüğü tarımsal kredi düzenlemesi duyurusu',
        '2026-02-17',
        '2026-02-17',
        'Ardahan İl Tarım ve Orman Müdürlüğü',
        'official',
        'https://ardahan.tarimorman.gov.tr/Haber/1460/15-Subat-2026-Tarihli-Resm%C3%AE-Gazetede-Yayimlanan-Cumhurbaskani-Karari-Ile-Hazine-Faiz-Destekli-Tarimsal-Uretim-Kredisine-Erisimi-Kolaylastirici-Duzenlemeler-Yapilmistir',
        '6b26c38ab75b290cfbd6534544d6a94ac7e48919cebd12b8461c844709daf3d1',
        (
            ('day', 'Haber yayımlanma günü', None, '17.02.2026 /'),
            ('publication', 'Duyuru başlığı, Resmî Gazete yayımı', None, '15 Şubat 2026 tarihli Resmî Gazete’de yayımlanan Cumhurbaşkanı Kararı'),
            ('clearance', 'Borcu olmayanlar için belge süresi', None, 'Vergi ve SGK borcu bulunmayan üreticiler için belge süresi 15 gün olarak belirlenmiştir.'),
            ('offset', 'Mahsup ve kredi oranı', None, 'kredi tutarının azami %25’i borçlara mahsup edilerek'),
            ('cap', 'Yıllık mahsup üst sınırı', None, '300.000 TL ile sınırlandırılmıştır.'),
            ('exemption', 'Temel üretim için aynî kredi koşulu', None, '400.000 TL’ye kadar aynî kredilerde 31.12.2026 tarihine kadar borcu yoktur şartı aranmayacaktır.'),
        ),
    ),
    (
        'passed-5488.html',
        'enacted-5488',
        '5488 sayılı Tarım Kanununun kabul edilen ilk metni',
        '2006-04-18',
        None,
        'TBMM',
        'official',
        'https://cdn.tbmm.gov.tr/KKBSPublicFile/D22/Y3/T1/KanunMetni/741ac98e-b41b-45f0-b5c6-0f8907a69691.html',
        '33be33c65ce9b79739c714693ace65c7b5ea78743f854fbe88200e039ae5a1ef',
        (
            ('floor', 'Kabul edilen ilk metinde 21. madde', None, 'gayrisafi millî hasılanın yüzde birinden az olamaz.'),
        ),
    ),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0412-agri-credit-'+key
    vid=doc+'-v1'
    obj=f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable=f'objects/{digest}/readable.html'
    store(obj,raw)
    store(readable,readable_bytes(raw,'pdf' if pdf else 'html',legacy=False))
    add('document',id=doc,party_id='demokrat',title=title,source_kind=kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,
        date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Dinamik kayıt ilk yayın gününü belirtmiyor.',
        version_label='Özgün kurum veya parti nüshası.',accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='application/pdf' if pdf else 'text/html',sha256=digest,original_path=obj,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author=None,kind='official' if kind=='official' else 'party_publication',
        published_at=published,date_precision='day' if published else 'unknown',social_handle=None,public_url=url,
        basis='Özgün üst başlık ve varsa gün, parti, ilk imza ve kurum bağlamı birlikte okundu.')
    if not pdf:
        view=build_view(raw,url,root,fetch_assets=False)
        view['version_id']=vid
        validate_view(root,view)
        manifest=root/view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
        add('archive_view',**view)
    for suffix,section,index,exact in anchors:
        text=pdf_page_text(root/obj,index) if pdf else html_source_text(raw)
        manual = pdf and not text.strip()
        assert (pdf_page_exists(root/obj,index) if manual else exact in text), (key,suffix)
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,
            article=None,section=section,pdf_page_index=index,printed_page=None)
        if manual:
            add('manual_passage',passage_id=doc+'-'+suffix, checked_at=now, method='Özgün dört imzalı PDF sayfası Poppler görüntüsünde okundu.', reason='Özgün taramanın belirtilen sayfası görsel olarak okundu.')
(checks/'agri-credit-source-records.json').write_text(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'agri-credit-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
