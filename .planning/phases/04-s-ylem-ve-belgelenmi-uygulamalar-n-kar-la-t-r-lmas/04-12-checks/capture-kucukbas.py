"""Archive the small-ruminant program, its critics and reported local deliveries."""

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
    ('party.html','statement','23 Şubat Demokrat Parti küçükbaş projesi açıklaması','2026-02-23','2026-02-23','Demokrat Parti','party',
     'https://www.dp.org.tr/haber/demokrat-parti-genel-baskani-gultekin-uysal-in-kucukbas-hayvanciligi-desteklemeye-yonelik-ilan-edilen-projeye-ve-hayvancilik-sektorunun-sorunlarina-dair-yaptigi-basin-aciklamasi',
     '83199a6b2092036d8a3471d8345d8342c670dda65a98aef9776e903c81156989', [
         ('day','Parti açıklamasının tarihi',None,'23/02/2026'),
         ('target','Yem üretimi ve girdi maliyeti hedefi',None,'yem bitkileri &uuml;retimini artırarak, girdi maliyetlerini d&uuml;ş&uuml;rerek'),
         ('critique','Üreticiye hayvan dağıtılmasına ve maliyetlere ilişkin açıklama',None,'hayvan dağıtmak; meseleyi &ccedil;&ouml;zmek değil, sorunu ertelemektir'),
         ('quote','İthalatın kapsamı hakkında parti açıklaması',None,'ithalatı istisna haline getirip'),
     ]),
    ('launch.html','launch','21 Şubat Bakanlık küçükbaş proje duyurusu','2026-02-21','2026-02-21','Tarım ve Orman Bakanlığı','official',
     'https://www.tarimorman.gov.tr/Haber/6977/Kirsalda-Bereket-Kucukbasa-Destek-Projesi-Basliyo',
     'bcc65b47ef9de1033e6335f05d730b4b1262e8970d5332246875934a971e5ff4', [
         ('day','Bakanlık ilk proje duyurusu tarihi',None,'21.02.2026'),
         ('target','Üç yıllık proje kapsamında açıklanan 150 bin hayvan hedefi',None,'150 bin baş</strong> küçükbaş hayvan dağıtımı öngörülmektedir'),
     ]),
    ('apply.html','apply','1 Nisan Bakanlık başvuru açılışı','2026-04-01','2026-04-01','Tarım ve Orman Bakanlığı','official',
     'https://www.tarimorman.gov.tr/Haber/7019/Kirsalda-Bereket-Kucukbasa-Destek-Projesinde-Basvurular-Basladi',
     '1e536f1751bf3fe155bf0123eade98316614044135d93e183f0a4386a96c2a6c', [
         ('day','Bakanlık duyurusunda başvuru aralığı',None,'başvurular 1-30 Nisan 2026 tarihlerinde yapılabilecek.'),
         ('opened','Küçükbaş programı başvurularının açılması',None,'KIRSALDA BEREKET KÜÇÜKBAŞA DESTEK PROJESİNDE BAŞVURULAR BAŞLADI'),
         ('planned','Bakanın her 100 hayvan için üç aylık bakım desteği açıklaması',None,'100 küçükbaş hayvan için toplamda 3 aylık 45 bin TL destek ödemesi'),
     ]),
    ('instructions.pdf','instructions','Kırsalda Bereket Küçükbaşa Destek Projesi uygulama talimatı',None,None,'Tarım ve Orman Bakanlığı','official',
     'https://malatya.tarimorman.gov.tr/Belgeler/2026%20K%C4%B1rsalda%20Bereket/Kirsalda%20Bereket%20Ku%C3%A7ukbasa%20Destek%20Projesi%20Talimati.pdf',
     '9879e9d8aa8c555a09c7cc32d36ac6dfb1000a93a92351c38d4907b699d7515d', [
         ('window','C. Başvuru yerleri ve 1–30 Nisan aralığı',1,'Başvurular 01.04.2026 tarihinde başlayıp, 30.04.2026 mesai bitiminde sona erer.'),
         ('scores','D. İl ve puan sıralamasıyla hak sahipliği',3,'Tüm ülkede yapılan başvurular için il bazında puan sıralaması yapılarak TİGEM’e gönderilir.'),
         ('price','G. Başvuru sahibinin peşin veya krediyle hayvan bedelini ödemesi',4,'gerçekleşecek ve hak sahipleri hayvan bedellerini peşin veya kredi ile ödeyebilecektir.'),
         ('actual','H. Yerinde tespit edilen hayvan başına aylık bakım ve besleme desteği',5,'başına aylık olarak 150 TL bakım ve besleme gideri bedeli ödenecektir.'),
     ]),
    ('first.html','first','11 Haziran Bakanlık ilk etap sonuç açıklaması','2026-06-11','2026-06-11','Tarım ve Orman Bakanlığı','official',
     'https://www.tarimorman.gov.tr/Haber/7108/',
     'd89d63e9437d3ef252575cdc3318be0c5d2bfa2b1d26508775f1793963d01e27', [
         ('day','Bakanlığın ilk sonuç duyurusunun günü',None,'11.06.2026'),
         ('list','İl bazında asil ve yedek listelerin tamamlanması',None,'her il bazında asil ve yedek hak sahipleri listeleri oluşturuldu.'),
         ('sms','Geçerli başvurulara SMS bildirimleri',None,'SMS ile bilgilendirmeler yapıldı.'),
     ]),
    ('duzce.html','duzce','16 Eylül Düzce İl Müdürlüğü hayvan teslimi bildirimi','2026-09-16','2026-09-16','Düzce İl Tarım ve Orman Müdürlüğü','official',
     'https://duzce.tarimorman.gov.tr/Haber/1542/Kirsalda-Bereket-Kucukbasa-Destek-Projesi-Kapsaminda-100-Kucukbas-Hayvan-Teslim-Edildi',
     'cf77895907ed7a48fbd21d2cef9d269d97b532efe88933ccca32b1a89e389a0d', [
         ('day','Düzce İl Müdürlüğü teslim bildiriminin yayım tarihi',None,'16.09.2026'),
         ('delivery','Gümüşova Halilbey köyünde bildirilen teslim',None,'95’i dişi ve 5’i erkek olmak üzere toplam 100 küçükbaş hayvan teslim edildi.'),
         ('visit','Düzce İl Müdürlüğünün işletmede inceleme bildirimi',None,'ziyaret ederek teslim edilen hayvanları yerinde inceledi.'),
     ]),
    ('yozgat.html','yozgat','24 Eylül Yozgat İl Müdürlüğü küçükbaş proje bildirimi','2026-09-24','2026-09-24','Yozgat İl Tarım ve Orman Müdürlüğü','official',
     'https://yozgat.tarimorman.gov.tr/Haber/829/Kirsalda-Bereket-Kucukbasa-Destek-Destek-Projesi-Kapsaminda-Hak-Sahiplerine-Hayvanlari-Dagitilmaya-Devam-Ediyor',
     '5424faeed2487e3ff1a0ea04be899405a06d448758d39b5c05771ce47dceb38d', [
         ('day','Yozgat İl Müdürlüğü bildiriminin yayım tarihi',None,'24.09.2026'),
         ('applications','Yozgat başvuru sayısı',None,'2.381'),
         ('roster','Yozgat ilk etap asil ve yedek ayrımı',None,"14'ü</strong> asil ve <strong>42</strong>'si yedek"),
         ('reported','Yozgat 24 Eylül yayımına kadar bildirilen teslimlerin ilçeleri',None,'Çandır İlçemizden 2, Boğazlıyan ilçemizden 1, Sorgun ilçemizden 1 son olarak da Merkez ilçemizden 1'),
     ]),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0412-kucukbas-'+key
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
    add('source_attribution',version_id=vid,publisher=publisher,author='Gültekin Uysal' if kind == 'party' else None,kind='official' if kind=='official' else 'party_publication',
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
        assert exact in text,(key,suffix)
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,
            article=None,section=section,pdf_page_index=index,printed_page=None)
(checks/'kucukbas-v2-source-records.json').write_text(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'kucukbas-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
