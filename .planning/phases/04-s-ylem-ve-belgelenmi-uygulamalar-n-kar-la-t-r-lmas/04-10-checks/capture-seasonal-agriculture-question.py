import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');now=datetime.now(timezone.utc).isoformat(timespec='seconds');entries=[]
sources=[('register','html','/tmp/gsd0410-733034-detail.html','https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/d41d3db3-02de-4b5b-86bb-0198f00c244e'),('question','pdf','/tmp/gsd0410-733034-question.pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/058afe31-ead6-463c-8111-a24333dcc65d.pdf'),('answer','pdf','/tmp/gsd0410-733034-answer.pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/180ca1da-046a-4ade-8f16-071a708160fb.pdf')]
def add(k,**v):entries.append(dict(kind=k,values=v))
for role,typ,path,url in sources:
 raw=Path(path).read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);original='original.html.bin' if typ=='html' else 'original.pdf';ident='0410-emep-question-33034-'+role
 for name,content in [(original,raw),('readable.html',readable_bytes(raw,typ,legacy=False))]:
  dest=obj/name
  if dest.exists():assert dest.read_bytes()==content
  else:dest.write_bytes(content)
 add('document',id=ident,party_id='emep',title='TBMM 7/33034 '+{'register':'kayıt','question':'yazılı soru','answer':'bakanlık yanıtı'}[role],source_kind='official')
 add('document_version',id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date='2025-08-27' if role=='question' else None,version_label={'register':'TBMM kayıt ekranı','question':'TBMM yazılı soru PDF metin katmanı okundu','answer':'Bakanlık yanıtı; görsel okuma bekliyor'}[role],accessed_at=now,verified_at=now,mime='text/html' if typ=='html' else 'application/pdf',sha256=sha,original_path='objects/'+sha+'/'+original,readable_path='objects/'+sha+'/readable.html',date_precision='day' if role=='question' else 'unknown',date_unknown_reason=None if role=='question' else 'Ekran veya yanıtın kesin yayımlanma tarihi doğrulanmadı.')
 if typ=='html':
  view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view)
  add('archive_view',**view);exact='7 / 33034';assert exact in html_source_text(raw)
  add('passage',id=ident+'-number-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Soru esas numarası',pdf_page_index=None,printed_page=None)
 if role=='question':
  exact='Oysa ki 27 Nisan 2024’te yayımlanan Cumhurbaşkanlığı Genelgesi, mevsimlik tarım\nişçilerinin barınma ve altyapı sorunlarının devlet eliyle çözülmesini';assert exact in pdf_page_text(Path(path),0)
  add('passage',id=ident+'-context-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Sorunun barınma ve altyapı bağlamı',pdf_page_index=0,printed_page=None)
 add('source_attribution',version_id=ident+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM resmî kaydı, yazılı soru ve yanıt ayrı özgün belgelerdir; yayımlanma tarihi çıkarılmadı.')
 print(role,sha)
out=Path(__file__).parent/'seasonal-agriculture-question-source-draft.json'
with out.open('x') as f:json.dump(dict(status='source_read_partial',entries=entries,note='Kayıt İskender Bayhan, 27 Ağustos 2025 soru ve 29 Haziran 2026 yanıt bildirimi gösteriyor. Soru PDF OCR metin katmanında soyadı BAYMAN çıktığı için kimlik kaydı asıl TBMM ekranından alınır; imza görseli henüz doğrulanmadı. Yanıt PDF metin katmanı boş ve görsel okuması açık. Sorudaki iddialar kesin olgu kabul edilmez.'),f,ensure_ascii=False,indent=2);f.write('\n')
