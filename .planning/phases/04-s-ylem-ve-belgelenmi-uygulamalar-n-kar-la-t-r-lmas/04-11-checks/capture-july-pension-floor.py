"""Archive the July pension floor law and the separate Saadet statement."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage, paths_output = map(Path,sys.argv[1:])
root=Path('data/practices/sources/saadet')
now=datetime.now(timezone.utc).isoformat()
sources=(
    ('aa','Son Dakika','ANKA','2026-07-01','journalism','journalism',
     '1 Temmuz Arıkan grup konuşmasında en düşük emekli aylığı hedefi',
     'https://www.sondakika.com/amp/haber-arikan-nato-hazirliklari-utanc-verici-20007729/',
     'ca88623b948ef97c773021fe784ffe64571ca0aaf1f678de58bc3921dbd1b712',
     (('day','ANKA haberinin yayım zamanı','2026-07-01T11:28:00+03:00'),
      ('target','Arıkan’ın temmuz ayına ilişkin eşitleme talebi',
       'en düşük emekli maaşını asgari ücrete eşitleyecek kalıcı bir kanuni düzenleme yapalım.'))),
    ('wage-announcement','Çalışma ve Sosyal Güvenlik Bakanlığı',None,'2025-12-23','official','official',
     'Bakanlığın 2026 yılı net ve brüt asgari ücret duyurusu',
     'https://www.csgb.gov.tr/haberler/2026-yilinda-gecerli-olacak-yeni-asgari-ucret-28-bin-75-lira-olarak-belirlendi',
     '673bf2fc8408d4001a67831b3f4347050cb65bf68c289ba76e532c393ea57a80',
     (('net','1 Ocak 2026’dan geçerli net asgari ücret',
       'net asgari ücret 28 bin 75 lira 50 kuruş'),
      ('gross','Brüt asgari ücretin farklı tutarı','brüt asgari ücret tutarı ise 33 bin 30 lira'))),
    ('law-detail','TBMM',None,None,'official','official',
     '7590 sayılı Kanunun kabul ve Resmî Gazete sicili',
     'https://tbmm.gov.tr/Yasama/Kanun/da9978b9-5655-4725-8ffa-019f273b6db5',
     '5d3d3ee7885e732a9b1a29a22679c1d39af5e433687bdf726d7da9265cce7ea7',
     (('accept','7590 sayılı Kanunun kabul tarihi','24/07/2026'),
      ('gdate','Resmî Gazete yayım günü','31/07/2026'),
      ('gno','Resmî Gazete sayı numarası','33326'))),
    ('law-text','TBMM',None,'2026-07-31','official','official',
     '7590 sayılı Kanunun kabul edilen metni',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/KanunMetni/152a9101-15fe-4138-aceb-99a304bb9ec3.htm',
     'cc1cbfd4c5d3f72b08554acaf3dfbd2df9383845e3b631bb87d57a30a7e5f07d',
     (('amend','7590 m.16. 5510 ek m.19 değişikliği',
       'alan “20.000” ibaresi “23.552” şeklinde değiştirilmiştir.'),
      ('effect','7590 m.31/ç. Temmuz ödeme dönemi ve yayım yürürlüğü',
       'ncı maddesi 2026 yılı Temmuz ayı ödeme döneminden itibaren uygulanmak üzere\r\nyayımı tarihinde,'))),
)
entries=[]
written=set()

def add(table,**values):
    entries.append(dict(kind=table,values=values))

def archive(path,body):
    dest=root/path
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.is_file():
        assert dest.read_bytes()==body
    else:
        dest.write_bytes(body)
    written.add(str(dest))

for key,publisher,author,published,source_kind,attribution_kind,title,url,digest,passages in sources:
    path=stage/f'pension-{key}.html'
    raw=path.read_bytes()
    body=html_source_text(raw)
    assert sha256(raw).hexdigest()==digest
    doc=f'0411-july-pension-{key}'
    vid=doc+'-v1'
    original=Path('objects')/digest/'original.html.bin'
    readable=original.parent/'readable.html'
    archive(original,raw)
    archive(readable,readable_bytes(raw,'html',legacy=False))
    add('document',id=doc,party_id='saadet',title=title,source_kind=source_kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date='2026-07-24' if key=='law-text' else published,
        date_precision='day' if published else 'unknown',date_unknown_reason=None if published else 'TBMM sicil sayfasının ilk yayım günü açık.',version_label='Yayının erişilen özgün HTML sürümü.',
        accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,
        mime='text/html',sha256=digest,original_path=str(original),readable_path=str(readable))
    add('source_attribution',version_id=vid,publisher=publisher,author=author,kind=attribution_kind,
        published_at=published,date_precision='day' if published else 'unknown',social_handle=None,public_url=url,
        basis='Yayın adı ve zaman bilgisi özgün sayfada. Yazar adı mevcutsa yayındaki atıf kullanıldı.')
    view=build_view(raw,url,root,fetch_assets=False)
    view['version_id']=vid
    validate_view(root,view)
    add('archive_view',**view)
    manifest=root/view['manifest_path']
    written.add(str(manifest))
    written.update(str(manifest.parent/key) for key in json.loads(manifest.read_bytes())['files'])
    for name,heading,exact in passages:
        assert exact in body,(key,name,exact)
        add('passage',id=doc+'-'+name,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
            section=heading,pdf_page_index=None,printed_page=None)
with (checks/'july-pension-floor-source-records.json').open('x') as stream:
    stream.write(json.dumps(dict(party_id='saadet',entries=entries),ensure_ascii=False,indent=2)+'\n')
paths_output.write_text('\n'.join(sorted(written))+'\n')
print(len(entries),len(written))
