import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');now=datetime.now(timezone.utc).isoformat(timespec='seconds');entries=[]
def add(k,**v):entries.append(dict(kind=k,values=v))
for typ,capture,url,ident in [('html',Path('/tmp/gsd0410-expression.html'),'https://tbmm.gov.tr/Yasama/KanunTeklifi/22b15f79-4d62-4c4e-8188-019d777c5d4a','0410-emep-expression-23643-register'),('pdf',Path('/tmp/gsd0410-expression.pdf'),'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T2/WebOnergeMetni/1f90d096-c858-4c65-886e-5c9dcdc5e878.pdf','0410-emep-expression-23643-pdf')]:
 raw=capture.read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);original='original.html.bin' if typ=='html' else 'original.pdf'
 for name,content in [(original,raw),('readable.html',readable_bytes(raw,typ,legacy=False))]:
  path=obj/name
  if path.exists():assert path.read_bytes()==content
  else:path.write_bytes(content)
 add('document',id=ident,party_id='emep',title='TBMM 2/3643 Türk Ceza Kanunu teklifi '+('kaydı' if typ=='html' else 'metni'),source_kind='official')
 add('document_version',id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date=None,version_label='TBMM kayıt ekranı' if typ=='html' else 'TBMM’ye 10 Nisan 2026 geliş kayıtlı imzalı teklif',accessed_at=now,verified_at=now,mime='text/html' if typ=='html' else 'application/pdf',sha256=sha,original_path='objects/'+sha+'/'+original,readable_path='objects/'+sha+'/readable.html',date_precision='unknown',date_unknown_reason='Ekran veya teklifin yayın günü ayrıca doğrulanmadı; geliş tarihi içerikte ayrı gösterilir.')
 if typ=='html':
  view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view);add('archive_view',**view);values=[('number','2 / 3643',None),('filed','10/04/2026',None),('karaca','Sevda KARACA DEM&#x130;R',None),('bayhan','&#x130;skender BAYHAN',None)]
 else:values=[('filing','Teklifi ve gerekçesi ekte sunulmuştur. 10.04,2026',0),('proposal',"Madde 1- 26/9/2004 tarihli ve 5237 sayılı Türk Ceza Kanunu'nun 217/A maddesi yürürlükten\nkaldırılmıştır.",4)]
 for suffix,exact,page in values:
  actual=html_source_text(raw) if page is None else pdf_page_text(capture,page);assert exact in actual,(suffix,exact)
  add('passage',id=ident+'-'+suffix+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='TBMM teklif bilgisi' if typ=='html' else 'İmzalı teklif metni',pdf_page_index=page,printed_page=None)
 add('source_attribution',version_id=ident+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None if typ=='html' else 'İskender Bayhan ve Sevda Karaca Demir',social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM resmi kayıt ve imzalı metni; yayın zamanı ile başkanlığa geliş günü ayrıdır.')
 print(typ,sha)
out=Path(__file__).parent/'expression-bill-source-draft.json';assert not out.exists();out.write_text(json.dumps(dict(status='draft_unvalidated',entries=entries,note='2/3643 TCK 217/A maddesinin kaldırılmasını önerir; sunulması kabul, yürürlük veya sonuç değildir.'),ensure_ascii=False,indent=2)+'\n')
