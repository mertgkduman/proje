"""Archive the complete originals and quote the read Tokluca passages."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage, paths_output = map(Path, sys.argv[1:])
root = Path('data/practices/sources/dbp')
now = datetime.now(timezone.utc).isoformat()
municipality = 'Bağlar Belediyesi'
attachment = 'https://www.baglar.bel.tr/Content/uploads/'
kanun = 'https://cdn.tbmm.gov.tr/KKBSPublicFile/'
originals = (
    ('council2010.pdf', 'pdf', attachment+'cfbb3e73-b60c-4bfc-b12f-63ce1b24c2c6.pdf',
     'Bağlar Belediye Meclisi 2010 karar derlemesi', municipality, None,
     'c25254ccb92374683c3ff0ae45ed14f3d7b547f70364540bc426fd9b0359d422'),
    ('council2011.pdf', 'pdf', attachment+'c65c9df2-57f2-47d7-9ba0-73a36d57e7b1.pdf',
     'Bağlar Belediye Meclisi 2011 karar derlemesi', municipality, None,
     'da7ad6ed7e72c836fd37bb2be47de32fac747054aa46b45b99b1231cff1e1c21'),
    ('council2016.pdf', 'pdf', attachment+'650ee114-c24f-482a-b241-4a4036f5aff2.pdf',
     'Bağlar Belediye Meclisi 2016 karar derlemesi', municipality, None,
     '8364a09ace89fc806e5d65ea578e6eef8054bcaf54f3d41ddf9c7c5e298ffca1'),
    ('council2021.pdf', 'pdf', attachment+'956e0249-8362-43c5-9697-c21ffd8161d9.pdf',
     'Bağlar Belediyesi faaliyet raporu, 2021 yol çalışmaları', municipality, None,
     '8da91ece7c0f1d7c5e1a593795f941bece65392a70907f576706a2892d341ff7'),
    ('belediye-5393.html', 'html', kanun+'D22/Y3/T1/KanunMetni/9df50352-880c-4072-8dd7-29deb3942567.html',
     '5393 sayılı Belediye Kanunu, TBMM’nin kabul ettiği metin', 'TBMM', '2005-07-03',
     'afdf6c289d84ca15bdd841c2f80a4c1c5bb46dbe960ba830442fd19ef097b760'),
    ('belediye-6360.html', 'html', kanun+'D24/Y3/T1/KanunMetni/6fd1dca0-c56a-40ef-bc98-fb463d9ac578.html',
     '6360 sayılı Kanun, TBMM’nin kabul ettiği metin', 'TBMM', '2012-11-12',
     '43bf4f0b09057fa1b91d12a4ea4e6b54573533ee7a5b673de37582c9c4c60371'),
)
entries = []
written = set()
source_paths = {}

def add(table, **row):
    entries.append(dict(kind=table, values=row))

def archive(path, data):
    destination = root/path
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        assert destination.read_bytes() == data
    else:
        destination.write_bytes(data)
    written.add(str(destination))

def source_id(label):
    return '0409-tokluca-'+label

for name,fmt,url,title,publisher,date,digest in originals:
    p = stage/name
    raw = p.read_bytes()
    assert sha256(raw).hexdigest() == digest
    doc = source_id(p.stem)
    vid = doc+'-v1'
    original = Path('objects')/digest/('original.pdf' if fmt=='pdf' else 'original.html.bin')
    readable = original.parent/'readable.html'
    archive(original,raw)
    archive(readable,readable_bytes(raw,fmt,legacy=False))
    source_paths[p.stem] = (vid, root/original)
    day = bool(date and len(date)==10)
    date_precision = 'day' if day else ('year' if date else 'unknown')
    add('document', id=doc,party_id='dbp',title=title,source_kind='official')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,
        date_precision=date_precision,date_unknown_reason=None if date else 'Belgenin kapsadığı dönem başlıkta belirtiliyor. Yayım günü doğrulanamadı.',
        version_label='Arşivdeki özgün kurum nüshası.',accessed_at=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='application/pdf' if fmt=='pdf' else 'text/html',
        sha256=digest,original_path=str(original),readable_path=str(readable))
    add('source_attribution',version_id=vid,publisher=publisher,author=None,kind='official',published_at=None,
        date_precision='unknown',social_handle=None,public_url=url,basis='Belgeyi yayımlayan kurumun açık arşivi.')
    if fmt=='html':
        view = build_view(raw,url,root,fetch_assets=False)
        view['version_id'] = vid
        validate_view(root,view)
        add('archive_view',**view)
        manifest = root/view['manifest_path']
        written.add(str(manifest))
        written.update(str(manifest.parent/n) for n in json.loads(manifest.read_bytes())['files'])

source_paths['council2015'] = ('0409-cemr-baglar-v1',
    root/'objects/6059362c11b4a6e867ec207394929002475c1b5d0cec6ee142a8eb65e61dccd3/original.pdf')
passages = (
    ('council2010',253,'2010-227','2010/227 komisyona sevk','Tokluca Mezrasının Batıkarakoç Mahallesinden'),
    ('council2011',19,'2011-20','2011/20 araştırma ve rapor talebi','24/11/2010 tarih ve 2804 sayılı dilekçesinde'),
    ('council2011',61,'2011-54','2011/54 geçmiş mahalle önerisi','Tomat (Tokluca) adıyla mahalle olma isteklerinin'),
    ('council2011',190,'2011-183','2011/183 ayrı yol çalışması','Tavşantepe-Tokluca-Uzunbahçe gurup yolu'),
    ('council2015',22,'2015-22-file','Avşin dosyası karar numarası','2015/22'),
    ('council2015',22,'2015-22-plan','Avşin adıyla mahalle önerisi','AvĢin Mahallesi ismi ile yeni mahalle kurulması;'),
    ('council2015',22,'2015-22-people','Mahalle sakinlerinin hane ve nüfus bilgisi','hane sayısının 60 olduğu ve yaklaĢık 564 kiĢinin yaĢadığı'),
    ('council2015',22,'2015-22-vote','Komisyon raporu kabulü','kabulüne karar verildi.09/01/2015'),
    ('council2015',257,'2015-251-file','Yeniden komisyona sevk karar numarası','2015/251'),
    ('council2015',257,'2015-251-letter','Kaymakamlık yazısına belediye kararı içindeki atıf','26/11/2015 tarih ve 490-E.3299 sayılı yazısında'),
    ('council2015',257,'2015-251-referral','İnceleme ve Araştırma Komisyonuna sevk','önergenin Ġnceleme ve AraĢtırma Komisyonuna havale edilerek'),
    ('council2015',257,'2015-251-vote','Sevk oylaması','verildi.11/12/2015'),
    ('council2016',67,'2016-64-file','Yenilenen Avşin dosyası karar numarası','2016/64'),
    ('council2016',67,'2016-64-letter','583 sayılı müdürlük yazısına atıf','07/12/2015 tarih ve 583 sayılı'),
    ('council2016',68,'2016-64-plan','Avşin adıyla yenilenen kuruluş önerisi','Avşin Mahallesi ismi ile yeni mahalle kurulması;'),
    ('council2016',68,'2016-64-people','Mahalle sakinlerinin yenilenen nüfus bilgisi','hane sayısının 75 olduğu ve yaklaşık 520 kişinin yaşadığı'),
    ('council2016',68,'2016-64-vote','Yenilenen raporun kabulü','oy birliği ile kabulüne karar verildi.\n11/03/2016'),
    ('council2016',192,'2016-187-file','Tokluca adı karar numarası','2016/187'),
    ('council2016',192,'2016-187-request','Avşin adı üzerinde uzlaşmazlık dilekçesi','29/08/2016 tarih 4774 sayılı dilekçesinde'),
    ('council2016',192,'2016-187-name','Önerilen yeni Tokluca adı','Avşin Mahallesi yerine Tokluca Mahallesi olarak değiştirilmesi'),
    ('council2016',192,'2016-187-vote','Ad değişikliği önerisinin kabulü','oy birliği ile kabulüne karar\nverildi.08/09/2016'),
    ('council2021',75,'2021-road','2021 ilk yarı çalışmaları tablosu','16 Tokluca mah. 1275'),
    ('council2021',77,'2021-road-later','2021 ikinci yarı çalışmaları tablosu','16 Tokluca Mahallesi'),
    ('belediye-5393',None,'5393-approval','5393 sayılı Kanun 9. madde','belediye meclisinin kararı ve kaymakamın görüşü üzerine valinin onayı ile olur.'),
    ('belediye-5393',None,'5393-effect','5393 sayılı Kanun 12. madde','takip eden yılın ocak ayının birinci gününden itibaren yürürlüğe girer.'),
    ('belediye-6360',None,'6360-threshold','6360 sayılı Kanun 15. madde','nüfusu 500’ün altında mahalle kurulamaz.'),
)
for source,index,key,heading,exact in passages:
    vid, local = source_paths[source]
    body = pdf_page_text(local,index) if index is not None else html_source_text(local.read_bytes())
    assert exact in body,(key,exact,body[-1250:])
    add('passage',id=source_id(key),version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
        section=heading,pdf_page_index=index,printed_page=None)

def emit(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

emit(checks/'baglar-tokluca-source-records.json',dict(party_id='dbp',entries=entries))
paths_output.write_text('\n'.join(sorted(written))+'\n')
print(len(entries),len(written))
