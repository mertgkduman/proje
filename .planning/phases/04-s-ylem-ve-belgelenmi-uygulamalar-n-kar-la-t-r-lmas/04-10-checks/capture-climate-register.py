import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');raw=Path('/tmp/gsd0410-climate/register.html').read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
url='https://tbmm.gov.tr/Yasama/KanunTeklifi/a0d0d465-837b-41f0-bd57-0195237fad31';ident='0410-emep-climate-2025-register';version=ident+'-v1';now=datetime.now(timezone.utc).isoformat(timespec='seconds')
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);text=html_source_text(raw)
exact='2 / 2927';assert exact in text
entries=[dict(kind='document',values=dict(id=ident,party_id='emep',title='TBMM İklim Kanunu 2/2927 teklif kaydı',source_kind='official')),dict(kind='document_version',values=dict(id=version,document_id=ident,original_url=url,final_url=url,document_date=None,date_precision='unknown',date_unknown_reason='Kayıt ekranının yayın tarihi bilinmiyor.',version_label='Teklif ve komisyon kayıt ekranı',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')),dict(kind='archive_view',values=view),dict(kind='source_attribution',values=dict(version_id=version,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM teklif kaydı; kayıt ekranının yayın tarihi çıkarılmadı.')),dict(kind='passage',values=dict(id=ident+'-number-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='İklim Kanunu teklif esas numarası',pdf_page_index=None,printed_page=None))]
out=Path(__file__).parent/'climate-register-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=entries,status='source_read_package_pending',note='TBMM 2/2927 kaydı teklif başlığını, sıra sayısı 198 ve kanunlaşma bilgisini gösterir; oylama cetveli ayrı.'),f,ensure_ascii=False,indent=2);f.write('\n')
print('CLIMATE_REGISTER_CAPTURE_OK',sha,view['view_id'])
