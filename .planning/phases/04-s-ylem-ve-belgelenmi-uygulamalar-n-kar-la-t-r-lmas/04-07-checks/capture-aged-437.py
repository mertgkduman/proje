"""Archive the Saadet pension proposal and the separate adopted law."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/iyi')
now = datetime.now(timezone.utc).isoformat()
entries = []
paths = set()
sources = [
    ('iyi-437','html','https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/1de74186-02dd-4030-a545-018b3d649158',
     '10/437 yaşlıların sosyal ve ekonomik sorunları araştırma önergesi','2023-10-12',None,[
        ('id','10/437 esas numarası','10 / 437',None),
        ('submitted','Önergenin Başkanlığa geliş tarihi','12/10/2023',None),
        ('first','İlk imza kaydı','Manisa Milletvekili &#x15E;enol Sunat ve 19 Milletvekili',None),
        ('status','Erişim anındaki dosya durumu','G&#xFC;ndemde',None),
    ]),
    ('iyi-437','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y2/T10/WebOnergeMetni/21c93b44-ef81-4790-9a6e-b2350fafc1d7.pdf',
     '10/437 imzalı önerge ve gerekçesi','2023-10-12',None,[
        ('id','Önerge kapağındaki 10/437 esas numarası','10/437',0),
        ('quote','Gerekçede huzurevlerinin incelenmesi talebi','Bu kapsamda öncelikli olarak huzurevleri incelenmelidir.',1),
        ('condition','Gerekçedeki huzurevleri hizmet ve standartları hedefi',
         'huzurevlerinin standartlarını yükseltmeyi ve yaşlı vatandaşlarımızın daha iyi hizmet',2),
    ]),
    ('pension-2024-session','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/2/50/Tam/8eacee7b-6d28-4728-ae25-74885298f608.html',
     '17 Ocak 2024 TBMM 50. Birleşim tam tutanağı','2024-01-17',None,[
        ('proposal','Gündeme alınması istenen Ekim 2023 önerisi',
         'Manisa Milletvekili Şenol Sunat ve 19 milletvekili tarafından yaşlı vatandaşların karşılaştığı sosyal ve ekonomik sorunların araştırılarak bu sorunlara yönelik yapıcı çözüm önerileri geliştirilmesi amacıyla 12/10/2023 tarihinde',None),
        ('sunat','Gündeme alma önerisini savunan Şenol Sunat’ın grup yetkisi','İYİ PARTİ GRUBU ADINA ŞENOL SUNAT (Manisa)',None),
        ('sunat-statement','Sunat’ın grup adına araştırma önerisini savunduğu cümle',
         'İYİ Parti Grubu adına yaşlı vatandaşlarımızın mağduriyetlerinin giderilmesi amacıyla sunduğumuz araştırma önergemiz üzerine söz aldım.',None),
        ('dem-role','Adalet Kaya’nın DEM Parti Grubu adına konuştuğu başlık','DEM PARTİ GRUBU ADINA ADALET KAYA (Diyarbakır)',None),
        ('dem-support','DEM Parti Grubu adına yapılan sözlü destek açıklaması',
         'Bu sebeple, yaşlı bakımevlerinde hizmetin iyileştirilmesine yönelik bu önergeyi DEM PARTİ olarak destekliyoruz.',None),
    ]),
    ('pension-2024-summary','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/2/50/Ozet/daf93bf0-106b-4149-93f4-b97383f560c0.html',
     '17 Ocak 2024 TBMM 50. Birleşim işlem özeti','2024-01-17',None,[
        ('topic','İYİ Parti’nin gündeme alma önerisinin birleşim özetindeki satırı',
         'İYİ Parti Grubunun, 12/10/2023 tarihinde Manisa Milletvekili Şenol Sunat ve 19 milletvekili tarafından',None),
        ('result','Gündeme alma önerilerinin TBMM birleşim özetindeki sonucu',
         'Görüşmelerinin Genel Kurulun 17 Ocak 2024 Çarşamba günkü birleşiminde yapılmasına ilişkin önerileri yapılan görüşmelerden sonra kabul edilmedi.',None),
    ]),
]

def add(table, **row):
    entries.append({'kind':table, 'values':row})

def put(rel, body):
    path = root/rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes()==body
    else:
        path.write_bytes(body)
    paths.add(path)

for key, ext, url, title, day, published, passages in sources:
    fetched = stage/f'{key}.{ext}'
    raw = fetched.read_bytes()
    digest = sha256(raw).hexdigest()
    doc = f'0407-aged-{key}' + ('-signed' if ext=='pdf' else '')
    vid = doc+'-v1'
    original = f'objects/{digest}/original.'+('pdf' if ext=='pdf' else 'html.bin')
    readable = f'objects/{digest}/readable.html'
    put(original, raw)
    put(readable, readable_bytes(raw,ext,legacy=False))
    captured = datetime.fromtimestamp(fetched.stat().st_mtime, timezone.utc).isoformat()
    add('document',id=doc,party_id='iyi',title=title,source_kind='official')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,
        date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'TBMM kayıt sayfasının ilk yayımlandığı gün açık değil. Teklifin geliş, sevk ve kabul tarihleri ayrı görünen pasajlarda.',version_label='TBMM’nin erişilen özgün kaydı.',
        accessed_at=captured,verified_at=now,mime='text/html' if ext=='html' else 'application/pdf',
        sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',
        published_at=published,date_precision='day' if published else 'unknown',social_handle=None,
        public_url=url,basis='TBMM künye ve tarih bilgileri, belge veya yasama işlemi gününden ayrı değerlendirildi.')
    if ext=='html':
        view=build_view(raw,url,root,fetch_assets=False)
        view['version_id']=vid
        validate_view(root,view)
        add('archive_view',**view)
        manifest=root/view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
        body=html_source_text(raw)
    else:
        assert [pdf_page_text(root/original,n).strip() for n in range(4)]==['10/437','','','']
    for suffix, section, exact, page in passages:
        if page is None:
            assert exact in body,(key,suffix,repr(exact))
        pid=doc+'-'+suffix
        add('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=page,printed_page=None)
        if page is not None and page>0:
            add('manual_passage',passage_id=pid,checked_at=now,
                method='Özgün PDF Poppler ile sayfa bazında görüntülendi.',
                reason='Gerekçe sayfasının metin katmanı boş. Pasaj ve bağlam gözle okundu.')
out=checks/'aged-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps({'party_id':'iyi','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0407-aged-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(sha256(out.read_bytes()).hexdigest(),len(entries),len(paths))
