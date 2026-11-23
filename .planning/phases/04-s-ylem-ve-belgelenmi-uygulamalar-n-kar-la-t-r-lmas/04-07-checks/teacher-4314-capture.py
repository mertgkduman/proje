from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,sys
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/iyi');stage=Path('/tmp/gsd0411-party010-stage').read_text().strip();stage=Path(stage);here=Path(__file__).parent
prefix='0407-iyi-teacher-4314-';now=datetime.now(timezone.utc).isoformat();rows=[];paths=[]
def add(table,**values):rows.append(dict(kind=table,values=values))
def keep(path,data):
 p=root/path;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==data
 else:p.write_bytes(data)
 paths.append(str(p))
sources=[('floor','teacher-floor-june.html','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/106/Tam/85e331c0-15aa-4e85-97d6-52978dcb79f6.html','345555a33e92cba3e4928bda28122980615d8260b0073ae6ce0135ef1dd20b00'),('register','teacher-4314.html','html','https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/09a2fce3-d544-4465-9b45-019f1c9cbb10','eca60c24cb751aeb20e0b77c1d19035bad52836e8defcd183039bda35fd0a32b'),('signed','teacher-4314.pdf','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T10/WebOnergeMetni/cf90ff9c-881e-4bf1-89c6-77913f32941b.pdf','6002a0aa4088e81a426c92b9391bbf5bcf5a723731454d34f3aa1851d4962241')]
for label,name,fmt,url,digest in sources:
 p=stage/name;raw=p.read_bytes();assert sha256(raw).hexdigest()==digest
 doc=prefix+label;vid=doc+'-v1';obj=Path('objects')/digest;original=obj/('original.html.bin' if fmt=='html' else 'original.pdf');readable=obj/'readable.html';keep(original,raw);keep(readable,readable_bytes(raw,fmt,legacy=False))
 add('document',id=doc,party_id='iyi',title={'floor':'24 Haziran 2026 TBMM 106. Birleşim tam tutanağı','register':'10/4314 TBMM esas sicili','signed':'10/4314 imzalı araştırma önergesi'}[label],source_kind='official')
 add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date='2026-06-24',date_precision='day',date_unknown_reason=None,version_label='24 Haziran 2026 tarihli TBMM işlemi.',accessed_at=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,mime='text/html' if fmt=='html' else 'application/pdf',sha256=digest,original_path=str(original),readable_path=str(readable))
 add('source_attribution',version_id=vid,publisher='TBMM',author='Bülent Kaya' if label=='signed' else None,kind='official',published_at=None,date_precision='unknown',social_handle=None,public_url=url,basis='TBMM tutanağı, esas kaydı veya imzalı önerge.')
 def passage(key,section,exact,index=None):add('passage',id=prefix+key,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=index,printed_page=None)
 if fmt=='html':
  body=html_source_text(raw)
  anchors={'floor':[('proposal','Birinci gündem önerisi','Meclis araştırması önergemizin diğer önergelerin önüne alınarak görüşmelerinin 24/6/2026 Çarşamba günkü birleşimde yapılması önerilmiştir.'),('identity','İYİ Parti grup temsilcisi','BAŞKAN - İYİ Parti Grubu adına Bursa Milletvekili Sayın Yüksel Selçuk Türkoğlu.'),('support','İYİ Parti adına sözlü destek','Önergeyi desteklediğimizi peşinen söylerken'),('result','Birinci gündem önerisinin sonucu','BAŞKAN - Evet, sayın milletvekilleri, öneriyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Kabul edilmemiştir.')],'register':[('register-number','Esas numarası','10 / 4314'),('register-date','Başkanlığa geliş tarihi','24/06/2026')]}
  for key,section,quote in anchors[label]:assert quote in body,(key,quote);passage(key,section,quote)
  if label=='floor':
   a=body.index(anchors[label][0][2]);b=body.index(anchors[label][1][2],a);c=body.index(anchors[label][2][2],b);d=body.index(anchors[label][3][2],c);assert a<b<c<d<body.index('İYİ Parti Grubunun İç Tüzük',d)
  view=build_view(raw,url,root,fetch_assets=False);view['version_id']=vid;validate_view(root,view);add('archive_view',**view);manifest=root/view['manifest_path'];paths.append(str(manifest));paths.extend(str(manifest.parent/name) for name in json.loads(manifest.read_bytes())['files'])
 else:
  assert pdf_page_text(root/original,0).strip()=='10/4314';assert not pdf_page_text(root/original,2).strip()
  passage('signed-number','Esas numarası','10/4314',0);passage('signed-scope','Gerekçedeki araştırma kapsamı','bir atama sisteminin kurulması amacıyla bir Meclis Araştırma Komisyonu kurulması elzemdir.',2)
  add('manual_passage',passage_id=prefix+'signed-scope',checked_at=now,method='Özgün dört sayfa Poppler görüntüsünde görsel okundu.',reason='Gerekçe sayfasında metin katmanı bulunmuyor; pasaj görselden doğrulandı.')
(here/'teacher-4314-source-records.json').write_text(json.dumps(dict(party_id='iyi',entries=rows),ensure_ascii=False,indent=2)+'\n');(here/'teacher-4314-paths.txt').write_text('\n'.join(sorted(paths))+'\n');print('TEACHER_4314_CAPTURE',len(rows),len(paths))
