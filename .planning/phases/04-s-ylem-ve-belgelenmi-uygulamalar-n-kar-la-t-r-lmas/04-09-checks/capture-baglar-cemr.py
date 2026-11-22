"""Keep the DBP conference report, Bağlar decision, and later signature record."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/dbp')
entries = []
paths = set()
now = datetime.now(timezone.utc).isoformat()


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def save(relative, content):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == content, path
    else:
        path.write_bytes(content)
    paths.add(path)


sources = (
    ('women','html','https://www.wanhaber.com/yerel-yonetimler-merkezi-kadin-konferansi-sonuc-bildirgesi-aciklandi',
     'Wan Haber, DBP Yerel Yönetimler Merkezi Kadın Konferansı sonuç bildirgesi',
     '2014-12-22','2014-12-22','Wan Haber',None,'news','0372f667b08019662e851ae2894d8fc74ad7bc05729ab156f843b141567ce612',[
        ('conference','Konferansı ve sonuç bildirgesini birlikte tanımlayan paragraf',
         "3 gündür devam eden DBP Yerel Yönetimler Merkezi Kadın Konferansı, 3'üncü günün sonunda",None),
        ('cemr','Konferans bildirgesinin CEMR maddesi',
         'CEMR belgesinin tüm belediyelerimiz tarafından onaylanıp toplu olarak imzalanması.',None),
     ]),
    ('baglar','pdf','https://www.baglar.bel.tr/Content/uploads/21863ec7-9e03-474f-a5ef-053be6f60cdb.pdf',
     'Bağlar Belediyesi 2015 meclis kararları, 2015/48 CEMR kararı',
     None,None,'Bağlar Belediye Başkanlığı',None,'official','6059362c11b4a6e867ec207394929002475c1b5d0cec6ee142a8eb65e61dccd3',[
        ('decision-id','Meclis kararı 2015/48 başlığı ve konu',
         'Karar No\n: 2015/48\nKarar Konusu : Yerel YaĢamda Kadın-Erkek EĢitliği\nġartı (CEMR)\n06/02/2015',52),
        ('agenda','Kültür ve Sosyal İşleri Müdürlüğünün 3 Şubat tarihli yazısı',
         '03/02/2015 tarih ve 133 sayılı',52),
        ('approval','Mevcudun oybirliğiyle onay ve karar günü',
         'mevcudun oy birliği ile kabulüne karar\nverildi. 06/02/2015',52),
        ('chair','Belgede Meclis Başkanı Birsen Kaya Akat',
         'Birsen KAYA AKAT\nMeclis BaĢkanı',52),
     ]),
    ('aa','html','https://www.aa.com.tr/tr/turkiye/baglar-belediye-baskani-akat-dbpden-ihrac-edildi/855723',
     'Anadolu Ajansı, Birsen Kaya Akat’ın 2014 seçimi ve 2017 parti açıklaması',
     '2017-07-06','2017-07-06','Anadolu Ajansı',None,'news','8fd61cd809111346c967a964a53eea0716114c469c3ab0388f57bd50e1df36c2',[
        ('election','Meclis başkanının 2014 yerel seçimindeki parti ve kimliği',
         "30 Mart 2014'te yapılan yerel seçimlerde o zamanki adıyla Barış ve Demokrasi Partisinden <strong>Bağlar Belediye Başkanı </strong>seçilen <strong>Birsen Kaya Akat'",None),
        ('membership','2017 DBP il başkanı açıklamasındaki parti ve kişi bağı',
         "DBP İl Başkanı Zeki Baran, AA muhabirine yaptığı açıklamada, Akat'ın DBP Disiplin Kurulu kararıyla partiden ihraç edildiğini",None),
     ]),
    ('tbb','html','https://www.tbb.gov.tr/tr/cemr-avrupa-yerel-yasamda-kadin-erkek-esitligi-sarti',
     'Türkiye Belediyeler Birliği CEMR işlem adımları ve imza tablosu',
     None,None,'Türkiye Belediyeler Birliği',None,'official','0e5ea4f62eece39b2c0aef7a8eb96e85f7c014dc14dce25b5a0bc5caa03ffd47',[
        ('submission','CEMR’a iletim adımı',
         'İmzalanan belge, CEMR’a gönderilmek üzere Türkiye Belediyeler Birliğine gönderilmeli.',None),
     ]),
)
for name,ext,url,title,day,published,publisher,author,kind,expected,anchors in sources:
    original_file = stage / (name + '.body')
    raw = original_file.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest == expected, name
    document = '0409-cemr-' + name
    version = document + '-v1'
    original = f'objects/{digest}/' + ('original.pdf' if ext == 'pdf' else 'original.html.bin')
    readable = f'objects/{digest}/readable.html'
    save(original, raw)
    save(readable, readable_bytes(raw, ext, legacy=False))
    add('document', id=document, party_id='dbp', title=title, source_kind=kind)
    add('document_version', id=version, document_id=document, original_url=url, final_url=url,
        document_date=day, date_precision='day' if day else 'unknown',
        date_unknown_reason=None if day else 'Derlemenin yayımlanma günü açık. Seçili karar veya imza tarihi pasajda.',
        version_label='Özgün erişilen nüsha.',
        accessed_at=datetime.fromtimestamp(original_file.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now, mime='application/pdf' if ext == 'pdf' else 'text/html',
        sha256=digest, original_path=original, readable_path=readable)
    add('source_attribution', version_id=version, publisher=publisher, author=author,
        kind='official' if kind == 'official' else 'journalism', published_at=published,
        date_precision='day' if published else 'unknown', social_handle=None, public_url=url,
        basis='Özgün belgede yayımlayan kurum, haber tarihi veya karar tarihi kontrol edildi.')
    if ext == 'html':
        view = build_view(raw, url, root, fetch_assets=False)
        view['version_id'] = version
        validate_view(root, view)
        add('archive_view', **view)
        manifest = root / view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent / name for name in json.loads(manifest.read_bytes())['files'])
        body = html_source_text(raw)
        if name == 'tbb':
            name_position = body.index('Bağlar Belediyesi')
            begin = body.rindex('<tr>',0,name_position)
            end = body.index('</tr>',name_position)+len('</tr>')
            row = body[begin:end]
            assert '01.10.2024' in row
            anchors.append(('signature','TBB imza tablosunda Bağlar Belediyesi ve tarih',row,None))
    else:
        body = pdf_page_text(root / original, 52)
    for key,section,exact,page in anchors:
        assert exact in body, (name,key,repr(exact))
        add('passage', id=document+'-'+key,version_id=version,exact=exact,prefix=None,suffix=None,
            article=None,section=section,pdf_page_index=page,printed_page=None)

output = checks / 'baglar-cemr-source-records.json'
with output.open('x') as stream:
    stream.write(json.dumps(dict(party_id='dbp',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0409-baglar-cemr-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(sha256(output.read_bytes()).hexdigest(),len(entries),len(paths))
