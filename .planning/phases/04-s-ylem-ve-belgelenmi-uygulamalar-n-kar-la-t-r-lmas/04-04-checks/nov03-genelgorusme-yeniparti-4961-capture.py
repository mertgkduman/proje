from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json,sys
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/yeni-parti'); stage=Path('/tmp/gsd0408-nov03.LiHmMI');checks=Path(__file__).parent
prefix='0404-nov03-genelgorusme-yeniparti-4961-';now=datetime.now(timezone.utc).isoformat(); rows=[]; paths=[]
def add(table,**values): rows.append(dict(kind=table,values=values))
def keep(path,data):
 p=root/path;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists(): assert p.read_bytes()==data
 else: p.write_bytes(data)
 paths.append(str(p))
sources=[('register','nov03-10-4961-detail.html','html','https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/e60bf69c-b039-4d55-895f-01a1a6e214e5','7776c08b485557b9ee33b6bc95c3d661bf0b0cb9f1a3c157b2daf5370273abf9'),('signed','nov03-10-4961.pdf','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T10/WebOnergeMetni/7c72b7a0-bb49-404b-a402-d6e82f3651b7.pdf','cb666b0c83888dbe5418ef370a61361d4a0081c2e029a3439c0e6d3d81c17606')]
for label,name,fmt,url,digest in sources:
 p=stage/name;raw=p.read_bytes();assert sha256(raw).hexdigest()==digest
 doc=prefix+label;vid=doc+'-v1';obj=Path('objects')/digest;original=obj/('original.html.bin' if fmt=='html' else 'original.pdf');readable=obj/'readable.html'
 keep(original,raw);keep(readable,readable_bytes(raw,fmt,legacy=False))
 add('document',id=doc,party_id='yeni-parti',title='10/4961 araştırma önergesi '+('TBMM sicili' if label=='register' else 'imzalı metni'),source_kind='official')
 add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date='2026-11-03',date_precision='day',date_unknown_reason=None,version_label='3 Kasım 2026 tarihli TBMM işlemi.',accessed_at=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,mime='text/html' if fmt=='html' else 'application/pdf',sha256=digest,original_path=str(original),readable_path=str(readable))
 add('source_attribution',version_id=vid,publisher='TBMM',author='Turhan Çömez' if label=='signed' else None,kind='official',published_at=None,date_precision='unknown',social_handle=None,public_url=url,basis='TBMM esas kaydı ve imzalı önerge.')
 def passage(key,section,exact,index=None): add('passage',id=prefix+key,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=index,printed_page=None)
 if fmt=='html':
  body=html_source_text(raw)
  for key,section,quote in [('register-number','Esas numarası','10 / 4961'),('register-date','Başkanlığa geliş tarihi','03/11/2026')]:
   assert quote in body;passage(key,section,quote)
  view=build_view(raw,url,root,fetch_assets=False);view['version_id']=vid;validate_view(root,view);add('archive_view',**view);manifest=root/view['manifest_path'];paths.append(str(manifest));paths.extend(str(manifest.parent/name) for name in json.loads(manifest.read_bytes())['files'])
 else:
  assert pdf_page_text(root/original,0).strip()=='10/4961';assert not pdf_page_text(root/original,1).strip()
  passage('signed-number','Esas numarası','10/4961',0)
  passage('signed-scope','Gerekçede araştırma istemi','araştırmanın yalnızca iki şirketin iç işlemlerini değil, ana hissedar ve TVF düzeyindeki',1)
  add('manual_passage',passage_id=prefix+'signed-scope',checked_at=now,method='Özgün üç sayfa Poppler görüntüsünde görsel okundu.',reason='Gerekçe sayfasında metin katmanı bulunmuyor; pasaj görselden doğrulandı.')
out=checks/'nov03-genelgorusme-yeniparti-4961-source-records.json';out.write_text(json.dumps(dict(party_id='yeni-parti',entries=rows),ensure_ascii=False,indent=2)+'\n');(checks/'nov03-genelgorusme-yeniparti-4961-paths.txt').write_text('\n'.join(sorted(paths))+'\n');print('4961_SOURCE_CAPTURE',len(rows),len(paths))
