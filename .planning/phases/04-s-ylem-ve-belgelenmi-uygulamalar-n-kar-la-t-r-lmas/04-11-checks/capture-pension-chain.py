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
    ('arikan-3456','html','https://tbmm.gov.tr/Yasama/KanunTeklifi/f8c3247e-5f23-4c8b-81b9-019b8e661f8b',
     '2/3456 en düşük emekli aylığı teklifinin TBMM kaydı',None,None,[
        ('id','2/3456 esas numarası','2 / 3456',None),
        ('submitted','Başkanlığa geliş günü','05/01/2026',None),
        ('referred','Esas ve tali komisyona giriş günü','06/01/2026',None),
        ('status','Sayfada erişim anında gösterilen komisyon durumu','Komisyonda',None),
        ('initial','İlk imza sahibi Mahmut Arıkan','Mahmut ARIKAN',None),
    ]),
    ('arikan-3456','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T2/WebOnergeMetni/3c8e1790-d377-470f-947b-96caf368b9bf.pdf',
     '2/3456 Mahmut Arıkan imzalı teklif PDF’si','2026-01-05',None,[
        ('signature','İlk sayfadaki imza sahibi ve iki sıfatı','Mahmut ARIKAN\nSaadet Partisi Genel Başkanı\nKayseri Milletvekili',0),
        ('filed','İmza üst yazısının tarihi','Gereğini saygılarımla arz ederim. 05.01.2026',0),
        ('article','1. maddenin önerdiği alt aylık ölçütü','“16.881 Türk lirasından” ibaresi “asgari ücretten” şeklinde değiştirilmiştir.',5),
    ]),
    ('pension-group','html','https://tbmm.gov.tr/Haber/Detay?Id=5d542213-31fe-4e28-b4f2-019be02b88e5',
     'TBMM 21 Ocak Yeni Yol grup toplantısı ve Saadet Genel Başkanı açıklaması','2026-01-21','2026-01-21',[
        ('role','TBMM haberinde konuşmacının Saadet sıfatı','Toplantıda konuşan Saadet Partisi Genel Başkanı Mahmut Arıkan',None),
        ('quote','Arıkan’ın emekli aylığının alt sınırı önerisi','Bizim teklifimiz net, en düşük emekli aylığı en azından asgari ücret seviyesine yükseltilmelidir.',None),
        ('graduated','Ayrı kademeli prim önerisi','prim ödemelerine göre kademeli bir oranlama ile tüm emeklilerin maaşları artırılmalıdır.',None),
        ('objection','20.000 TL’lik teklife ilişkin itiraz','teklifin 20 bin lira olmasını kabul etmediklerini kaydederek',None),
    ]),
    ('pension-bill-23464','html','https://tbmm.gov.tr/Yasama/KanunTeklifi/eeaf5693-28b4-4c9a-8197-019ba20e2a59',
     '2/3464 ve 248 sıra sayılı teklifin TBMM kaydı',None,None,[
        ('id','2/3464 esas numarası','2 / 3464',None),
        ('law','2/3464’ten kanun kaydına bağlantı','>7573</a>',None),
    ]),
    ('pension-law-7573','html','https://tbmm.gov.tr/Yasama/Kanun/EEAF5693-28B4-4C9A-8197-019BA20E2A59',
     '7573 sayılı kanunun kabul ve yayım kaydı','2026-01-23',None,[
        ('accept','7573 sayılı kanunun TBMM kabul tarihi','<td><b>Kabul Tarihi</b></td>\n                                <td>23/01/2026</td>',None),
        ('gazette','Resmî Gazete günü ve sayısı','<td><b>Resmi Gazete Numarası</b></td>\n                                <td> 33152</td>',None),
    ]),
    ('pension-text-7573','html','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/KanunMetni/bdf52380-b42e-40d5-b616-97b8bdbeaccd.htm',
     '7573 sayılı kanunun TBMM’deki tam metni','2026-01-23','2026-01-29',[
        ('article','7. madde, 16.881 TL yerine 20.000 TL','“16.881” ibaresi “20.000” şeklinde değiştirilmiştir.',None),
        ('effect','Ocak 2026 ödeme döneminden itibaren uygulama ibaresi','nci maddesi 2026 yılı Ocak ayı ödeme döneminden itibaren uygulanmak üzere\r\nyayımı tarihinde,',None),
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
    doc = f'0411-pension-{key}' + ('-signed' if ext=='pdf' else '')
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
    else:
        assert [pdf_page_text(root/original,n).strip() for n in range(6)]==['']*6
    for suffix, section, exact, page in passages:
        if page is None:
            assert exact in body,(key,suffix,repr(exact))
        pid=doc+'-'+suffix
        add('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=page,printed_page=None)
        if page is not None:
            add('manual_passage',passage_id=pid,checked_at=now,
                method='Özgün PDF Poppler ile sayfa bazında görüntülendi.',
                reason='Altı tarama sayfasının metin katmanı boş. Pasaj ve bağlam gözle okundu.')
out=checks/'pension-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps({'party_id':'saadet','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0411-pension-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(sha256(out.read_bytes()).hexdigest(),len(entries),len(paths))
