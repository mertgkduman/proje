"""Preserve four published sources for the Jan–Aug reciprocal visits."""

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
    ('indy','Independent Türkçe',None,'2026-01-28T13:56:40+03:00',
     'Arıkan’ın TBMM basın toplantısı ve karşılıklı ziyaret açıklaması',
     'https://www.indyturk.com/node/771988/siyaset/saadet-partisi-genel-ba%C5%9Fkan%C4%B1-ar%C4%B1kan-2027%E2%80%99de-se%C3%A7imlerin-yap%C4%B1laca%C4%9F%C4%B1n%C4%B1-d%C3%BC%C5%9F%C3%BCn%C3%BCyorum',
     'fe87472139403077a06ac34dee2995a619b8f01bcf7b5a0d487ec13de7e20516',
     (
         ('date','Özgün yayının tarih ve saati','2026-01-28T13:56:40+03:00'),
         ('plan','Arıkan aynı günkü ziyaret planını açıklıyor','Bugün Yeniden Refah Partisi ziyaretimiz olacak.'),
         ('target','Arıkan’ın karşılıklı görüşme hedefi','Yeniden Refah Partisi ile karşılıklı bir ziyaret takvimi yürüyor.'),
         ('position','Yeniden Refah ile iş birliğine ilişkin görüş','Beraber yol yürümeyi arzu ettiğimiz partilerden biridir.'),
     )),
    ('dha','Demirören Haber Ajansı','DHA','2026-01-28T19:55:40+03:00',
     'Arıkan’ın Yeniden Refah Genel Merkezi ziyareti',
     'https://www.dha.com.tr/yerel-haberler/ankara/ankara-saadet-partisi-baskani-arikandan-erb-2807506',
     '40ae0edfbb3e1c6cbadf829089618d062b95905fba758f9d2e058594fd1c2328',
     (
         ('date','DHA yayınının tarih ve saati','2026-01-28T19:55:40+03:00'),
         ('place','Ocak ziyareti yeri ve süresi','basına kapalı gerçekleşen görüşme yaklaşık 1 saat sürdü.'),
         ('press','Görüşme sonrası basın açıklaması','Görüşme sonrası Arıkan ve Erbakan basın açıklaması yaptı.'),
     )),
    ('bun','BUN','Halis Yıldız','2026-08-11T20:01:52+03:00',
     '11 Ağustos’taki Saadet Genel Merkezi toplantısı',
     'https://bun.com.tr/saadet-ile-yeniden-refahtan-secim-is-birligi-gorusmesi/',
     'baff94840bc5a4c5762cb072b14ce5c2eed715b13da393ba578fad406401f060',
     (
         ('occurred','Görüşme günü ve Saadet Genel Merkezi','11 Ağustos 2026’da Saadet Partisi Genel Merkezi’nde bir araya geldi.'),
         ('press','Görüşme sonrası ortak açıklama','iki lider ortak basın açıklaması düzenledi.'),
         ('followup','Temasları sürdürmeye ilişkin açıklama','temasları daha sık sürdürme konusunda görüş birliğine vardıklarını açıkladı.'),
     )),
    ('milligazete','Millî Gazete','Abdullah Kutay Eskalen','2026-08-11T19:57:00+03:00',
     'Arıkan ve Erbakan’ın 11 Ağustos görüşmesi ve açıklamaları',
     'https://www.milligazete.com.tr/arikan-erbakan-ile-bir-araya-geldi-arikan-turkiyenin-onunu-acmak-istiyoruz-erbakan-milletimize-umut-olacak-calismalar-yapacagiz',
     'f8668073992e47910783baa15a788e6ac5f639fffc641251cb59f2e506b9eff6',
     (
         ('date','Özgün yayının tarih ve saati','2026-08-11T19:57:00+03:00'),
         ('place','Saadet Genel Merkezinde kabul','Saadet Partisi Genel Merkezi’nde kabul etti.'),
         ('election','Erbakan’ın sözünü ettiği milletvekili seçimi müzakeresi','Şu an için milletvekili seçimine yönelik bir ittifakın yapılmasıyla ilgili görüşmeler yapıyoruz.'),
         ('president','Ortak cumhurbaşkanı adayı hakkında Erbakan’ın açıklaması','Şu ana kadar ortak cumhurbaşkanı adayı üzerinde herhangi bir görüşmemiz, müzakeremiz olmadı'),
     )),
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

for key,publisher,author,published,title,url,digest,passages in sources:
    path=stage/f'arikan-erbakan-{key}.html'
    raw=path.read_bytes()
    body=html_source_text(raw)
    assert sha256(raw).hexdigest()==digest
    doc=f'0411-arikan-erbakan-{key}'
    vid=doc+'-v1'
    original=Path('objects')/digest/'original.html.bin'
    readable=original.parent/'readable.html'
    archive(original,raw)
    archive(readable,readable_bytes(raw,'html',legacy=False))
    add('document',id=doc,party_id='saadet',title=title,source_kind='journalism')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=published[:10],
        date_precision='day',date_unknown_reason=None,version_label='Yayının erişilen özgün HTML sürümü.',
        accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,
        mime='text/html',sha256=digest,original_path=str(original),readable_path=str(readable))
    add('source_attribution',version_id=vid,publisher=publisher,author=author,kind='journalism',
        published_at=published[:10],date_precision='day',social_handle=None,public_url=url,
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
with (checks/'arikan-erbakan-visits-v2-source-records.json').open('x') as stream:
    stream.write(json.dumps(dict(party_id='saadet',entries=entries),ensure_ascii=False,indent=2)+'\n')
paths_output.write_text('\n'.join(sorted(written))+'\n')
print(len(entries),len(written))
