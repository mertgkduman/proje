"""Capture the dated TBMM documents for the 2/3939 debate."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path,sys.argv[1:])
sources = Path('data/practices/sources')
root = sources/'iyi'
now = datetime.now(timezone.utc).isoformat()
paths, entries = set(), []
already = json.loads(Path('data/practices/04-yeni-parti.json').read_bytes())['entries']
tutanak = 'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/'


def save(relative, content):
    path = root/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes()==content
    else:
        path.write_bytes(content)
    paths.add(path)


def add(table,**row):
    entries.append(dict(kind=table,values=row))


assets = (
    ('oct07.html','oct07','7 Ekim 2026 Genel Kurul tam tutanağı','2026-10-07',
     tutanak+'3/Tam/5e3c67e6-7f96-4c37-9401-393802259f00.html',
     '248d35a6070a1858effe9173b47f9a2824c090fa85f74fa1fb5ae2eab6631a1c','windows-1254',
     [('usta-role','Erhan Usta’nın 7 Ekim İYİ grup sıfatı','İYİ PARTİ GRUBU ADINA ERHAN USTA (Samsun)'),
      ('usta-plan','Usta’nın araştırma komisyonu talebi','Mecliste komisyon kurulması son derece önemlidir.'),
      ('dalgin-role','Burak Dalgın’ın 7 Ekim İYİ grup sıfatı','İYİ PARTİ GRUBU ADINA BURAK DALGIN (Balıkesir)'),
      ('dalgin-plan','Dalgın’ın araştırma komisyonunda eşit temsil önerisi','grubu olan her partiden eşit üyeden müteşekkil bir komisyon kurardık.')]),
    ('oct07-summary.html','oct07-summary','7 Ekim 2026 Genel Kurul özeti','2026-10-07',
     tutanak+'3/Ozet/b749992e-fb8b-44ef-afd3-4a0522a593f1.html',
     'b45a47227d6aaee3bd0acd01293285abf7db69ffcf32db2cea559fcbeec6e2d0','windows-1254',
     [('role','Özette İYİ adına söz alan milletvekilleri','Erhan Usta ile Balıkesir Milletvekili Burak Dalgın')]),
    ('oct20-ham.html','oct20','20 Ekim 2026 Genel Kurul ham tutanağı','2026-10-20',
     tutanak+'8/Ham/dcb831f7-1664-48cd-8209-d84d460415f8.html',
     'a1a7038f7af34b3ca15ec0f5603d19b41b7df64468ec04160234c4752377c522',None,
     [('role','2/3939 görüşmesinde Erhan Usta’nın İYİ grup sıfatı','İYİ PARTİ GRUBU ADINA ERHAN USTA (Samsun)'),
      ('scope','Usta’nın zorunlu iade kapsamı','suça bulaşmamış ama ciddi miktarda fahiş kazanç elde etmiş insanlar'),
      ('goal','Usta’nın olağanüstü getirilerin zorunlu geri alınması çağrısı','Dolayısıyla, buralardan da bu paralar cebrî olarak alınmalıdır ki havuzun kaynağı artsın.')]),
    ('oct22-ham.html','oct22','22 Ekim 2026 Genel Kurul ham tutanağı','2026-10-22',
     tutanak+'10/Ham/9d2247ec-f63a-4c5d-8d9c-52fd57a71a1a.html',
     'be088b4f0c0de533e363906a9ddcb7cc19ef6374b3c56321e6731527cebe47c2',None,
     [('sunat-role','Şenol Sunat’ın 9. madde üzerindeki grup sıfatı',
       'ŞENOL SUNAT (Manisa) - Evet, Sayın Başkan, değerli milletvekilleri; görüşmekte olduğumuz kanun teklifinin 9\'uncu maddesi üzerine verdiğimiz önerge üzerinde İYİ Parti Grubu adına söz aldım'),
      ('sunat-objection','Sunat’ın isteğe bağlı iade itirazı',
       'olağan dışı getirilerin geri ödenmesi isteğe bağlı bir mekanizmaya bırakılmaktadır. İYİ Parti olarak bu düzenlemeye itiraz ediyoruz.'),
      ('electron','Teklifin tümü için elektronik oylama açıklaması',
       'Divanda ihtilaf olduğundan dolayı elektronik cihazla oylamaya başvuracağım.'),
      ('accept','Başkanın 2/3939 kabul açıklaması','BAŞKAN - Teklif kabul edilmiş ve kanunlaşmıştır.')]),
    ('oct22-summary.html','oct22-summary','22 Ekim 2026 Genel Kurul özeti','2026-10-22',
     tutanak+'10/Ozet/71dc404e-93b4-4ccc-bc02-124b9910ccaf.html',
     'dac5a7469af5b0d7ccce4e720ade3496346d6e7eed083d6bb063d9b40203cead','windows-1254',
     [('accept','294 sıra sayılı teklifin kabulü','görüşmeleri tamamlanarak kabul edildi.')]),
    ('law.html','law','7596 sayılı kanun kayıt kartı','2026-10-22',
     'https://tbmm.gov.tr/Yasama/Kanun/1ea72322-e59c-4d76-b4d0-01a120a2361a',
     '01efb17d7847abb3fb0da84f5cb6d5714c8c00119e521be38d3839b85635dcc8',None,
     [('date','Kanun kayıt kartındaki kabul tarihi','<td>22/10/2026</td>'),
      ('pub','Kanun kayıt kartındaki Resmî Gazete tarihi','<td> 27/10/2026</td>')]),
    ('law-text.html','law-text','7596 sayılı Kanunun kabul edilen metni','2026-10-22',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/KanunMetni/e15f4510-0860-4ccb-ab21-5dc05a661ad8.htm',
     '47cd4aab17cfacb1e0f528616d088b634b15e3b4a8ffc37cc5aeda083911123e',None,
     [('voluntary','4. madde 4. fıkrada ilan edilen hesaba isteğe bağlı iade','hesaplara isteğe bağlı olarak iade edilebilir.'),
      ('shares','4. madde 4. fıkrada genel hisse iade hesabı','genel hisse iade hesabına isteğe bağlı olarak iade edilebilir.'),
      ('liability','5. madde 2. fıkrada tespit edilenlerin şahsen sorumluluğu','kişiler ile bu kişilerle birlikte hareket ettiği tespit edilenler şahsen\r\nsorumludur.'),
      ('enforcement','5. madde 4. fıkrada TMSF’nin işlemleri','TMSF tarafından tahsil ve takip işlemleri başlatılır.')]),
)
for filename,key,title,day,url,h,charset,anchors in assets:
    file=stage/filename
    raw=file.read_bytes()
    assert sha256(raw).hexdigest()==h
    doc='0407-fund-'+key
    vid=doc+'-v1'
    original=f'objects/{h}/original.html.bin'
    readable=f'objects/{h}/readable.html'
    old_version=next((r['values'] for r in already if r['kind']=='document_version'
                      and r['values']['sha256']==h and r['values']['final_url']==url),None)
    old_root=next((d for d in (sources/'yeni-parti',sources/'emep') if (d/original).is_file()),None)
    if old_root:
        assert (old_root/original).read_bytes()==raw
    save(original,raw)
    save(readable,(old_root/readable).read_bytes() if old_root else readable_bytes(raw,'html',legacy=False))
    add('document',id=doc,party_id='iyi',title=title,source_kind='official')
    accessed=datetime.fromtimestamp(file.stat().st_mtime,timezone.utc).isoformat()
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,
        document_date=day,date_precision='day',date_unknown_reason=None,
        version_label='TBMM özgün nüshası.',accessed_at=accessed,verified_at=now,
        mime='text/html',sha256=h,original_path=original,readable_path=readable)
    view=next((r['values'].copy() for r in already if r['kind']=='archive_view'
               and old_version and r['values']['version_id']==old_version['id']),None)
    if view:
        manifest=Path(view['manifest_path'])
        assert old_root
        save(manifest,(old_root/manifest).read_bytes())
        for f in json.loads((root/manifest).read_bytes())['files']:
            save(manifest.parent/f,(old_root/manifest.parent/f).read_bytes())
    else:
        view=build_view(raw,url,root,fetch_assets=False,http_charset=charset)
        manifest=Path(view['manifest_path'])
        paths.add(root/manifest)
        paths.update(root/manifest.parent/f for f in json.loads((root/manifest).read_bytes())['files'])
    view['version_id']=vid
    validate_view(root,view)
    add('archive_view',**view)
    add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',published_at=None,
        date_precision='unknown',social_handle=None,public_url=url,basis='Özgün TBMM nüshasındaki işlem ve aktör başlığı.')
    body=html_source_text(raw)
    for suffix,section,exact in anchors:
        assert exact in body,(key,suffix)
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=None,printed_page=None)
(checks/'fund-floor-source-records.json').write_text(
    json.dumps(dict(party_id='iyi',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
