import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes,pdf_page_text
from arsiv_gorunum import build_view,validate_view
D=Path(__file__).parent;root=Path('data/practices/sources/emep');now=datetime.now(timezone.utc).isoformat(timespec='seconds')
u='https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y1/T7/WebOnergeMetni/'
sources=[('detail','html','https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/34e45a42-a0b2-4b9f-9123-01895862860a',None,None),('question','pdf',u+'7898951f-aab6-4754-88e5-d7e56dbe8c94.pdf','2023-07-14','İskender Bayhan'),('answer','pdf',u+'e79b5aac-fd3d-4f6b-8dbb-264cee0147b2.pdf',None,'İçişleri Bakanlığı')]
entries=[]
for role,typ,url,date,author in sources:
 raw=(D/('migration-2134-'+role+'.'+typ)).read_bytes();digest=hashlib.sha256(raw).hexdigest();obj=root/'objects'/digest;obj.mkdir(parents=True,exist_ok=True);original='original.html.bin' if typ=='html' else 'original.pdf'
 for name,content in [(original,raw),('readable.html',readable_bytes(raw,typ,legacy=False))]:
  path=obj/name
  if path.exists():assert path.read_bytes()==content
  else:path.write_bytes(content)
 doc='0410-emep-migration-2134-'+role;version=doc+'-v1'
 entries.append(dict(kind='document',values=dict(id=doc,party_id='emep',title='TBMM yabancı uyruklular yazılı sorusu '+role,source_kind='official')))
 entries.append(dict(kind='document_version',values=dict(id=version,document_id=doc,original_url=url,final_url=url,document_date=date,date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Belgenin kendi düzenleme günü doğrulanmadı.',version_label='TBMM özgün kaydı',accessed_at=now,verified_at=now,mime='text/html' if typ=='html' else 'application/pdf',sha256=digest,original_path='objects/'+digest+'/'+original,readable_path='objects/'+digest+'/readable.html')))
 if typ=='html':
  view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);entries.append(dict(kind='archive_view',values=view))
  for key,exact in [('number','7 / 2134'),('date','14.07.2023'),('reply','07.11.2023'),('owner','&#x130;skender BAYHAN'),('topic','&#xDC;lkemizdeki yabanc&#x131; uyruklu ki&#x15F;ilere ili&#x15F;kin')]:
   assert exact in html_source_text(raw)
   entries.append(dict(kind='passage',values=dict(id=doc+'-'+key+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Soru ve yanıt bildirimi',pdf_page_index=None,printed_page=None)))
 entries.append(dict(kind='source_attribution',values=dict(version_id=version,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=author,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM özgün kaydı; soru ve yanıt taranmış sayfaları görsel olarak okundu.')))
 print(role,digest)
raw=(D/"migration-2134-party-policy.html").read_bytes();url="https://www.emep.org/goc-izleme-raporu";digest=hashlib.sha256(raw).hexdigest();obj=root/"objects"/digest;obj.mkdir(parents=True,exist_ok=True)
for name,content in [("original.html.bin",raw),("readable.html",readable_bytes(raw,"html",legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
doc="0410-emep-migration-2022-policy";version=doc+"-v1";exact="İdari gözetim ve geri gönderme merkezleri yerine göç, iltica ve kabul merkezleri açılmalıdır.";assert exact in html_source_text(raw)
entries.append(dict(kind="document",values=dict(id=doc,party_id="emep",title="Emek Partisi Göç İzleme Raporu",source_kind="party")))
entries.append(dict(kind="document_version",values=dict(id=version,document_id=doc,original_url=url,final_url=url,document_date="2022-06-20",date_precision="day",date_unknown_reason=None,version_label="Parti yayını",accessed_at=now,verified_at=now,mime="text/html",sha256=digest,original_path="objects/"+digest+"/original.html.bin",readable_path="objects/"+digest+"/readable.html")))
view=build_view(raw,url,root,fetch_assets=False,http_charset="utf-8");view["version_id"]=version;validate_view(root,view);entries.append(dict(kind="archive_view",values=view))
entries.append(dict(kind="passage",values=dict(id=doc+"-p",version_id=version,exact=exact,prefix=None,suffix=None,article=None,section="Geri gönderme merkezleri ve iltica",pdf_page_index=None,printed_page=None)))
entries.append(dict(kind="source_attribution",values=dict(version_id=version,kind="party",publisher="Emek Partisi",author="Emek Partisi Genel Merkezi",social_handle=None,published_at="2022-06-20",date_precision="day",public_url=url,basis="Parti yayınında tarih ve Genel Merkez imzası.")))
print("policy",digest,view["view_id"])
with (D/'migration-2134-source-draft.json').open('x') as f:json.dump(dict(status='source_read_package_pending',entries=entries,note='Bayhanın soru ve bakanlık yanıtı farklı iddialar içerir; mevcut koşullara otomatik genellenmez.'),f,ensure_ascii=False,indent=2);f.write('\n')
