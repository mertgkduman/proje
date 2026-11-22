import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root=Path('data/practices/sources/yeni-parti');capture=Path('/tmp/gsd-0404-grup-dunya.html');raw=capture.read_bytes()
digest=hashlib.sha256(raw).hexdigest();assert digest=='ba51c913e2e9057d8c78da61b60e8c78dc9e1724aa059de7a566279c3fa2373b'
folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    dest=folder/name
    if dest.exists():assert dest.read_bytes()==content
    else:dest.write_bytes(content)
url='https://www.dunya.com/gundem/yeni-partinin-grup-baskan-vekilleri-pm-ve-ydk-uyeleri-belli-oldu-haberi-833547';ident='0404-grup-kurulus-dunya'
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view)
text=html_source_text(raw);exact='Kurucular Kurulu toplantısının ardından gerçekleştirilen YENİ Parti Kapalı Grup Toplantısı&#039;nda ise TBMM Grup Başkanvekilleri belirlendi. Yapılan seçim sonucunda Ali Mahir Başarır, Murat Emir ve Gökhan Günaydın grup başkanvekilliği görevine seçildi.'
assert text.count(exact)==1 and '2026-07-24T17:57:00+03:00' in text
access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds');checked=datetime.now(timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='yeni-parti',title='Yeni Parti grup başkanvekilleri belirlendi',source_kind='news')),('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date='2026-07-24',version_label='Dünya haberinin yakalanan HTML sürümü',accessed_at=access,verified_at=checked,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='day',date_unknown_reason=None)),('archive_view',view),('passage',dict(id=ident+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Kapalı grup toplantısı ve başkanvekili seçimi',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=ident+'-v1',kind='journalism',publisher='Dünya Gazetesi',author='Dünya Gazetesi',social_handle=None,published_at='2026-07-24',date_precision='day',public_url=url,basis='Sayfanın yayıncı ve article:author alanları ile 24 Temmuz yayın tarihi okundu.'))]
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/group-founding-source-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=[dict(kind=k,values=v) for k,v in rows]),ensure_ascii=False,indent=2)+'\n');print(view['view_id'])
