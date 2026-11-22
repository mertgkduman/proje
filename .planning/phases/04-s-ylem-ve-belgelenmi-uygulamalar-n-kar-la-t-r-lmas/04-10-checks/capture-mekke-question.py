import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');now=datetime.now(timezone.utc).isoformat(timespec='seconds');entries=[]
def add(k,**v):entries.append(dict(kind=k,values=v))
for typ,capture,url,ident in [('html',Path('/tmp/gsd0410-mekke-question.html'),'https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/05477d87-3d9b-42d9-a104-01a03923ed8f','0410-emep-mekke-748173-register'),('pdf',Path('/tmp/gsd0410-mekke-question.pdf'),'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T7/WebOnergeMetni/15574087-5b0b-4d68-aee6-03a2d2d4a674.pdf','0410-emep-mekke-748173-pdf')]:
 raw=capture.read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);original='original.html.bin' if typ=='html' else 'original.pdf'
 for name,content in [(original,raw),('readable.html',readable_bytes(raw,typ,legacy=False))]:
  path=obj/name
  if path.exists():assert path.read_bytes()==content
  else:path.write_bytes(content)
 add('document',id=ident,party_id='emep',title='TBMM 7/48173 Mekke Anlaşması yazılı soru '+('kaydı' if typ=='html' else 'metni'),source_kind='official')
 add('document_version',id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date=None if typ=='html' else '2026-08-24',version_label='TBMM kayıt ekranı' if typ=='html' else '24 Ağustos 2026 tarihli milletvekili sorusu',accessed_at=now,verified_at=now,mime='text/html' if typ=='html' else 'application/pdf',sha256=sha,original_path='objects/'+sha+'/'+original,readable_path='objects/'+sha+'/readable.html',date_precision='unknown' if typ=='html' else 'day',date_unknown_reason='Kayıt ekranı yayın tarihi bilinmiyor.' if typ=='html' else None)
 if typ=='html':
  view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view);add('archive_view',**view);values=[('number','7 / 48173',None),('date','24.08.2026',None),('owner','&#x130;skender BAYHAN',None)]
 else:values=[('criticism','taahhütlerine uzanan bu kapsamlı iş birliğinin, bölge ve dünya halklarmm güvenliğine\nkazandıracağı hiçbir şey yoktur.',0)]
 for suffix,exact,page in values:
  actual=html_source_text(raw) if page is None else pdf_page_text(capture,page);assert exact in actual,(suffix,exact)
  add('passage',id=ident+'-'+suffix+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='TBMM soru kaydı' if typ=='html' else 'Bayhan’ın anlaşmaya ilişkin değerlendirmesi',pdf_page_index=page,printed_page=None)
 add('source_attribution',version_id=ident+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None if typ=='html' else 'İskender Bayhan',social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM kayıt ve milletvekilinin 24 Ağustos tarihli yazılı sorusu; açıklama ilgili milletvekiline aittir.')
 print(typ,sha)
out=Path(__file__).parent/'mekke-question-source-draft.json';assert not out.exists();out.write_text(json.dumps(dict(status='draft_unvalidated',entries=entries,note='24 Ağustos sorusu 5 Kasım açık oylamasından ayrı işlem; Bayhan görüşü kişiye atfedilir. Ekrandaki cevapsızlık duyurusunun tarihi bilinmez.'),ensure_ascii=False,indent=2)+'\n')
