"""Capture Diyarbakır's 2015 municipal transport sources and later reports."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

checks,stage=map(Path,sys.argv[1:])
root=Path('data/practices/sources/dbp')
now=datetime.now(timezone.utc).isoformat()
entries,paths=[],set()


def add(table,**row):
    entries.append(dict(kind=table,values=row))


def save(relative,content):
    path=root/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes()==content
    else:
        path.write_bytes(content)
    paths.add(path)


assets=(
    ('diyarbakir-20150506.html','may06','6 Mayıs 2015 doğalgaz dolum tesisi haberi','2015-05-06','day',
     'https://www.sondakika.com/yerel/haber-otobus-dogalgaz-dolum-tesisi-temel-atma-toreni-7278922/',
     'af86be98f85c6ab94aa2c10464c397650613c474ee3c593d3e57693e00198ee6','news','Son Dakika','Anadolu Ajansı',[
         ('role','Gültan Kışanak’ın belediye başkanı sıfatı',None,None,"Büyükşehir Belediye\xa0Başkanı <a class='keyword-sd' href='/gultan-kisanak/' title='Gültan Kışanak'>Gültan Kışanak</a>"),
         ('goal','Toplu taşımada temiz enerjiye geçiş açıklaması',None,None,'belediye olarak temiz enerjiye geçme kararı aldıklarını söyledi.'),
         ('plan','Kışanak’ın açıkladığı ilk hizmet takvimi',None,None,
          "22 Mayıs'tan itibaren şehir içi ulaşımda hizmet vermeye başlayacağını sözlerine ekledi."),
         ('agency','Yayın künyesinde Anadolu Ajansı',None,None,'Kaynak:&nbsp;AA'),
     ]),
    ('diyarbakir-20150527.html','may27','27 Mayıs 2015 Diyarbakır doğalgazlı otobüs tanıtımı','2015-05-27','day',
     'https://www.sondakika.com/guncel/haber-dogalgazla-calisan-otobusler-sefere-basladi-7355342/',
     'b2459648425660265086317d2e8d502ced066b854548f0882507db5815fded23','news','Son Dakika','Temsilci',[
         ('launch','Tanıtımda ilk 22 araç',None,None,
          "48 adet doğalgazla çalışan otobüsün 22'si bugün düzenlenen tanıtım toplantıyla halkın hizmetine sunuldu."),
         ('tour','Tanıtım için şehir turu',None,None,'Şehir Turu Yapılarak Araçlar Halka Tanıtıldı'),
         ('later','Düzenli hizmet için sonraki gün başlığı',None,None,'Yarın Sefere Başlıyorlar'),
         ('simsek-role','DBP İl Eş Başkanı Ali Şimşek',None,None,'DBP İl Eş Başkanı Ali Şimşek'),
         ('simsek-words','Şimşek’in belediyeye teşekkür etmesi',None,None,
          'Şimşek, yapılan değerli çalışmadan dolayı belediyeye teşekkür etti'),
     ]),
    ('dbp-yerel-rapor.pdf','dbp-report','DBP yerel yönetim ve kayyum raporu',None,'unknown',
     'https://www.hdp.org.tr/Images/UserFiles/Documents/Editor/DBP%20Kayyum%20Raporu.pdf',
     '0a66bab03b3da563152c3fc964b5a3d725173505733606a36e50cd465be8dd91','party','Demokratik Bölgeler Partisi',None,[
         ('author','İç başlıkta Demokratik Bölgeler Partisi',2,'1','DEMOKRATİK BÖLGELER PARTİSİ'),
         ('claimed-route','Partinin belediye ulaşımı hakkında geriye dönük açıklaması',22,'21',
          'çevreye duyarlı doğalgazlı toplu taşıma araçları alınmıştır.'),
     ]),
    ('diyarbakir-2016.pdf','city-report','Diyarbakır Büyükşehir Belediyesi 2016 faaliyet raporu',None,'unknown',
     'https://www.diyarbakir.bel.tr/uploads/2016_yili_faaliyet_raporu_0cabdb7e76.pdf',
     '87ee8b89d691e979f14212653a21b5eef83f0e2d6cc622827b2f69adc96201cd','official','Diyarbakır Büyükşehir Belediyesi',None,[
         ('cover','Kapakta Nisan 2017',0,None,'NİSAN 2017'),
         ('annual','2016 raporunda belediye araçları',92,'92','doğalgazlı otobüs alındı,'),
         ('station','2016 raporunda doğalgaz dolum istasyonu',93,'93','istasyonu kurduk.'),
     ]),
)
for name,key,title,date,precision,url,h,source_kind,publisher,author,anchors in assets:
    path=stage/name
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==h
    is_pdf=name.endswith('.pdf')
    doc='0409-diyarbakir-cng-'+key
    vid=doc+'-v1'
    original=f'objects/{h}/'+('original.pdf' if is_pdf else 'original.html.bin')
    readable=f'objects/{h}/readable.html'
    save(original,raw)
    save(readable,readable_bytes(raw,'pdf' if is_pdf else 'html',legacy=False))
    add('document',id=doc,party_id='dbp',title=title,source_kind=source_kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,
        date_precision=precision,date_unknown_reason=None if date else ('Kapakta Nisan 2017 yazıyor. Gün ve ilk çevrim içi yayın tarihi açık.'
                                                 if key=='city-report' else 'PDF’nin çevrim içi ilk yayın tarihi açık.'),
        version_label='Erişilen özgün nüsha.',
        accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='application/pdf' if is_pdf else 'text/html',sha256=h,
        original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author=author,
        kind={'news':'journalism','party':'party_publication','official':'official'}[source_kind],
        published_at=date if source_kind=='news' else None,date_precision='day' if source_kind=='news' else 'unknown',
        social_handle=None,public_url=url,basis='Yayın künyesi veya rapor kapağı ve atfın bağlamı okundu.')
    if not is_pdf:
        view=build_view(raw,url,root,fetch_assets=False)
        view['version_id']=vid
        validate_view(root,view)
        manifest=root/view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent/f for f in json.loads(manifest.read_bytes())['files'])
        add('archive_view',**view)
    for suffix,section,page,printed,exact in anchors:
        text=pdf_page_text(root/original,page) if is_pdf else html_source_text(raw)
        assert exact in text,(key,suffix)
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,
            article=None,section=section,pdf_page_index=page,printed_page=printed)
(checks/'diyarbakir-cng-source-records.json').write_text(json.dumps(dict(party_id='dbp',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'cng-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
