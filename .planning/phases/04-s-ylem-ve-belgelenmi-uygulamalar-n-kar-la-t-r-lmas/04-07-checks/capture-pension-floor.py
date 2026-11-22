"""Archive the Saadet pension proposal and the separate adopted law."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/iyi')
now = datetime.now(timezone.utc).isoformat()
entries = []
paths = set()
sources = [
    ('iyi-7573-49','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/49/Tam/a08098a8-d17e-4b50-8742-c596420d67a5.html',
     'TBMM 49. Birleşim 2/3464 görüşmeleri ve değişiklik önergesi','2026-01-21',None,[
        ('usta','Erhan Usta’nın İYİ Parti Grubu adına söz aldığını gösteren başlık','İYİ PARTİ GRUBU ADINA ERHAN USTA (Samsun)',None),
        ('quote','En düşük aylık için İYİ Parti politikasına ilişkin ifade','Bizim parti politikamız, asgari ücret düzeyinde olması',None),
        ('committee','Usta’nın komisyondaki 25.000 TL önergesine ilişkin beyanı',
         'daha makul bir rakam olsun "25 bin liraya çıkartalım." diye biz önerge verdik İYİ Parti Grubu olarak, önergemiz reddedilmişti.',None),
        ('amendment','7. maddeye ilişkin Genel Kurul 25.000 TL önergesi',
         '"20.000" ibaresinin "25.000" ibaresiyle değiştirilmesini arz ve teklif ederiz.',None),
        ('defense','Önerge üzerinde söz alan Yüksel Selçuk Türkoğlu',
         'Önerge üzerinde söz isteyen Bursa Milletvekili Sayın Yüksel Selçuk Türkoğlu.',None),
    ]),
    ('iyi-7573-50','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/50/Tam/334de34c-51a4-43d6-a3be-5d65bb5659a8.html',
     '22 Ocak’ta açılan 50. Birleşimin 23 Ocak kabul ve oylama tutanağı','2026-01-23',None,[
        ('accept','Başkanın kanunlaşmayı açıkladığı cümle','BAŞKAN - Teklif kabul edilmiş ve kanunlaşmıştır.',None),
        ('close','Kabulün açıklandığı oturumun kapanış saati','Kapanma Saati: 00.57',None),
    ]),
    ('pension-bill-23464','html','https://tbmm.gov.tr/Yasama/KanunTeklifi/eeaf5693-28b4-4c9a-8197-019ba20e2a59',
     '2/3464 esas ve 248 sıra sayılı teklifin TBMM kayıt sayfası',None,None,[
        ('id','2/3464 esas numarası','2 / 3464',None),
        ('law','Teklif kaydının 7573 sayılı kanun bağlantısı','>7573</a>',None),
    ]),
    ('pension-law-7573','html','https://tbmm.gov.tr/Yasama/Kanun/EEAF5693-28B4-4C9A-8197-019BA20E2A59',
     '7573 sayılı kanunun TBMM kabul kaydı','2026-01-23',None,[
        ('day','7573 sayılı kanunun kabul tarihi','<td>23/01/2026</td>',None),
        ('session','Kabul edildiği 50. Birleşim','28. Dönem 4. Yasama Yılı 50. Birleşim',None),
    ]),
    ('pension-text-7573','html','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/KanunMetni/bdf52380-b42e-40d5-b616-97b8bdbeaccd.htm',
     '7573 sayılı kanunun yayımlanan tam metni','2026-01-23','2026-01-29',[
        ('floor','7. madde, 16.881 TL yerine 20.000 TL','“16.881” ibaresi “20.000” şeklinde değiştirilmiştir.',None),
        ('effect','7. maddenin ödeme dönemi','nci maddesi 2026 yılı Ocak ayı ödeme döneminden itibaren uygulanmak üzere',None),
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
    doc = f'0407-floor-{key}' + ('-signed' if ext=='pdf' else '')
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
        if key=='iyi-7573-49':
            start=body.index('"25.000" ibaresiyle')
            rejection='Önergeyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Önerge kabul edilmemiştir.'
            finish=body.index(rejection,start)
            signers=body[start:finish]
            names=('Turhan Çömez','Ayyüce Türkeş Taş','Burhanettin Kocamaz','Hüsmen Kırkpınar','Lütfü Türkkan','Yüksel Selçuk Türkoğlu')
            assert all(name in signers for name in names)
            first=signers.index(names[0])
            last=signers.index(names[-1])+len(names[-1])
            passages.append(('signers','25.000 TL Genel Kurul önergesini imzalayan altı milletvekili',signers[first:last],None))
            passages.append(('rejection','25.000 TL önergesini izleyen oylama sonucu',rejection,None))
        if key=='iyi-7573-50':
            start=body.index('Kullanılan oy sayısı')
            end=body.index('Kâtip Üye',start)
            tally=body[start:end]
            assert all(text in tally for text in ('426','247','179'))
            passages.append(('tally','248 sıra sayılı teklif için tutanakta açıklanan oy toplamları',tally,None))
    for suffix, section, exact, page in passages:
        if page is None:
            assert exact in body,(key,suffix,repr(exact))
        pid=doc+'-'+suffix
        add('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=page,printed_page=None)
out=checks/'pension-floor-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps({'party_id':'iyi','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0407-pension-floor-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(sha256(out.read_bytes()).hexdigest(),len(entries),len(paths))
