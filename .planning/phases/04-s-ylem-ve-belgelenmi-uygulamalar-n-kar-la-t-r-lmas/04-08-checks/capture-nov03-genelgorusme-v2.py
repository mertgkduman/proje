"""Bind the 8/153 signed proposal, register, group speakers and agenda result."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

party, checks, stage, path_list = sys.argv[1:]
checks, stage, path_list = map(Path,(checks,stage,path_list))
assert party in ('iyi','yeni-yol')
root = Path('data/practices/sources')/party
prefix = ('0407' if party=='iyi' else '0408')+'-nov03-genelgorusme-'
day = '2026-11-03'
when = datetime.now(timezone.utc).isoformat()
rows = []
paths = set()
sources = (
    ('floor','nov03.html','html',
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/12/Ham/0643059d-54b7-4950-980d-f3f86843df5e.html',
     'TBMM 3 Kasım 2026, 12. Birleşim ham tutanağı','43f76c014493808d974aed00ce23152667132f1862f387bde6f788524a17357b'),
    ('summary','nov03-summary.html','html',
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/12/Ozet/41e1ed7f-5e30-4e5b-b082-12d3b4d130a4.html',
     'TBMM 3 Kasım 2026, 12. Birleşim tutanak özeti','3e71d39fcb0a18b1b1dc726070e2fbd6c70be995bb9dba3e7f27c06905f84751'),
    ('register','nov03-8-153-detail.html','html',
     'https://tbmm.gov.tr/Denetim/Genel-Gorusme-Onergesi-Detay/da5cdaed-c494-42c2-a5c5-01a1a69d2f81',
     '8/153 genel görüşme önergesi esas dosyası','5465005ff75287b0b05b9db025937b2f93b2ae88bc9443972dc41d83bd85d627'),
    ('signed','nov03-8-153.pdf','pdf',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T8/WebOnergeMetni/3623d77f-a15f-48e9-8751-18ca1a5d7c94.pdf',
     '8/153 genel görüşme önergesinin imzalı metni','308e5249344e7e7d2103dc5b96b6289c23697ee5aca0175e3f448b24acc73793'),
)
anchors = {
    'floor': [
        ('call','1. grup önerisi, Ekmen’in ön görüşme talebi','genel görüşme önerimizin diğer önergelerin önüne alınarak görüşmelerin 3/11/2026 Salı günkü birleşimde yapılması önerilmiştir.'),
        ('vote','Gündem önerisinin oylama sonucu','BAŞKAN - Öneriyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Kabul edilmemiştir.'),
    ],
    'summary': [
        ('call','Birleşim özetinde 1. grup işlemi','genel görüşme önergesinin diğer önergelerin önüne alınarak'),
        ('vote','Birleşim özetinde ön görüşme kararı','Görüşmelerinin Genel Kurulun 3 Kasım 2026 Salı günkü birleşiminde yapılmasına ilişkin önerileri yapılan görüşmelerden sonra kabul edilmedi.'),
    ],
    'register': [
        ('number','Esas numarası','8 / 153'),
        ('date','Başkanlığa geliş tarihi','03/11/2026'),
        ('status','Esas dosyasının erişimde görülen durumu','G&#xFC;ndemde'),
    ],
}
if party=='iyi':
    anchors['floor'] += [
        ('role','Hasan Toktaş’ın İYİ Parti Grup sıfatı','İYİ PARTİ GRUBU ADINA HASAN TOKTAŞ (Bursa)'),
        ('position','Hasan Toktaş’ın gündem önerisine desteği','Çok isabetli bulduğumuz bu önergeyi desteklediğimizi şimdiden ifade etmek istiyorum.'),
    ]
else:
    anchors['floor'] += [
        ('role','Sadullah Kısacık’ın Yeni Yol Grup sıfatı','YENİ YOL GRUBU ADINA SADULLAH KISACIK (Adana)'),
        ('position','Sadullah Kısacık’ın yatırımcılara ödeme çağrısı','Bir an önce insanların parasını ödemeyi konuşmalıyız biz burada.'),
        ('transparency','Yatırımcılara bilgi verme çağrısı','insanlar parasını ne zaman ne alacağını bilsin.'),
    ]

def add(table,**row):
    rows.append(dict(kind=table,values=row))

def keep(location,data):
    p = root/location
    p.parent.mkdir(exist_ok=True,parents=True)
    if p.is_file():
        assert p.read_bytes()==data
    else:
        p.write_bytes(data)
    paths.add(str(p))

def passage(key,vid,section,quote,index=None):
    add('passage',id=prefix+key,version_id=vid,exact=quote,prefix=None,suffix=None,
        article=None,section=section,pdf_page_index=index,printed_page=None)

for label,name,fmt,url,title,digest in sources:
    p=stage/name
    raw=p.read_bytes()
    assert sha256(raw).hexdigest()==digest
    doc=prefix+label
    vid=doc+'-v1'
    folder=Path('objects')/digest
    original=folder/('original.html.bin' if fmt=='html' else 'original.pdf')
    readable=folder/'readable.html'
    keep(original,raw)
    keep(readable,readable_bytes(raw,fmt,legacy=False))
    add('document',id=doc,party_id=party,title=title,source_kind='official')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,
        date_precision='day',date_unknown_reason=None,version_label='3 Kasım 2026 tarihli TBMM işlemi.',
        accessed_at=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=when,mime='text/html' if fmt=='html' else 'application/pdf',sha256=digest,
        original_path=str(original),readable_path=str(readable))
    add('source_attribution',version_id=vid,publisher='TBMM',author='Mehmet Emin Ekmen' if label=='signed' else None,
        kind='official',published_at=None,date_precision='unknown',social_handle=None,
        public_url=url,basis='TBMM tutanak arşivi veya imzalı evrakın TBMM esas dosyası.')
    if fmt=='html':
        body=html_source_text(raw)
        for key,section,quote in anchors[label]:
            assert quote in body,(label,key,quote)
            if label=='floor' and key=='vote':
                a=body.index('Mersin Milletvekili ve Grup Başkanı Mehmet Emin Ekmen tarafından')
                b=body.index(quote,a)
                c=body.index('İYİ Parti Grubunun İç Tüzük',b)
                assert a<b<c and c-b<2000
            passage(label+'-'+key,vid,section,quote)
        view=build_view(raw,url,root,fetch_assets=False)
        view['version_id']=vid
        validate_view(root,view)
        add('archive_view',**view)
        manifest=root/view['manifest_path']
        paths.add(str(manifest))
        paths.update(str(manifest.parent/name) for name in json.loads(manifest.read_bytes())['files'])
    else:
        assert pdf_page_text(root/original,0).strip()=='8/153'
        passage('signed-number',vid,'Esas numarası', '8/153',0)
        for key,index,section,quote in [
            ('scope',1,'İmzalı önergenin ekonomik etki gerekçesi','Fon dolandırıcılığının ekonomik ve toplumsal sonuçlarının'),
            ('loss',1,'Gerekçede önerge sahibine ait piyasa kaybı hesabı','173 milyar dolara yükselmiştir.'),
        ]:
            passage('signed-'+key,vid,section,quote,index)
            add('manual_passage',passage_id=prefix+'signed-'+key,checked_at=when,
                method='Özgün tarama iki sayfada Poppler görüntüsünden okundu.',
                reason='Pasaj, PDF’nin metin katmanında bulunmayan taramada görsel olarak doğrulandı.')

out=checks/'nov03-genelgorusme-v2-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps(dict(party_id=party,entries=rows),ensure_ascii=False,indent=2)+'\n')
path_list.write_text('\n'.join(sorted(paths))+'\n')
print(party,len(rows),len(paths))
