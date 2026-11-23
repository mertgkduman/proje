"""Archive the original published accounts of the Yıldırım district congress."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/saadet')
now = datetime.now(timezone.utc).isoformat()
sources = (
 ('bursa-saati','bursa','Yıldırım kongresi ve yeniden seçim, Bursa Saati','Bursa Saati','Burhan Kurtulmuş','news','2026-09-27',
  'https://www.bursasaati.com.tr/bursada-saadet-coskusu-mahmut-arikan-yildirim-kongresinde-konustu',
  '1ec758aa721a5de8eb2b5a2d50ea64f4898cd75e587e833c47c6f4abc0527a65',(
    ('day','27 Eylül haberin ilk yayım zamanı','article:published_time" content="2026-09-27T18:21:00+03:00'),
    ('occurred','Haber gövdesinde kongrenin gerçekleşmesi','Genel Başkan Mahmut Arıkan’ın katılımıyla yoğun ve coşkulu bir atmosferde gerçekleştirildi.'),
    ('election','Haber gövdesinde Nuri Keçeli’nin yeniden seçilmesi',
     'Kongrede yapılan seçim sonucunda Nuri Keçeli yeniden Saadet Partisi Yıldırım İlçe Başkanlığı görevine seçilerek güven tazeledi.'),
  )),
 ('vatan-plan','plan','Yıldırım 10. Olağan İlçe Kongresi ön duyurusu','Vatan Havadis',None,'news','2026-09-19',
  'https://www.vatanhavadis.com/siyaset/bursa-da-saadet-partisi-heyecani-genel-baskan-mahmut-arikan-yildirim-kongresi-icin-geliyor-142739',
  '1a8eeba46639f349d0d8f90d4efa7fc89e804f7b5a1b536bb6d29100e5da2afb',(
    ('day','Ön duyuruda 27 Eylül ve kongre numarası',
     '27 Eylül 2026 Pazar günü saat 15.30&#39;da Bursa Barış Manço Kültür Merkezi&#39;nde düzenlenecek olan Yıldırım İlçe Teşkilatı 10. Olağan Kongresi'),
  )),
 ('vatan-outcome','result','Vatan Havadis’in Yıldırım kongresi seçim haberi','Vatan Havadis',None,'news','2026-09-27',
  'https://www.vatanhavadis.com/gundem/yildirim-da-sandiktan-nuri-keceli-cikti-mahmut-arikan-dan-umut-mesaji-145184',
  'f1e5f3dc759021d78d829855f1bc00ecefbdb4d01aa195943284cf88a7fbf999',(
    ('day','Sonuç haberinin ilk yayın saati','Haber Giriş Tarihi: 27.09.2026 20:56'),
    ('election','Aynı gün yayımlanan sonuç, Nuri Keçeli',
     'Saadet Partisi Yıldırım İlçe Kongresi&#39;nde yapılan seçim sonucunda Nuri Keçeli, yeniden İlçe Başkanlığı görevine seçildi.'),
  )),
)
entries, paths = [], set()


def add(table, **values):
    entries.append(dict(kind=table,values=values))


def save(path, content):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes()==content
    else:
        path.write_bytes(content)
    paths.add(path)


for filename,key,title,publisher,author,kind,published,url,digest,anchors in sources:
    raw_file=stage/f'{filename}.html'; raw=raw_file.read_bytes()
    assert sha256(raw).hexdigest()==digest
    doc=f'0411-yildirim-congress-{key}';version=doc+'-v1'
    original=f'objects/{digest}/original.html.bin';readable=f'objects/{digest}/readable.html'
    save(root/original,raw);save(root/readable,readable_bytes(raw,'html',legacy=False))
    add('document',id=doc,party_id='saadet',title=title,source_kind=kind)
    add('document_version',id=version,document_id=doc,original_url=url,final_url=url,document_date=published,
        date_precision='day',date_unknown_reason=None,version_label='Özgün yayımlanan web nüshası.',mime='text/html',
        accessed_at=datetime.fromtimestamp(raw_file.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,
        sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=version,publisher=publisher,author=author,
        kind='journalism',published_at=published,
        date_precision='day' if published else 'unknown',social_handle=None,public_url=url,
        basis='Yayıncı, kongre ve sonuç atıfları özgün gövdede okundu.')
    view=build_view(raw,url,root,fetch_assets=False);view['version_id']=version;validate_view(root,view)
    manifest=root/view['manifest_path'];paths.add(manifest)
    paths.update(manifest.parent/n for n in json.loads(manifest.read_bytes())['files'])
    add('archive_view',**view)
    body=html_source_text(raw)
    for suffix,section,exact in anchors:
        assert exact in body,(key,suffix)
        add('passage',id=doc+'-'+suffix,version_id=version,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=None,printed_page=None)
out=checks/'yildirim-congress-source-records.json'
with out.open('x') as handle:
    handle.write(json.dumps(dict(party_id='saadet',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'yildirim-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths),sha256(out.read_bytes()).hexdigest())
