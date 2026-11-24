from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
here=Path(__file__).resolve().parent;root=Path('data/practices/sources/saadet');now=datetime.now(timezone.utc).isoformat();entries=[];paths=set()
def add(table,**row): entries.append({'kind':table,'values':row})
def put(rel,raw):
 p=root/rel;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists(): assert p.read_bytes()==raw
 else: p.write_bytes(raw)
 paths.add(str(p))
sources=[('statement','party-news-bodies/353.json','https://admin.saadet.org.tr/veriler/api.php?resource=haber_detay&kod=liderlerin-ortak-aciklamasi-21082022','2022-08-21','Saadet Partisi','party','party_publication','application/json'),('meeting','six-leaders-2022-10-02-independent-original.html','https://www.indyturk.com/node/559216/haber/6-lider-chp-genel-merkezinde-bulu%C5%9Ftu-g%C3%B6sterece%C4%9Fimiz-ortak-aday-t%C3%BCrkiye%E2%80%99nin-13','2022-10-02','Independent Türkçe','journalism','journalism','text/html')]
for key,name,url,day,publisher,kind,attribution,mime in sources:
 raw=(here/name).read_bytes();h=sha256(raw).hexdigest();doc='0411-six-leaders-2022-'+key;vid=doc+'-v1';original=f'objects/{h}/original.html.bin';readable=f'objects/{h}/readable.html';put(original,raw);put(readable,readable_bytes(raw,'html',legacy=False))
 add('document',id=doc,party_id='saadet',title='Altı liderin 2022 buluşmaları: '+key,source_kind=kind)
 add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day',date_unknown_reason=None,version_label='21 Ağustos 2022 altı lider ortak açıklaması.' if key=='statement' else '2 Ekim 2022 bağımsız toplantı haberi.',accessed_at=datetime.fromtimestamp((here/name).stat().st_mtime,timezone.utc).isoformat(),verified_at=now,mime=mime,sha256=h,original_path=original,readable_path=readable)
 add('source_attribution',version_id=vid,publisher=publisher,author=None,kind=attribution,published_at=None if key=='statement' else day,date_precision='unknown' if key=='statement' else 'day',social_handle=None,public_url=url,basis='Altı lider ortak metninin Saadet yayını; API zaman damgası UTC 21.00 ve tarihli metin ayrıdır.' if key=='statement' else 'Independent Türkçe / ANKA imzalı 2 Ekim tarihli haber.')
 view=build_view(raw,url,root,fetch_assets=False);view['version_id']=vid;validate_view(root,view);add('archive_view',**view);m=root/view['manifest_path'];paths.add(str(m));paths.update(str(m.parent/n) for n in json.loads(m.read_bytes())['files']);body=html_source_text(raw)
 anchors={'statement':[('date','Ortak metnin kendi tarihi','(21 Ağustos 2022/ANKARA)'),('host','Saadetin 21 Ağustos toplantısındaki ev sahipliği',"bugün Saadet Partisi'nin ev sahipliğinde gerçekleştirdiğimiz 6. toplantımızla tamamlıyoruz."),('next','2 Ekim toplantısının ilan edilen yeri ve saati','2 Ekim 2022 Pazar günü saat 14.00’da CHP Genel Merkezinde')], 'meeting':[('arrival','Üç parti lideri ve 2 Ekimde CHP merkezine varışları','Uysal’ın ardından sırasıyla saat 13.59’da Saadet Partisi Genel Başkanı Temel Karamollaoğlu, saat 14.02 Gelecek Partisi Ahmet Davutoğlu, saat 14.05’te DEVA Partisi Genel Başkanı Ahmet Babacan ve saat 14.10’da İYİ Parti Genel Başkanı Meral Akşener, CHP Genel Merkezi’ne ulaştı.'),('opening','Görüşmenin fiilî başlangıcı ve yeri',"Saat 14.11’de başlayan görüşmenin CHP Genel Merkezi'nin, Genel Başkanlık katı olan 12. Katta yapıldığı öğrenildi."),('joint','Toplantı sonrası altı lider açıklaması','Toplantının ardından 6 liderin imzasını taşıyan ortak bir bildiri yayımladı.')]}[key]
 for suffix,section,exact in anchors:
  assert exact in body,(key,suffix);add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
(here/'six-leaders-2022-source-records.json').write_text(json.dumps({'party_id':'saadet','entries':entries},ensure_ascii=False,indent=2)+'\n');Path('/tmp/gsd0411-six-leaders-paths').write_text('\n'.join(sorted(paths))+'\n');print('entries',len(entries),'paths',len(paths))
