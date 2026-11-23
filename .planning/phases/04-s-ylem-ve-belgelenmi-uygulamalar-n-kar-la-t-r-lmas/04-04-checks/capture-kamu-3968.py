"""Archive and transcribe the necessary passages of the scanned 2/3968 bill."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path,sys.argv[1:])
root = Path('data/practices/sources/yeni-parti')
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def store(relative, content):
    path = root/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes() == content
    else:
        path.write_bytes(content)
    paths.add(path)


sources = (
    ('signed.pdf','signed','2/3968 imzalı kanun teklifi','2026-10-21',None,'TBMM','official',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T2/WebOnergeMetni/17e4e47e-432a-46f2-823b-17184123f812.pdf',
     'fcdb84ee41a1ada820e0252a98cdb1fa8bdbda3f67abb3eb9c2dddcd4e868d2d',[
         ('signature','Kapak, imza ve grup başkanvekili sıfatı',0,'Doç. Dr. Gökhan GÜNAYDIN\nİstanbul Milletvekili\nYENİ Parti Grup Başkanvekili'),
         ('file','Kapak, 2/3968 ve Plan ve Bütçe kutusu',0,'Esas No:2/3968'),
         ('stamp','İkinci sayfa, TBMM Genel Evrak tarihi',1,'21 Ekim 2026'),
         ('goal','Genel gerekçede kamu kaynağı ve ölçülülük',2,'kamu görevlilerine tanınan mali hakların ölçülülük ilkesine uygun biçimde'),
         ('pay','4. madde gerekçesi, SPK görevi ve ödemeler',3,'Sermaye Piyasası Kurulu başkan ve üyelerinden'),
         ('compensation','5. madde gerekçesi, tazminat sınırı',4,'görevde kaldıkları her yıl için ödenecek tazminat, kıdem tazminatı tavanıyla'),
         ('series','Teklif maddelerinde farklı kurumlara ilişkin değişiklikler',5,'132’nci maddesinin birinci fıkrasının ikinci, üçüncü ve dördüncü cümleleri'),
         ('compensation-text','5. madde, tazminat için teklif metni',5,'bir hizmet yılı için ödenecek azami emeklilik ikramiyesini geçmeyecek'),
     ]),
    ('detail.html','detail','2/3968 TBMM kanun teklifi kaydı',None,None,'TBMM','official',
     'https://tbmm.gov.tr/Yasama/KanunTeklifi/bad9a2b0-f0bb-493c-b17b-01a15e26a009',
     '82953f0ff80c7f1ae1c45d74c80ee5ed2960d48a893831ad25133dbc917572de',[
         ('id','Esas numarası',None,'<td>2 / 3968</td>'),
         ('arrival','Geliş tarihi alanı',None,'<td>21/10/2026</td>'),
         ('pending','Komisyon işlem alanı',None,'<td>Komisyonda</td>'),
         ('signer','İlk imza tablosunda Gökhan Günaydın',None,'G&#xF6;khan G&#xDC;NAYDIN'),
     ]),
    ('agenda.html','agenda','TBMM Gelen Kâğıtlar 15, 21 Ekim 2026','2026-10-21','2026-10-21','TBMM','official',
     'https://www.tbmm.gov.tr/Gundem/GelenKagitDetay/cfa20ad1-6674-4173-bef3-01a15e29ddef',
     '6bcabebc8a39717ec5fa58e773c977f65404baa0db2863157087def66deb18f1',[
         ('id','Milletvekili tekliflerinin sekizinci sırasında 2/3968',None,'Kanun Teklifi (2/3968) (Plan ve B&uuml;t&ccedil;e Komisyonuna)'),
     ]),
    ('press.html','press','TBMM, Gökhan Günaydın’ın 21 Ekim basın toplantısı','2026-10-21','2026-10-21','TBMM','official',
     'https://tbmm.gov.tr/Haber/Detay?Id=a091bf62-bdd5-4e19-a116-01a15ed9ff7a',
     '0bf84136831f043e79d734b31a88aa25f58471f576de7fb48fd0d5a3c5d40375',[
         ('date','TBMM haberinin 21 Ekim tarihi',None,'2026-10-21 - 17:25'),
         ('scope','TBMM haberinde Günaydın’ın teklif açıklaması',None,'Bu görevlerde bulunan insanların ayrıldıktan sonra maaş alamamaları için kanun teklifi verdiklerini belirten Günaydın'),
     ]),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0404-kamu-3968-'+key
    vid=doc+'-v1'
    obj=f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable=f'objects/{digest}/readable.html'
    store(obj,raw)
    store(readable,readable_bytes(raw,'pdf' if pdf else 'html',legacy=False))
    add('document',id=doc,party_id='yeni-parti',title=title,source_kind=kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,
        date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Dinamik kayıt ilk yayın gününü belirtmiyor.',
        version_label='Özgün kurum veya parti nüshası.',accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='application/pdf' if pdf else 'text/html',sha256=digest,original_path=obj,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author=None,kind='official' if kind=='official' else 'party_publication',
        published_at=published,date_precision='day' if published else 'unknown',social_handle=None,public_url=url,
        basis='Özgün üst başlık ve varsa gün, parti, ilk imza ve kurum bağlamı birlikte okundu.')
    if not pdf:
        view=build_view(raw,url,root,fetch_assets=False)
        view['version_id']=vid
        validate_view(root,view)
        manifest=root/view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
        add('archive_view',**view)
    for suffix,section,index,exact in anchors:
        text=pdf_page_text(root/obj,index) if pdf else html_source_text(raw)
        if pdf:
            assert not text.strip(), (key,suffix)
        else:
            assert exact in text,(key,suffix)
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,
            article=None,section=section,pdf_page_index=index,printed_page=None)
        if pdf:
            add('manual_passage',passage_id=doc+'-'+suffix,checked_at=now,method='Özgün tarama sayfası Poppler ile görüntülendi.',
                reason='Metin katmanı boş. Sayfadaki kısa ifade gözle doğrulandı.')
(checks/'kamu-3968-source-records.json').write_text(json.dumps(dict(party_id='yeni-parti',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'package-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
