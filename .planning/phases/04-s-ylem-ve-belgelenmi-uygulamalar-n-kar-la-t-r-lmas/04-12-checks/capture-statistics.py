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
root = Path('data/practices/sources/demokrat')
now = datetime.now(timezone.utc).isoformat()
entries = []
paths = set()
sources = [
    ('dp-4030','html','https://tbmm.gov.tr/Yasama/KanunTeklifi/186dbfa0-5ea5-42a3-9c8b-01a1b1325be2',
     '2/4030 Türkiye İstatistik Kanunu değişikliği teklif kaydı',None,None,[
        ('id','2/4030 esas numarası','2 / 4030',None),
        ('filed','Başkanlığa geliş günü','<td>06/11/2026</td>',None),
        ('commission','Plan ve Bütçe Komisyonu giriş günü','<td>10/11/2026</td>',None),
        ('status','Erişilen yasama kaydı, komisyon işlem sütunu','<td>Komisyonda</td>',None),
    ]),
    ('dp-4030-signed','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T2/WebOnergeMetni/c0b6d9a2-893e-48b2-9f7b-b414400a111d.pdf',
     'Haydar Altıntaş imzalı 2/4030 teklif ve gerekçesi','2026-11-06',None,[
        ('signature','Altıntaş’ın imza ve sıfatı','Haydar ALTINTAŞ',0),
        ('date','Üst yazı tarihi','Gereğini arz ederim. 06.11.2026',0),
        ('date-stamp','Geliş kaşesi','06 Kasım 2026',1),
        ('transparency','1. maddede veri yayımı yükümlülüğü','listesi, sepetteki ağırlık katsayıları, veri derleme yöntemleri ve kaynak türleri ile sepetteki her bir',5),
        ('publication','1. maddede elektronik açık veri biçimi','Başkanlığın resmî internet sitesinde herkesin erişimine açık ve işlenebilir elektronik veri',5),
        ('review','3. maddede bağımsız doğrulama ve denetim','incelemek, doğrulamak ve denetlemek üzere Bağımsız Fiyat ve Veri Doğrulama Kurulu',5),
        ('reports','3. maddede kamuya açıklama ve komisyona sunum','içinde kamuoyuna açıklar ve Türkiye Büyük Millet Meclisi Plan ve Bütçe Komisyonuna sunar.',6),
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
    doc = f'0412-stat-{key}'
    vid = doc+'-v1'
    original = f'objects/{digest}/original.'+('pdf' if ext=='pdf' else 'html.bin')
    readable = f'objects/{digest}/readable.html'
    put(original, raw)
    put(readable,readable_bytes(raw,ext,legacy=False))
    captured=datetime.fromtimestamp(fetched.stat().st_mtime,timezone.utc).isoformat()
    add('document',id=doc,party_id='demokrat',title=title,source_kind='official')
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
    else:
        assert [pdf_page_text(root/original,n).strip() for n in range(7)]==['']*7
    for suffix, section, exact, page in passages:
        if page is None:
            assert exact in body,(key,suffix,repr(exact))
        pid=doc+'-'+suffix
        add('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=page,printed_page=None)
        if page is not None:
            add('manual_passage',passage_id=pid,checked_at=now,
                method='Özgün PDF Poppler ile sayfa bazında görüntülendi.',
                reason='Yedi tarama sayfasının metin katmanı boş. Pasaj ve bağlam gözle okundu.')
out=checks/'statistics-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps({'party_id':'demokrat','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0412-statistics-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(sha256(out.read_bytes()).hexdigest(),len(entries),len(paths))
