"""Archive the original shelter field report and election records."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path,sys.argv[1:])
root = Path('data/practices/sources/dbp')
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
    ('ihd.pdf','ihd','Diyarbakır ilinde sığınma evleri görüşme ve tespit raporu','2016-03-10','2016-03-10',
     'İnsan Hakları Derneği Diyarbakır Şubesi','independent_report',
     'https://ihddiyarbakir.org/Content/uploads/7c6a3ffc-c949-483c-a11c-8f1199f924a2.pdf',
     '82a00a3657bb1e84449a9978ffea9b94ddd8e2014098ef75d15ec5564c4f9712',[
       ('credit','Kapağın yayıncı ve yazar bilgisi',0,'İHD DİYARBAKIR ŞUBESİ KADIN KOMİSYONU'),
       ('decision','Araştırma kararının 12 Ocak 2015 tarihi',1,'Kurulumuzun 12.01.2015 tarihli kararı'),
       ('institutions','Diyarbakır Büyükşehir ve Bağlar birimlerine erişim',1,
        'Diyarbakır Büyükşehir Belediyesi Kadın ve Sosyal Politikalar Daire Başkanlığı ile\nBağlar Belediyesi Kardelen Kadın Merkezine'),
       ('sample','Görüşme örneklemi ve onam',1,'17 kadın ile aydınlatılmış onamları doğrultusunda birebir\ngörüşmeler yapılmıştır.'),
       ('support','Görüşmecilerin barınma ve sağlık desteği anlatımı',2,
        'barınma, ısınma, kişisel bakım, temizlik ve sağlık ihtiyaçlarının\nyeterince karşılandığı ifade edilmiştir.'),
       ('gap','Görüşmecilerin hukuki bilgilendirmeye ilişkin yanıtları',2,
        'sığınaklarda ne kadar kalabileceklerine dair bilgilendirmenin yeterince\nyapılmadığı anlaşılmıştır.'),
       ('recommendations','Görüşme bulgularından ayrı öneri bölümü',3,'TESPİT VE ÖNERİLER'),
       ('followup','Çıkış sonrası takip için yetkili atfı',4,'yetkililerden\naldığımız bilgiye göre:'),
     ]),
    ('index.html','index','İHD Diyarbakır raporlar dizini',None,None,
     'İnsan Hakları Derneği Diyarbakır Şubesi','independent_report','https://ihddiyarbakir.org/tr/raporlar?s=8',
     '3eba620ffa9b80dbc59821144c4747794b99ec08bba192127b0b8cfac64bfdc8',[
       ('date','Raporun yayın dizininde gösterilen 10 Mart 2016 tarihi',None,'<div class="date">10 Mart 2016</div>'),
       ('link','Aynı dizin kaydının özgün rapor bağlantısı',None,
        'href="https://ihddiyarbakir.org/Content/uploads/7c6a3ffc-c949-483c-a11c-8f1199f924a2.pdf"'),
     ]),
    ('Buyuksehir-KazananAdaylar.pdf','ysk-big','2014 büyükşehir belediye başkanlığı seçim sonuçları','2014-03-30',None,
     'Yüksek Seçim Kurulu','official',
     'https://ysk.gov.tr/doc/dosyalar/docs/2014MahalliIdareler/Buyuksehir-KazananAdaylar.pdf',
     '02bceff3d52407258d6e65a80ba8c02d571e8752e65bda4c3543bde5d18e8a8a',[
       ('name','Diyarbakır satırı, Gültan Kışanak; satır görseli ve soyadı sütunu',0,'KIŞANAK'),
       ('party','Diyarbakır satırı, parti sütunu',0,'BARIŞ VE DEMOKRASİ PARTİSİ'),
     ]),
    ('BelediyeBsk-KazananAdaylar.pdf','ysk-district','2014 ilçe belediye başkanlığı seçim sonuçları','2014-03-30',None,
     'Yüksek Seçim Kurulu','official',
     'https://ysk.gov.tr/doc/dosyalar/docs/2014MahalliIdareler/BelediyeBsk-KazananAdaylar.pdf',
     '4ec89785bff1f66834a602c22e4a0ab2f8d36658099f815c549015c2ab2c6c25',[
       ('name','Bağlar satırı, Birsen Kaya Akat; satır görseli ve soyadı sütunu',5,'KAYA AKAT'),
       ('party','Bağlar satırı, parti sütunu',5,'BARIŞ VE DEMOKRASİ PARTİSİ'),
     ]),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0409-siginak-'+key
    vid=doc+'-v1'
    obj=f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable=f'objects/{digest}/readable.html'
    store(obj,raw)
    store(readable,readable_bytes(raw,'pdf' if pdf else 'html',legacy=False))
    add('document',id=doc,party_id='dbp',title=title,source_kind=kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,
        date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Dinamik kayıt ilk yayın gününü belirtmiyor.',
        version_label='Özgün kurum veya parti nüshası.',accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='application/pdf' if pdf else 'text/html',sha256=digest,original_path=obj,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author='İHD Diyarbakır Şubesi Kadın Komisyonu' if key=='ihd' else None,
        kind='official' if kind=='official' else 'other',
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
existing = root/'objects'/'0a66bab03b3da563152c3fc964b5a3d725173505733606a36e50cd465be8dd91'/'original.pdf'
passage = 'Bağlar Belediyesi ve Akdeniz Belediyesi bünyesinde ‘kadın sığınma evleri’'
assert passage in pdf_page_text(existing,28)
add('passage',id='0409-siginak-dbp-report-shelters',version_id='0409-diyarbakir-cng-dbp-report-v1',
    exact=passage,prefix=None,suffix=None,article=None,section='4.5 Kadın Politikaları, DBP’nin 2017 tarihli sığınak anlatımı',
    pdf_page_index=28,printed_page='27')
(checks/'siginak-source-records.json').write_text(json.dumps(dict(party_id='dbp',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'siginak-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
