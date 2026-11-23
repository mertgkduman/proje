"""Archive the Şiran Tekstilkent campaign account and municipal action notice."""

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
    ('siran-tekstil-taka.body','taka','Abdulbaki Kara’nın adaylık projeleri, Taka Gazete','2024-02-29','2024-02-29','Taka Gazete','news',
     'https://www.takagazete.com.tr/siran-demokrat-parti-belediye-baskan-adayi-abdulbaki-kara-projelerini-taka-gazetesine-anlatti',
     '15e3058834fe3de80a61849b48badf50d663da6f2c17bbfc6445080ac50e6a95',[
         ('role','Demokrat Parti Şiran belediye başkan adayı',None,'Şiran Demokrat Parti Belediye Başkan Adayı Abdulbaki Kara'),
         ('goal','Tekstil Kent, üç aşamalı proje ve 500 kişilik hedef',None,'500 kişiyi istihdam edecek bir kapasite ile Şiran’da Tekstil Kent Projesini hayata geçireceklerini belirten Abdulbaki Kara'),
         ('first','İlk geçici saha ve yaklaşık 120 kişilik hedef',None,'İlk aşamada geçici bir yer ve yaklaşık 120 kişilik bir istihdam ile projeyi başlatacaklarını'),
         ('quote','Adaydan aktarılan işsizlik hedefi',None,'işsizliği çözeceğiz'),
         ('byline','Yayında Doğukan Özkurt atfı',None,'<meta name="author" content="DOĞUKAN ÖZKURT">'),
     ]),
    ('siran-tekstil-municipal.body','municipal','Şiran Belediyesi Tekstilkent yer incelemesi duyurusu','2024-05-18','2024-05-18','Şiran Belediyesi','official',
     'https://www.siran.bel.tr/haberler/tekstilkent-projemiz-icin-yatirimcilarimiz-ile-bir-araya-geldik',
     '954270fd4b0a15f1f3eded61d7a9ed2682b5fbbf3d431b5d1aca71b7cab205ac',[
         ('date','Belediye duyurusu tarihi',None,'<span class="text">18 Mayıs 2024</span>'),
         ('site','Yatırımcılarla yer incelemesi',None,'Tekstilkent projemiz için yatırımcılarımız ile bir araya gelerek yer incelemesi yaptık.'),
         ('plan','Duyurudaki ileriye dönük istihdam beklentisi',None,'süreci tamamlayıp Şiran\'da istihdam hamlesini başlatacağız.'),
     ]),
    ('siran-handover.body','handover','Şiran Belediyesi 3 Nisan 2024 devir teslim haberi','2024-04-03','2024-04-03','Şiran Belediyesi','official',
     'https://www.siran.bel.tr/haberler/belediye-baskanimiz-sayin-abdulbaki-kara-goreve-basladi',
     'fc80d5c8bbc60da52ae2fcaf3c0058eb20b87c464bb3177e70e3853143fad84d',[
         ('date','Devir teslim haberi günü',None,'<span class="text">3 Nisan 2024</span>'),
         ('role','Mazbata ve belediye başkanlığı devir teslimi',None,'Bugün mazbatasını devralarak ilçe halkımız tarafından Şiran Belediye Başkanlığı görevine seçilen Belediye Başkanımız Sayın Abdulbaki KARA'),
     ]),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0412-tekstil-'+key
    vid=doc+'-v1'
    obj=f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable=f'objects/{digest}/readable.html'
    store(obj,raw)
    store(readable,readable_bytes(raw,'pdf' if pdf else 'html',legacy=False))
    add('document',id=doc,party_id='demokrat',title=title,source_kind=kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,
        date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Dinamik kayıt ilk yayın gününü belirtmiyor.',
        version_label='Özgün belediye ve gazetecilik kaynağı.',accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='application/pdf' if pdf else 'text/html',sha256=digest,original_path=obj,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author='Doğukan Özkurt' if key=='taka' else None,kind='official' if kind=='official' else 'journalism',
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
(checks/'siran-tekstil-source-records.json').write_text(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'textile-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
