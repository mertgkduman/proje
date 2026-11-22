import hashlib, json, sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

root=Path('data/practices/sources/yeni-parti');capture=Path('/tmp/gsd-0404-grup-ekonomim.html');raw=capture.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest=='afafe91b796da18984d3bd76a6ffec49b404eafedb8fcde8603b91bee514964b'
folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    dest=folder/name
    if dest.exists():assert dest.read_bytes()==content
    else:dest.write_bytes(content)
url='https://www.ekonomim.com/gundem/yeni-parti-ilk-kapali-grup-toplantisini-gerceklestirdi-tbmm-grup-yonetimi-belirlendi-haberi-908682';ident='0404-grup-yonetim-ekonomim'
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view)
text=html_source_text(raw);start="YENİ Parti&#039;nin Grup Yönetim Kurulu üyeleri ise şöyle oldu:";i=text.find(start);j=text.find('Özgür Karabat',i)+len('Özgür Karabat');assert i>=0 and j>i and '2026-07-28T12:47:00+03:00' in text
exact=text[i:j];access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds');checked=datetime.now(timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='yeni-parti',title='Yeni Parti TBMM grup yönetimi belirlendi',source_kind='news')),('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date='2026-07-28',version_label='Ekonomim haberinin yakalanan HTML sürümü',accessed_at=access,verified_at=checked,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='day',date_unknown_reason=None)),('archive_view',view),('passage',dict(id=ident+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='TBMM grup yönetim kurulu üyeleri',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=ident+'-v1',kind='journalism',publisher='Ekonomim',author='Haber Merkezi',social_handle=None,published_at='2026-07-28',date_precision='day',public_url=url,basis='Yayıncı ve articleAuthor alanı ile 28 Temmuz yayın tarihi okundu.'))]
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/group-management-source-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=[dict(kind=k,values=v) for k,v in rows]),ensure_ascii=False,indent=2)+'\n');print(view['view_id'],repr(exact))
