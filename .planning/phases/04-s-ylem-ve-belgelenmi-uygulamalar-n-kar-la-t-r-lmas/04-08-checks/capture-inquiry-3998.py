"""Archive the Saadet pension proposal and the separate adopted law."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/yeni-yol')
now = datetime.now(timezone.utc).isoformat()
entries = []
paths = set()
sources = [
    ('yy-3998','html','https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/5f4ebd17-60ec-4431-83d8-019d96b0d808',
     '10/3998 TÜİK araştırma önergesi TBMM kaydı',None,None,[
        ('id','10/3998 esas numarası','10 / 3998',None),
        ('filed','TBMM Başkanlığına geliş tarihi','<td>08/04/2026</td>',None),
        ('status','Erişilen dosya durumu','<td>G&#xFC;ndemde</td>',None),
     ]),
    ('yy-3998-signed','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T10/WebOnergeMetni/b624a732-6fc2-455b-8b77-e6deb4f9e88a.pdf',
     'Selçuk Özdağ ve 19 milletvekilinin 10/3998 imzalı önergesi','2026-04-08',None,[
        ('id','TBMM belge kimliğinin ilk sayfası','10/3998',0),
        ('terms','Araştırma gerekçesinde sepet açıklaması','TÜİK’in enflasyon sepetini açıklamama pratiğinin hukuki ve anayasal dayanaklarının,',1),
        ('commission','Gerekçedeki araştırma komisyonu talebi','Araştırma Komisyonu kurulmasını arz ve teklif ederiz.',1),
        ('signer','Üçüncü sayfa imza tablosunda Selçuk Özdağ','SELÇUK ÖZDAĞ',2),
     ]),
    ('yy-3998-february','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/55/Tam/f9f62b1e-6286-4d85-942a-59e83b756739.html',
     '3 Şubat 2026 55. Birleşimde Yeni Yol Grubu adına TÜİK araştırma çağrısı','2026-02-03',None,[
        ('role','Tutanakta Yeni Yol Grubu adına Özdağ','YENİ YOL GRUBU ADINA SELÇUK ÖZDAĞ (Muğla)',None),
        ('quote','TÜİK sepetinin araştırılmasına ilişkin kısa birebir ifade',"Gelin, hep beraber bir araştırma önergesi verelim, TÜİK'in bu enflasyon sepetini niçin açıklamadığını",None),
     ]),
    ('yy-3998-session','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/79/Tam/95653b0a-b778-4b4f-8107-4b20c9756996.html',
     '8 Nisan 2026 79. Birleşimde Yeni Yol TÜİK gündem önerisi ve oy','2026-04-08',None,[
        ('role','Tutanakta Yeni Yol Grubu adına Selçuk Özdağ','YENİ YOL GRUBU ADINA SELÇUK ÖZDAĞ (Muğla)',None),
        ('motion','İçtüzük 19 kapsamındaki gündeme alma önerisi','8/4/2026 Çarşamba günkü birleşimde yapılması önerilmiştir.',None),
        ('support','Özdağ’ın grup konuşmasında araştırma isteği','Gelin, bu enflasyon sepetini araştıralım.',None),
        ('debate','İşaretle oylamaya ilişkin Koçyiğit açıklaması','muhalefetin önergesi kabul edilmiş görünüyor.',None),
        ('dalgin-role','İYİ Parti Grubu adına Burak Dalgın','İYİ PARTİ GRUBU ADINA BURAK DALGIN (Balıkesir)',None),
        ('dalgin-call','Dalgın’ın fiyat ve ürün sepeti çağrısı','Fiyat ve ürün sepetinizi açıklayın',None),
        ('kamaç-role','DEM Parti Grubu adına Mehmet Kamaç','DEM PARTİ GRUBU ADINA MEHMET KAMAÇ (Diyarbakır)',None),
     ]),
    ('yy-3998-summary','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/79/Ozet/df9c8bda-488f-49a4-8cd1-414963704c20.html',
     'TBMM 79. Birleşim gündem oylamalarının işlem özeti','2026-04-08',None,[
        ('motion','Yeni Yol grubunun TÜİK araştırma önerisi','Muğla Milletvekili Selçuk Özdağ ve 19 milletvekili tarafından, TÜİK’in açıkladığı enflasyon verilerinin hesaplanma yöntemi',None),
        ('result','Aynı gün görüşme önerilerinin işlemi','Görüşmelerinin Genel Kurulun 8 Nisan 2026 Çarşamba günkü birleşiminde yapılmasına ilişkin önerileri yapılan görüşmelerden sonra kabul edilmedi.',None),
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
    raw=fetched.read_bytes()
    digest = sha256(raw).hexdigest()
    doc = f'0408-stats-{key}'
    vid = doc+'-v1'
    original = f'objects/{digest}/original.'+('pdf' if ext=='pdf' else 'html.bin')
    readable = f'objects/{digest}/readable.html'
    put(original, raw)
    put(readable,readable_bytes(raw,ext,legacy=False))
    captured=datetime.fromtimestamp(fetched.stat().st_mtime,timezone.utc).isoformat()
    add('document',id=doc,party_id='yeni-yol',title=title,source_kind='official')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,
        date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'TBMM kayıt sayfasının ilk yayımlandığı gün açık değil. Teklifin geliş, sevk ve kabul tarihleri ayrı görünen pasajlarda.',version_label='Erişilen özgün kaynak kaydı.',
        accessed_at=captured,verified_at=now,mime='text/html' if ext=='html' else 'application/pdf',
        sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',
        published_at=published,date_precision='day' if published else 'unknown',social_handle=None,
        public_url=url,basis='Yayıncı ve künye, özgün sayfada görülen bilgiyle kaydedildi.')
    if ext=='html':
        view=build_view(raw,url,root,fetch_assets=False)
        view['version_id']=vid
        validate_view(root,view)
        add('archive_view',**view)
        manifest=root/view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
        body=html_source_text(raw)
        if key == 'yy-3998-session':
            left = body.index('Elektronik cihazla oylama yapacağım.')
            result = 'BAŞKAN - Öneri kabul edilmemiştir.'
            right = body.index(result,left)+len(result)
            passages.append(('decision','Elektronik oylama ve hemen izleyen başkan ilanı',body[left:right],None))
    else:
        assert [pdf_page_text(root/original,n).strip() for n in range(3)]==['10/3998','','']
    for suffix, section, exact, page in passages:
        if page is None:
            assert exact in body,(key,suffix,repr(exact))
        pid=doc+'-'+suffix
        add('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=page,printed_page=None)
        if page is not None and page > 0:
            add('manual_passage',passage_id=pid,checked_at=now,
                method='Özgün PDF Poppler ile sayfa bazında görüntülendi.',
                reason='İkinci ve üçüncü tarama sayfasının metin katmanı boş. Pasaj ve bağlam gözle okundu.')
out=checks/'inquiry-3998-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps({'party_id':'demokrat','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0408-inquiry-3998-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(sha256(out.read_bytes()).hexdigest(),len(entries),len(paths))
