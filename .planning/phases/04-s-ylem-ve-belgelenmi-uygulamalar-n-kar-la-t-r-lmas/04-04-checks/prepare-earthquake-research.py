import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/yeni-parti');raw=Path('/tmp/gsd-0404-104638.html').read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest=='48336797e511cc491574a68bcaaf159bb8fc199a12169ce7fd0a440688d7efa6'
folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    dest=folder/name
    if dest.exists():assert dest.read_bytes()==content
    else:dest.write_bytes(content)
url='https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/85b6bbae-2234-406d-9487-01a11b942e6a';identity='0404-tbmm-deprem-4638';at='2026-11-21T23:26:50+00:00'
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=identity+'-v1';validate_view(root,view)
text=html_source_text(raw); i=text.find('Depreme kar'); j=text.find('</td>',i); exact=text[i:j];assert i>=0 and 'Meclis ara' in exact and '10 / 4638' in text
entries=[('document',dict(id=identity,party_id='yeni-parti',title='10/4638 deprem önlemleri araştırma önergesi',source_kind='official')),('document_version',dict(id=identity+'-v1',document_id=identity,original_url=url,final_url=url,document_date=None,version_label='TBMM dinamik kayıt sayfası; yakalanan HTML',accessed_at=at,verified_at=at,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='unknown',date_unknown_reason='Dinamik kayıt sayfasının yayın tarihi bilinmiyor; önerge geliş tarihi ayrı kaydedilir.')),('archive_view',view),('passage',dict(id=identity+'-p',version_id=identity+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='10/4638 önerge özeti',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=identity+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM kurumsal başlığı ve önerge künyesi incelendi.'))]
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/earthquake-research-records-draft.json');out.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=[dict(kind=k,values=v) for k,v in entries]),ensure_ascii=False,indent=2)+'\n');print(digest,repr(exact))
