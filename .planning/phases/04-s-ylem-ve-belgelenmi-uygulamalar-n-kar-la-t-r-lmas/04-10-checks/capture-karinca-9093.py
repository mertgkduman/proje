import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes,pdf_page_text
from arsiv_gorunum import build_view,validate_view
D=Path(__file__).parent;root=Path('data/practices/sources/emep');now=datetime.now(timezone.utc).isoformat(timespec='seconds')
u='https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y2/T7/WebOnergeMetni/'
sources=[('detail','html','https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/fa07b567-6f5a-45d2-8da7-018d6a10b9d0',None,None),('question','pdf',u+'8ed1061c-7cf7-4267-85c1-1b79e68ef42e.pdf','2024-02-02','İskender Bayhan'),('answer','pdf',u+'ab77b90b-56dc-48db-97c2-49704d910ea0.pdf',None,'Çalışma ve Sosyal Güvenlik Bakanlığı')]
entries=[]
for role,typ,url,date,author in sources:
 raw=(D/('karinca-9093-'+role+'.'+typ)).read_bytes();digest=hashlib.sha256(raw).hexdigest();obj=root/'objects'/digest;obj.mkdir(parents=True,exist_ok=True);original='original.html.bin' if typ=='html' else 'original.pdf'
 for name,content in [(original,raw),('readable.html',readable_bytes(raw,typ,legacy=False))]:
  path=obj/name
  if path.exists():assert path.read_bytes()==content
  else:path.write_bytes(content)
 doc='0410-emep-karinca-9093-'+role;version=doc+'-v1'
 entries.append(dict(kind='document',values=dict(id=doc,party_id='emep',title='TBMM işkolu yazılı sorusu '+role,source_kind='official')))
 entries.append(dict(kind='document_version',values=dict(id=version,document_id=doc,original_url=url,final_url=url,document_date=date,date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Belgenin kendi düzenleme günü doğrulanmadı.',version_label='TBMM özgün kaydı',accessed_at=now,verified_at=now,mime='text/html' if typ=='html' else 'application/pdf',sha256=digest,original_path='objects/'+digest+'/'+original,readable_path='objects/'+digest+'/readable.html')))
 if typ=='html':
  view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);entries.append(dict(kind='archive_view',values=view))
  for key,exact in [('number','7 / 9093'),('date','02.02.2024'),('reply','07.11.2024'),('owner','&#x130;skender BAYHAN'),('topic','&#x130;&#x15F; kolu de&#x11F;i&#x15F;ikliklerinin sendikala&#x15F;ma s&#xFC;re&#xE7;lerine etkisine ili&#x15F;kin')]:
   assert exact in html_source_text(raw)
   entries.append(dict(kind='passage',values=dict(id=doc+'-'+key+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Soru ve yanıt bildirimi',pdf_page_index=None,printed_page=None)))
 entries.append(dict(kind='source_attribution',values=dict(version_id=version,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=author,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM özgün kaydı; soru ve yanıt taranmış sayfaları görsel olarak okundu.')))
 print(role,digest)
with (D/'karinca-9093-source-draft.json').open('x') as f:json.dump(dict(status='source_read_package_pending',entries=entries,note='Soru ve yanıt işkolu değişikliğine farklı gerekçeler verir; yanıt anındaki dava sonraki sonuç değildir.'),f,ensure_ascii=False,indent=2);f.write('\n')
