"""Bind the second 3 November agenda record to 10/4961 and dated KAP notices."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

party, checks, stage, path_list = sys.argv[1:]
checks,stage,path_list=map(Path,(checks,stage,path_list))
assert party in ('iyi','yeni-yol')
root=Path('data/practices/sources')/party
number='0407' if party=='iyi' else '0408'
prefix=number+'-nov03-4961-'
existing=number+'-nov03-genelgorusme-'
now=datetime.now(timezone.utc).isoformat()
rows=[]
paths=set()
sources=(
    ('register','nov03-10-4961-detail.html','html',
     'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/e60bf69c-b039-4d55-895f-01a1a6e214e5',
     '10/4961 araştırma önergesi esas kaydı','TBMM',None,'2026-11-03',
     '7776c08b485557b9ee33b6bc95c3d661bf0b0cb9f1a3c157b2daf5370273abf9'),
    ('signed','nov03-10-4961.pdf','pdf',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T10/WebOnergeMetni/7c72b7a0-bb49-404b-a402-d6e82f3651b7.pdf',
     '10/4961 araştırma önergesinin imzalı metni','TBMM','Turhan Çömez','2026-11-03',
     'cb666b0c83888dbe5418ef370a61361d4a0081c2e029a3439c0e6d3d81c17606'),
    ('tursg','kap-1689204.pdf','pdf','https://kap.org.tr/tr/api/BildirimPdf/1689204',
     'Türkiye Sigorta karşılıklar ve finansal tablo takvimi, 30 Ekim','Türkiye Sigorta A.Ş.',None,'2026-10-30',
     '0508d9165419bbe0c1c5644fd944a17953d4f87ba96d14313f6e5ce3dacd40b2'),
    ('deadline','kap-1689187.pdf','pdf','https://kap.org.tr/tr/api/BildirimPdf/1689187',
     'KAP, Türkiye Sigorta ek süre duyurusu, 30 Ekim','Kamuyu Aydınlatma Platformu',None,'2026-10-30',
     '013626d34b236614d5182ed6a911d155ca143b64d9155acf8fc03f5f76f45c59'),
)

def add(table,**row):
    rows.append(dict(kind=table,values=row))

def keep(rel,raw):
    path=root/rel
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes()==raw
    else:
        path.write_bytes(raw)
    paths.add(str(path))
    return path

def passage(key,vid,heading,exact,index=None):
    add('passage',id=prefix+key,version_id=vid,exact=exact,prefix=None,suffix=None,
        article=None,section=heading,pdf_page_index=index,printed_page=None)

floor_raw=(stage/'nov03.html').read_bytes()
assert sha256(floor_raw).hexdigest()=='43f76c014493808d974aed00ce23152667132f1862f387bde6f788524a17357b'
floor=html_source_text(floor_raw)
call='Meclis araştırma önergesinin diğer önergelerin önüne alınarak görüşmelerin 3/11/2026 Salı günkü birleşimde yapılması önerilmiştir.'
owner='İYİ PARTİ GRUBU ADINA TURHAN ÇÖMEZ (Balıkesir)'
vote='BAŞKAN - Öneriyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Kabul edilmemiştir.'
speaker=owner if party=='iyi' else 'YENİ YOL GRUBU ADINA SELÇUK ÖZDAĞ (Muğla)'
position=('Eğer bizim verdiğimiz önergeye "evet" derseniz' if party=='iyi' else
          'O nedenle ben diyorum ki araştırma önergesine "evet" oyu vereceğiz')
start=floor.index(owner)
stop=floor.index('Cumhuriyet Halk Partisi Grubunun İç Tüzük',start)
assert floor.rfind(call,0,start)>start-5000
assert all(start<=floor.index(value,start)<stop for value in (speaker,position,vote))
for key,heading,quote in (
    ('floor-call','Çömez’in ayrı Meclis araştırması gündem önerisi',call),
    ('floor-role','Grup adına konuşma yetkisi',speaker),
    ('floor-position','Görüşmedeki grup katkısı',position),
    ('floor-vote','İkinci grup gündem önerisinin reddi',vote),
):
    passage(key,existing+'floor-v1',heading,quote)

for label,name,fmt,url,title,publisher,author,day,digest in sources:
    path=stage/name
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    doc=prefix+label
    vid=doc+'-v1'
    folder=Path('objects')/digest
    original=folder/('original.pdf' if fmt=='pdf' else 'original.html.bin')
    readable=folder/'readable.html'
    local=keep(original,raw)
    keep(readable,readable_bytes(raw,fmt,legacy=False))
    add('document',id=doc,party_id=party,title=title,source_kind='official')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,
        date_precision='day',date_unknown_reason=None,version_label='Kurumun özgün nüshası.',
        accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='application/pdf' if fmt=='pdf' else 'text/html',
        sha256=digest,original_path=str(original),readable_path=str(readable))
    add('source_attribution',version_id=vid,publisher=publisher,author=author,kind='official',
        published_at=day if label in ('tursg','deadline') else None,
        date_precision='day' if label in ('tursg','deadline') else 'unknown',social_handle=None,
        public_url=url,basis='TBMM esas dosyası veya KAP’ta yayımlanan özgün kurum açıklaması.')
    if fmt=='html':
        for key,title,quote in (
            ('number','Esas numarası','10 / 4961'),
            ('date','TBMM başkanlığına geliş tarihi','03/11/2026'),
            ('status','Esas dosyasında erişilen durum','G&#xFC;ndemde'),
        ):
            assert quote in html_source_text(raw),(key,quote)
            passage(label+'-'+key,vid,title,quote)
        view=build_view(raw,url,root,fetch_assets=False)
        view['version_id']=vid
        validate_view(root,view)
        add('archive_view',**view)
        manifest=root/view['manifest_path']
        paths.add(str(manifest))
        paths.update(str(manifest.parent/name) for name in json.loads(manifest.read_bytes())['files'])
    elif label=='signed':
        assert pdf_page_text(local,0).strip()=='10/4961'
        passage('signed-number',vid,'İmzalı önergenin doğal esas numarası','10/4961',0)
        for key,index,title,quote in (
            ('scope',1,'Araştırma gerekçesinde iki şirket','Türkiye Sigorta ile Türkiye Hayat ve Emeklilik, TVF portföyündeki şirketlerdir.'),
            ('protection',2,'Sigortalı ve katılımcı haklarıyla ilgili gerekçe','Sigorta yükümlülüklerinin yerine getirilmesi ve katılımcı haklarının'),
        ):
            assert not pdf_page_text(local,index).strip()
            passage(label+'-'+key,vid,title,quote,index)
            add('manual_passage',passage_id=prefix+label+'-'+key,checked_at=now,
                method='Üç özgün sayfa Poppler ile görsel okundu.',
                reason='Pasaj, sayfanın tarama görüntüsünde doğrulandı.')
    else:
        refs = (
            ('total',2,'30 Eylül taslak tablosundaki toplam karşılık',"16.339.546.449 TL'dir."),
            ('additional',2,'Ek karşılığın vergi öncesi tutarı','15.631.728.459'),
            ('previous',2,'Eylül öncesi karşılık','707.817.990 TL'),
            ('net',2,'Vergi sonrası gider etkisi','10.942.209.921'),
            ('category',2,'Şirket açıklamasında karşılıkların kalemleri','borçlanma araçları ile ödünç menkul'),
        ) if label=='tursg' else (
            ('decision',1,'KAP SPK ek süre duyurusu','16.11.2026 (dahil) tarihine kadar.'),
        )
        for key,page,title,quote in refs:
            assert quote in pdf_page_text(local,page),(label,key,quote)
            passage(label+'-'+key,vid,title,quote,page)
with (checks/'nov03-4961-source-records.json').open('x') as stream:
    stream.write(json.dumps(dict(party_id=party,entries=rows),ensure_ascii=False,indent=2)+'\n')
path_list.write_text('\n'.join(sorted(paths))+'\n')
print(party,len(rows),len(paths))
