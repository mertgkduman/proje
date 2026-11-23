import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes,pdf_page_text
from arsiv_gorunum import build_view,validate_view
D=Path(__file__).parent;root=Path('data/practices/sources/emep');now=datetime.now(timezone.utc).isoformat(timespec='seconds')
u='https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y2/T7/WebOnergeMetni/'
sources=[('detail','html','https://www.tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/5039543c-5745-4643-89a9-018f86c1588b',None,None),('question','pdf',u+'63f4163a-4012-4898-8e22-8051e41006d7.pdf','2024-05-17','Sevda Karaca Demir'),('answer','pdf',u+'15a2275e-ab51-453d-8309-60235c53f8b7.pdf',None,'Adalet Bakanlığı')]
entries=[]
for role,typ,url,date,author in sources:
 raw=(D/('earthquake-11963-'+role+'.'+typ)).read_bytes();digest=hashlib.sha256(raw).hexdigest();obj=root/'objects'/digest;obj.mkdir(parents=True,exist_ok=True);original='original.html.bin' if typ=='html' else 'original.pdf'
 for name,content in [(original,raw),('readable.html',readable_bytes(raw,typ,legacy=False))]:
  path=obj/name
  if path.exists():assert path.read_bytes()==content
  else:path.write_bytes(content)
 doc='0410-emep-earthquake-11963-'+role;version=doc+'-v1'
 entries.append(dict(kind='document',values=dict(id=doc,party_id='emep',title='TBMM hasar tespit itirazları '+role,source_kind='official')))
 entries.append(dict(kind='document_version',values=dict(id=version,document_id=doc,original_url=url,final_url=url,document_date=date,date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Belgenin kendi düzenleme günü doğrulanmadı.',version_label='TBMM özgün kaydı',accessed_at=now,verified_at=now,mime='text/html' if typ=='html' else 'application/pdf',sha256=digest,original_path='objects/'+digest+'/'+original,readable_path='objects/'+digest+'/readable.html')))
 if typ=='html':
  view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);entries.append(dict(kind='archive_view',values=view))
  for key,exact in [('number','7 / 11963'),('date','17.05.2024'),('reply','15.08.2024'),('owner','Sevda KARACA DEM&#x130;R'),('topic','6 &#x15E;ubat 2023 tarihli depremler sonras&#x131;nda a&#xE7;&#x131;lan hasar tespitine itiraz davalar&#x131;na ili&#x15F;kin')]:
   assert exact in html_source_text(raw)
   entries.append(dict(kind='passage',values=dict(id=doc+'-'+key+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Soru ve yanıt bildirimi',pdf_page_index=None,printed_page=None)))
 if role=='answer':
  exact='idare mahkemelerinde afet işleri talepli açılan ve'
  assert exact in pdf_page_text(obj/original,1)
  entries.append(dict(kind='passage',values=dict(id=doc+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Adalet Bakanlığı yanıtı',pdf_page_index=1,printed_page=None)))
 entries.append(dict(kind='source_attribution',values=dict(version_id=version,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=author,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM özgün kaydı; soru iki taranmış sayfası görsel, yanıt metni okundu; tarih farkı korunur.')))
 print(role,digest)
with (D/'earthquake-11963-source-draft.json').open('x') as f:json.dump(dict(status='source_read_package_pending',entries=entries,note='TBMM özeti 6 Şubat 2023 derken soru ve cevapta 2024 yazılı; sayı ve bağlam farkı çözülmeden aynen atfedilir.'),f,ensure_ascii=False,indent=2);f.write('\n')
