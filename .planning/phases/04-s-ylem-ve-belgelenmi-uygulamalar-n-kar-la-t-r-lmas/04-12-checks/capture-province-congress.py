"""Archive three provincial congresses and their separately reported outcomes."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
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
    ('afyon.html','afyon','Afyon Haber 16. Afyonkarahisar İl Kongresi','2025-12-14','2025-12-14','Afyon Haber','Afyon Haber Editör',
     'https://www.afyonhaber.com/demokrat-parti-afyonkarahisar-kongresi-yapildi',
     '940c8ed1aa3701b012f9aa6d3f9f4c2ab6c2c8824b8f5c2726c56d36832a168e', [
         ('day','14 Aralık tarihli haberin yayım künyesi',None,'2025-12-14T17:21:00+03:00'),
         ('congress','Afyon Haber kongrenin gerçekleşmesi ve genel başkanın katılımı',None,'16. Olağan Kongresi, Genel Başkan Gültekin Uysal’ın katılımıyla gerçekleşti.'),
         ('result','Afyon Haber tek liste ve Hikmet Bülbül sonu',None,'Tek listeyle gidilen seçimde mevcut başkan Hikmet Bülbül güven tazeledi.'),
         ('boards','Afyon Haber yeni yönetim ve disiplin kurulu listelerinin başlangıcı',None,'Yapılan seçimler sonucunda Hikmet Bülbül başkanlığındaki yeni yönetim ve disiplin kurulları şu isimlerden oluştu:'),
         ('delegates','Afyon Haber üst kurul delegeleri listesi',None,'Üst Kurul Delegeleri arasında Genel Başkan Gültekin Uysal, Hikmet Bülbül ve Adnan Demirel gibi isimler yer aldı.'),
     ]),
    ('afyonsehir.html','afyonsehir','Afyon Şehir haberinde 16. kongre sonucu','2025-12-14','2025-12-14','Afyon Şehir','Haber Merkezi',
     'https://afyonsehir.com/dp-il-baskani-hikmet-bulbul-guven-tazeledi/',
     'd11d8a2cf002a74d37e1caa425ab167b881fac81fb5789292bf3cced9c794b37', [
         ('result','Afyon Şehir mevcut başkanın tek listeli seçimde yeniden seçilmesi',None,'Hikmet Bülbül yeniden seçilerek güven tazelerken'),
     ]),
    ('odak.pdf','odak','Odak gazetesinde Afyonkarahisar kongresi ve delege seçimi','2025-12-15','2025-12-15','Odak Gazetesi','Ahmet Sarlık',
     'https://odakgazetesicom.teimg.com/odakgazetesi-com/uploads/2025/12/15-12-25.pdf',
     '0f30111d37a3a026b3920440770cf5e352ee74471f60d8d310eec608bccf6355', [
         ('site','Basılı sayfa 8. Derya Düğün Salonu ve önceki gün kongresi',7,'16. İl Kongresi, dün saat 14.00\nitibarıyla Uydukent Derya Düğün\nSalonu’nda yapıldı.'),
         ('result','Basılı sayfa 8. Tek liste ve Hikmet Bülbül’ün seçim sonucu',7,'mevcut İl Başkanı Hikmet Bülbül, de-\nlegelerin oylarıyla yeniden Demokrat\nParti Afyonkarahisar İl Başkanı seçil-'),
         ('delegate','Basılı sayfa 8. Adnan Demirel’in üst kurul delegeliği',7,'Parti üst kurul delegesi olarak seçildi.'),
     ]),
    ('tokat.html','tokat','Tokat Haber il kongresi ve oylamanın başlaması','2026-03-07','2026-03-07','Tokat Haber','Burhan Arar',
     'https://www.tokathaber.com.tr/tokatta-kongre-gunu-demokrat-parti-lideri-uysal-gundemi-degerlendirdi',
     '3ae3b5bb2cfbda4826f683149d961cfa8d6a1e2939494c5e511f70716feede5a', [
         ('day','Tokat Haber yayım künyesinde 7 Mart',None,'2026-03-07T15:05:00+03:00'),
         ('session','Tokat il kongresinin parti binasında yapılması',None,'Demokrat Parti Tokat İl Kongresi parti binasında gerçekleştirildi.'),
         ('list','Tokat il başkanı ve tek listenin bildirimi',None,'Seyfettin Yüksekkaya seçime tek liste ile girdi.'),
         ('opening','Tokat il kongresinde delege oylarının başlaması',None,'Delegelerin oy kullanma süreci başladı ve kongre programı devam etti.'),
     ]),
    ('tokat-may.html','tokat-may','Hürsöz haberinde 23 Mayıs Tokat il başkanlığı kaydı','2026-05-23','2026-05-23','Hürsöz Gazetesi',None,
     'https://www.hursozgazetesi.com/muhalefetten-mutlak-butlan-kararina-tokattan-sert-tepki-korkmayacagiz-sinecegiz-saniyorlar',
     '3222d7356043b21de42bec0b6396af6a337665907901b0b4b4257facf6751fbe', [
         ('position','23 Mayıs tarihli haberin il başkanı olarak adlandırdığı kişi',None,'Demokrat Parti Tokat İl Başkanı Seyfettin Yüksekkaya'),
     ]),
    ('konya.html','konya','Anadolu’da Bugün Konya İl Kongresi ve kurul listeleri','2026-03-29','2026-03-29','Anadolu’da Bugün','Evren Atcı',
     'https://www.anadoludabugun.com.tr/politika/konyada-demokrat-parti-kongresi-uysaldan-kritik-mesajlar/412898',
     'ffb6ff002f22c86d856dedbaaedb0baf1cb7791c3bdea7276a713242a707f3d3', [
         ('day','İlk yayım ve sonuç bölümünü taşıyan güncelleme künyesi',None,'2026-03-29T15:50:02+03:00'),
         ('session','Konya Olağan İl Kongresinin gerçekleşmesi',None,'Demokrat Parti’nin Olağan İl Kongresi, Genel Başkan Gültekin Uysal’ın katılımıyla Konya’da'),
         ('result','Güncellenen haberde başkan seçimi',None,'Kongrede Mehmet Ali Yavuz il başkanı olarak seçilirken yönetim kurulu listesi şu şekilde oluştu:'),
         ('board','Konya il yönetim kurulu asıl üye tablosu',None,'İL YÖNETİM KURULU ASİL ÜYELER'),
         ('discipline','Konya il disiplin kurulu asıl üye tablosu',None,'İL DİSİPLİN KURULU ASİL ÜYELERİ'),
         ('delegates','Konya Büyük Kongre delegeleri listesi',None,'BÜYÜK KONGRE DELEGELERİ'),
     ]),
)
for filename,key,title,date,published,publisher,author,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0412-province-congress-'+key
    vid=doc+'-v1'
    obj=f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable=f'objects/{digest}/readable.html'
    store(obj,raw)
    store(readable,readable_bytes(raw,'pdf' if pdf else 'html',legacy=False))
    add('document',id=doc,party_id='demokrat',title=title,source_kind='journalism')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,
        date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Dinamik kayıt ilk yayın gününü belirtmiyor.',
        version_label='Özgün kurum veya parti nüshası.',accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='application/pdf' if pdf else 'text/html',sha256=digest,original_path=obj,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author=author,kind='journalism',
        published_at=published,date_precision='day' if published else 'unknown',social_handle=None,public_url=url,
        basis='Haberin tarih, muhabir, yer, işlem ve sonuç bölümleri birlikte okundu.')
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
        assert exact in text,(key,suffix)
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,
            article=None,section=section,pdf_page_index=index,printed_page='8' if key == 'odak' else None)
(checks/'province-congress-source-records.json').write_text(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'province-congress-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
