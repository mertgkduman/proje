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
    ('arikan-1998','html','https://tbmm.gov.tr/Yasama/KanunTeklifi/750f7596-5e40-412b-8a1b-018d837edf79',
     '2/1998 yaşlılık aylığına hak kazanma teklifinin TBMM kaydı',None,None,[
        ('id','2/1998 esas numarası','2 / 1998',None),
        ('submitted','Başkanlığa geliş günü','07/02/2024',None),
        ('referred','Esas ve tali komisyona giriş günü','08/02/2024',None),
        ('status','Sayfada erişim anında gösterilen komisyon durumu','Komisyonda',None),
        ('initial','İlk imza sahibi Mahmut Arıkan','Mahmut ARIKAN',None),
    ]),
    ('arikan-1998','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y2/T2/WebOnergeMetni/ca45758d-e480-49a0-b58c-d5452027f482.pdf',
     '2/1998 Mahmut Arıkan imzalı teklif PDF’si','2024-01-30',None,[
        ('signature','İmzalı üst yazı günü ve başvuru','Gereğini arz ederim. 30.01.2024',0),
        ('receipt','İkinci tarama sayfasındaki TBMM alım damgasının kurum adı','KANUNLAR ve KARARLAR BSK.LIĞI',1),
        ('period','Madde 1’de sigortalılık döneminin başlangıç ve bitişi','8/9/1999 tarihinden 30/4/2008 tarihine kadar ilk defa sigortalı sayılanlar',4),
        ('age','Belli sigortalı gruplarındaki yaş ve prim koşulu','45 yaşını doldurmuş ve 9000 gün',4),
        ('partial','Kısmi yaşlılık aylığı için prim koşulu','en az 15 tam yıl malullük',4),
        ('coefficient','Madde 2’de güncelleme katsayısı değişikliği','Güncelleme katsayısı;',4),
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
    for suffix, section, exact, page in passages:
        if page is None:
            assert exact in body,(key,suffix,repr(exact))
        else:
            assert exact in pdf_page_text(root/original,page),(key,suffix,repr(exact))
        pid=doc+'-'+suffix
        add('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=page,printed_page=None)
out=checks/'pension-age-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps({'party_id':'saadet','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0411-pension-age-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(sha256(out.read_bytes()).hexdigest(),len(entries),len(paths))
