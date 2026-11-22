import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

root=Path('data/practices/sources/emep');now=datetime.now(timezone.utc).isoformat(timespec='seconds');rows=[]
def add(k,**v):rows.append(dict(kind=k,values=v))
detail=Path('/tmp/gsd0410-forest.html');raw=detail.read_bytes();sha=hashlib.sha256(raw).hexdigest();url='https://tbmm.gov.tr/Yasama/KanunTeklifi/a234c8c0-bc04-4dc6-8901-019ff10d27e2';ident='0410-emep-forest-23804-register'
obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view)
add('document',id=ident,party_id='emep',title='TBMM 2/3804 teklif kaydı',source_kind='official')
add('document_version',id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date=None,version_label='TBMM canlı kayıt görünümü; başvuru ve havale tarihleri içerir',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',date_precision='unknown',date_unknown_reason='Canlı kayıt sayfasının yayın tarihi bilinmiyor; kayıtlı olay tarihi belge tarihi değildir.')
add('archive_view',**view)
for suffix,exact,section in [('number','2 / 3804','Esas numarası'),('filed','11/08/2026','Başkanlığa geliş'),('commission','01/10/2026','Komisyona giriş')]:
 assert exact in html_source_text(raw);add('passage',id=ident+'-'+suffix+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
add('source_attribution',version_id=ident+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM teklif kayıt ekranı; yayın günü bilinmiyor, tarihli işlemler içerikte ayrıdır.')
pdf=Path('/tmp/gsd0410-forest.pdf');raw=pdf.read_bytes();sha=hashlib.sha256(raw).hexdigest();url='https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T2/WebOnergeMetni/863fb3e5-63a0-432f-86f3-1f3ea3818a59.pdf';ident='0410-emep-forest-23804-pdf';obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.pdf',raw),('readable.html',readable_bytes(raw,'pdf',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
exact='Ormanların Korunması Amacıyla 6831 Sayılı Orman Kanununda Değişiklik\nYapılmasına Dair Kanun Teklifimiz ve gerekçesi ekte sunulmuştur.';assert exact in pdf_page_text(pdf,0)
add('document',id=ident,party_id='emep',title='Ormanların Korunması Amacıyla 6831 Sayılı Orman Kanununda Değişiklik Yapılmasına Dair Kanun Teklifi',source_kind='official')
add('document_version',id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date='2026-08-11',version_label='11 Ağustos 2026 tarihli imzalı teklif',accessed_at=now,verified_at=now,mime='application/pdf',sha256=sha,original_path='objects/'+sha+'/original.pdf',readable_path='objects/'+sha+'/readable.html',date_precision='day',date_unknown_reason=None)
add('passage',id=ident+'-filing-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Teklif üst yazısı',pdf_page_index=0,printed_page=None)
add('source_attribution',version_id=ident+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author='Sevda Karaca Demir ve İskender Bayhan',social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM tarafından saklanan imzalı teklifin üst yazısı 11 Ağustos tarihlidir; kayıt imzacıları tanımlar. Yayın zamanı ayrıca doğrulanmadı.')
out=Path(__file__).parent/'forest-bill-source-draft.json';assert not out.exists();out.write_text(json.dumps(dict(status='draft_unvalidated',entries=rows,note='Teklif ve 1 Ekim komisyon sevki ayrıdır; kabul veya yürürlük iddia edilmedi.'),ensure_ascii=False,indent=2)+'\n');print('FOREST_SOURCE_RECORDS_OK',sha,view['view_id'])
