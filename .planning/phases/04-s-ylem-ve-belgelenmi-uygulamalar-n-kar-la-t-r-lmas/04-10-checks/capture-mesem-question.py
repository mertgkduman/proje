import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');now=datetime.now(timezone.utc).isoformat(timespec='seconds');entries=[]
cases=[("8231","4677985e-607a-43ff-8519-018cfc88bb5e","2024-01-11","D28/Y2/T7/WebOnergeMetni/66e2b4ab-032d-4ebc-8d69-dd7f17593811.pdf","D28/Y2/T7/WebOnergeMetni/65e46966-b062-4275-9449-cac49e80d23c.pdf")]
def add(k,**v):entries.append(dict(kind=k,values=v))
for num,guid,day,qpath,apath in cases:
 sources=[('register','html',Path('/tmp/gsd0410-'+num+'-detail.html'),'https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/'+guid),('question','pdf',Path('/tmp/gsd0410-'+num+'-question.pdf'),'https://cdn.tbmm.gov.tr/KKBSPublicFile/'+qpath),('answer','pdf',Path('/tmp/gsd0410-'+num+'-answer.pdf'),'https://cdn.tbmm.gov.tr/KKBSPublicFile/'+apath)]
 for role,typ,capture,url in sources:
  raw=capture.read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);original='original.html.bin' if typ=='html' else 'original.pdf';ident='0410-emep-question-'+num+'-'+role
  for name,content in [(original,raw),('readable.html',readable_bytes(raw,typ,legacy=False))]:
   path=obj/name
   if path.exists():assert path.read_bytes()==content
   else:path.write_bytes(content)
  add('document',id=ident,party_id='emep',title='TBMM 7/'+num+' '+{'register':'kayıt','question':'yazılı soru','answer':'bakanlık yanıtı'}[role],source_kind='official')
  add('document_version',id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date=day if role=='question' else None,version_label='TBMM imzalı soru PDF taraması, görsel okuma' if role=='question' else ('TBMM kayıt ekranı' if role=='register' else 'Bakanlık yanıtı; geliş tarihi kayıt ekranında'),accessed_at=now,verified_at=now,mime='text/html' if typ=='html' else 'application/pdf',sha256=sha,original_path='objects/'+sha+'/'+original,readable_path='objects/'+sha+'/readable.html',date_precision='day' if role=='question' else 'unknown',date_unknown_reason=None if role=='question' else 'Kayıt ekranı veya yanıtın kesin yayım günü doğrulanmadı.')
  if typ=='html':
   view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view);add('archive_view',**view);exact='7 / '+num;assert exact in html_source_text(raw);add('passage',id=ident+'-number-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Soru esas numarası',pdf_page_index=None,printed_page=None)
  if role=='answer' and num in ('4186','13296'):
   exact='2023-2024 eğitim-öğretim yılında 6 Şubat 2023 tarihinde gerçekleşen Kahramanmaraş' if num=='4186' else 'okulda 158.416 öğrenciye, 2023-2024 eğitim öğretim yılında ise 836 okulda 118.778 öğrenciye';assert exact in pdf_page_text(capture,1);add('passage',id=ident+'-context-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Bakanlığın okul beslenmesi bağlamı',pdf_page_index=1,printed_page=None)
  author=None if role=='register' else ('Sevda Karaca' if role=='question' else 'Millî Eğitim Bakanlığı')
  add('source_attribution',version_id=ident+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=author,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM resmî kayıt, imzalı soru veya ilgili bakanlığın yanıtı; soru ve yanıt ayrı belge ve tarihleri ayrıdır.')
  print(num,role,sha)
out=Path(__file__).parent/'mesem-question-source-draft.json';assert not out.exists();out.write_text(json.dumps(dict(status='draft_unvalidated',entries=entries,note='7/8231 bir sayfa soru ve üç sayfa bakanlık yanıtı özgün taramalardan görsel okundu; sahte metin pasajı eklenmedi.'),ensure_ascii=False,indent=2)+'\n')
