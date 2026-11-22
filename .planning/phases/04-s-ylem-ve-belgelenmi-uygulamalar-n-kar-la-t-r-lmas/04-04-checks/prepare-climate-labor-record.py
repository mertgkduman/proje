import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/yeni-parti'); capture=Path('/tmp/gsd-0404-104651.html'); raw=capture.read_bytes()
digest=hashlib.sha256(raw).hexdigest(); assert digest=='3df91b271b68b8ef783993db41eb229e70ff154ea3fbbc6546b3390ceb95e9cb'
folder=root/'objects'/digest; folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    dest=folder/name
    if dest.exists(): assert dest.read_bytes()==content
    else: dest.write_bytes(content)
url='https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/35ebbaef-ef4c-4f18-abcf-01a11b750c08'; ident='0404-tbmm-iklim-tarim-4651'
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8'); view['version_id']=ident+'-v1'; validate_view(root,view)
text=html_source_text(raw); i=text.find('K&#xFC;resel iklim krizinin tar&#x131;m'); j=text.find('</td>',i); assert i>=0 and j>i and '10 / 4651' in text
accessed=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds'); checked=datetime.now(timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='yeni-parti',title='10/4651 iklim krizi ve tarım işçileri araştırma önergesi',source_kind='official')),('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date=None,version_label='TBMM dinamik kayıt sayfası; yakalanan HTML',accessed_at=accessed,verified_at=checked,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='unknown',date_unknown_reason='Dinamik sayfanın yayın tarihi bilinmiyor; önerge tarihi ayrı kaydedilir.')),('archive_view',view),('passage',dict(id=ident+'-p',version_id=ident+'-v1',exact=text[i:j],prefix=None,suffix=None,article=None,section='10/4651 önerge özeti',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=ident+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM kurumsal başlığı ve önerge künyesi incelendi.'))]
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/climate-labor-record-draft.json'); p.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=[dict(kind=k,values=v) for k,v in rows]),ensure_ascii=False,indent=2)+'\n'); print(view['view_id'])
