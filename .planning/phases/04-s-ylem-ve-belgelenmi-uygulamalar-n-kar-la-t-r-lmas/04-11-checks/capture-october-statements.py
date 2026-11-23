"""Archive two earlier Saadet statements in the Yeni Yol meeting."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

checks,stage=map(Path,sys.argv[1:])
root=Path('data/practices/sources/saadet')
now=datetime.now(timezone.utc).isoformat()
entries,paths=[],set()


def add(table,**row):
    entries.append(dict(kind=table,values=row))


def save(relative,raw):
    p=root/relative
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
        assert p.read_bytes()==raw
    else:
        p.write_bytes(raw)
    paths.add(p)


sources = (
    ('07', '9eeabf60-6b31-4ae7-b5e0-01a1165658a5',
     '5e4957fed900dd99096549e9065333189cdaffbd73570e5567e8c5c714d2106c',
     '7 Ekim 2026, Mahmut Arıkan’ın fon zararının tazmini açıklaması',(
        ('date','Yayım günü ve saati','2026-10-07 - 13:01'),
        ('authority','Saadet ve Yeni Yol grup toplantısı bağlamı',
         "Saadet Partisi Genel Başkanı Arıkan, Yeni Yol Partisi'nin TBMM Grup Toplantısı'nda konuştu"),
        ('funding','Kamu finansmanı ile telafiye yönelik itiraz',
         'Milletin sol cebinden çalınanları, milletin sağ cebinden alınanlarla ödemek gibi bir hataya asla düşmemeliyiz.'),
        ('recovery','Sorumlulara dönük tazmin çağrısı',
         'Her bir kuruş, işin başındakilerden, parayı götürenlerden, tüyoyu verenlerden, alanlardan tazmin edilmeli.'),
    )),
    ('14','281ea457-e09f-4c1f-9881-01a139defde3',
     'cee28c14e222f1103ccf8f8201cec02ee5d6be656df859be10325b64ccd7654d',
     '14 Ekim 2026, Mahmut Arıkan’ın Mekke Anlaşması ve Yemen açıklaması',(
        ('date','Yayım günü ve saati','2026-10-14 - 13:04'),
        ('authority','TBMM künyesinde Saadet Genel Başkanlığı sıfatı','Saadet Partisi Genel Başkanı Mahmut Arıkan,'),
        ('agreement','Mekke Anlaşması başlığı','Mekke Ortak Savunma Anlaşması'),
        ('guarantee','Açık hükümler ve hukuki denetim talebi',
         'açık hükümlerle, belirlenmiş sınırlarla ve hukuki denetimle güvence altına alınmalıdır.'),
        ('proposal','Yemen arabuluculuğu için ayrı öneri',
         'Ankara\'da bir \'Yemen Diyalog Masası\' kurulmalıdır.'),
        ('prevent','Fon piyasası için önleyici adım çağrısı','Bugünden tedbir alınmasını istiyoruz.'),
    )),
)
for day, identity, digest, title, slices in sources:
    captured = stage/f'{day}-ekim-tbmm.html'
    raw = captured.read_bytes()
    assert sha256(raw).hexdigest()==digest
    date = '2026-10-'+day
    url = 'https://www.tbmm.gov.tr/Haber/Detay?Id='+identity
    doc = '0411-arikan-2026-10-'+day
    vid = doc+'-v1'
    original=f'objects/{digest}/original.html.bin'
    readable=f'objects/{digest}/readable.html'
    save(original,raw)
    save(readable,readable_bytes(raw,'html',legacy=False))
    add('document',id=doc,party_id='saadet',title=title,source_kind='official')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,date_precision='day',
        date_unknown_reason=None,version_label='TBMM haberinin özgün nüshası.',
        accessed_at=datetime.fromtimestamp(captured.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='text/html',sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',public_url=url,
        published_at=date,date_precision='day',social_handle=None,
        basis='Haber künyesi, konuşmacının sıfatı ve toplantı metni birlikte okundu.')
    view=build_view(raw,url,root,fetch_assets=False)
    view['version_id']=vid
    manifest=root/view['manifest_path']
    paths.add(manifest)
    paths.update(manifest.parent/f for f in json.loads(manifest.read_bytes())['files'])
    validate_view(root,view)
    add('archive_view',**view)
    body=html_source_text(raw)
    for key,section,exact in slices:
        assert exact in body, (day,key,exact)
        add('passage',id=doc+'-'+key,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=None,printed_page=None)
out=checks/'october-statements-source-records.json'
with out.open('x') as handle:
    handle.write(json.dumps(dict(party_id='saadet',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0411-october-statements-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths),sha256(out.read_bytes()).hexdigest())
