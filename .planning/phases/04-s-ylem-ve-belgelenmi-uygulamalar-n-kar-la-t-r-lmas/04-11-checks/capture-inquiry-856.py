"""Archive the Saadet pension proposal and the separate adopted law."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/saadet')
now = datetime.now(timezone.utc).isoformat()
entries = []
paths = set()
sources = [
    ('kaya-10856','html','https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/8aa24eb3-fe47-4946-b662-018d219264bc',
     '10/856 emeklilik sistemi araştırma önergesi kaydı',None,None,[
        ('id','10/856 esas numarası','10 / 856',None),
        ('submitted','Resmî Başkanlığa geliş günü','16/01/2024',None),
        ('owner','Önergenin TBMM kayıt özetindeki sahibi','<td>Saadet Partisi</td>',None),
        ('status','Erişimde görülen önerge dosyası durumu','G&#xFC;ndemde',None),
    ]),
    ('kaya-10856','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y2/T10/WebOnergeMetni/ad5a6926-9947-4498-90bd-d4637249958c.pdf',
     '10/856 imzalı grup önergesi ve gerekçesi',None,None,[
        ('id','Önergenin ilk sayfası, 10/856 ve el yazılı tarih alanı','10/856',0),
        ('quote','Gerekçenin son bölümünde araştırma ve değerlendirme amacı',
         'aksaklıkların araştırılması ve değerlendirmelerin yapılması önem arz etmektedir.',1),
    ]),
    ('pension-2024-session','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/2/50/Tam/8eacee7b-6d28-4728-ae25-74885298f608.html',
     '17 Ocak 2024 TBMM 50. Birleşim tam tutanağı','2024-01-17',None,[
        ('author','Saadet grubu önergesinin sahibi ve içeriğinin okunması',
         'Grup Başkan Vekili İstanbul Milletvekili Bülent Kaya tarafından, ülkedeki emekli maaşlarının yetersizliği',None),
        ('role','Saadet Partisi Grubu adına konuşmacı','SAADET PARTİSİ GRUBU ADINA MAHMUT ARIKAN (Kayseri)',None),
        ('scope','Arıkan’ın Saadet Partisi Grubu adına açıkladığı araştırma konuları',
         'Saadet Partisi Grubu olarak emekli maaşlarının yetersizliğini, aylık bağlama ve güncellemelerdeki farklılıkları konuşmak üzere Meclis araştırması önerisi verdik.',None),
        ('iyi-role','İYİ Parti Grubu adına Ömer Karakaş’ın konuşması','İYİ PARTİ GRUBU ADINA ÖMER KARAKAŞ (Aydın)',None),
        ('iyi-stance','Karakaş’ın alt aylık tutarına ilişkin ayrı teklifi',
         'Biz İYİ Parti olarak en düşük emekli maaşının asgari ücret kadar olmasını ve tüm emekli maaşlarında kademeli olarak artış yapılmasını istiyoruz.',None),
    ]),
    ('pension-2024-summary','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/2/50/Ozet/daf93bf0-106b-4149-93f4-b97383f560c0.html',
     '17 Ocak 2024 TBMM 50. Birleşim işlem özeti','2024-01-17',None,[
        ('saadet','10/856’ya ilişkin Saadet Grubu önerisinin 16 Ocak geliş bilgisi',
         'Saadet Partisi Grubunun, 16/1/2024 tarihinde Grup Başkan Vekili İstanbul Milletvekili Bülent Kaya tarafından',None),
        ('result','Gündeme alma önerilerinin birleşim özetindeki sonucu',
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
    doc = f'0411-inquiry-{key}' + ('-signed' if ext=='pdf' else '')
    vid = doc+'-v1'
    original = f'objects/{digest}/original.'+('pdf' if ext=='pdf' else 'html.bin')
    readable = f'objects/{digest}/readable.html'
    put(original, raw)
    put(readable, readable_bytes(raw,ext,legacy=False))
    captured = datetime.fromtimestamp(fetched.stat().st_mtime, timezone.utc).isoformat()
    add('document',id=doc,party_id='saadet',title=title,source_kind='official')
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
        if key=='pension-2024-session':
            after=body.index('SAADET PARTİSİ GRUBU ADINA MAHMUT ARIKAN (Kayseri)')
            result=body.index('Öneri kabul edilmemiştir.',after)
            following=body.index('İYİ Parti Grubunun İç Tüzük’ün 19’uncu maddesi',result)
            end=following+len('İYİ Parti Grubunun İç Tüzük’ün 19’uncu maddesi')
            passages.append(('saadet-result','Saadet gündem oylamasının sonucu ve sonraki gündem maddesi',body[result:end],None))
    else:
        assert [pdf_page_text(root/original,n).strip() for n in range(2)]==['10/856','']
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
out=checks/'inquiry-856-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps({'party_id':'saadet','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0411-inquiry-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(sha256(out.read_bytes()).hexdigest(),len(entries),len(paths))
