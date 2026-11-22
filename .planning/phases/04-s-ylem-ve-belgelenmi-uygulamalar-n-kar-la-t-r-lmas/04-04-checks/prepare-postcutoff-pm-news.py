import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

root=Path('data/practices/sources/yeni-parti');capture=Path('/tmp/gsd-0404-pm-amida.html');raw=capture.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest=='9e39001fe4c3df9801eb7a766e8e1e4c3512e077b8261083d11f2e2576f17fa6'
folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    dest=folder/name
    if dest.exists():assert dest.read_bytes()==content
    else:dest.write_bytes(content)
url='https://amidahaber.com/gundem/yeni-parti-kongresi-suruyor-parti-meclis-uyeleri-belli-oldu-240410h';ident='0404-pm-artis-amida'
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view)
text=html_source_text(raw);exact="Saat 10.00'da başlayan oturumda, Parti Meclisi'nin (PM) üye sayısının 150'den 160'a çıkarılması kararlaştırıldı. Partinin 9 Kasım tarihli Kurucular Kurulu kararıyla 80'den 150'ye yükseltilen üye sayısı, Genel Başkan Özgür Özel'e verilen yetki doğrultusunda 10 kişi daha artırıldı.";assert text.count(exact)==1 and '2026-11-15T14:10:52+03:00' in text
access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds');checked=datetime.now(timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='yeni-parti',title='Kurultayda Parti Meclisi üye sayısı hakkında haber',source_kind='news')),('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date='2026-11-15',version_label='Amida Haber kesim sonrası haber HTML sürümü',accessed_at=access,verified_at=checked,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='day',date_unknown_reason=None)),('archive_view',view),('passage',dict(id=ident+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='9 Kasım 150 ve kurultayda 160 anlatımı',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=ident+'-v1',kind='journalism',publisher='Amida Haber',author='Haber Merkezi',social_handle=None,published_at='2026-11-15',date_precision='day',public_url=url,basis='Haberin yayıncı ve Haber Merkezi künye alanları ile 15 Kasım yayın tarihi okundu.'))]
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/postcutoff-pm-news-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated_postcutoff_context',source_root=str(root),entries=[dict(kind=k,values=v) for k,v in rows]),ensure_ascii=False,indent=2)+'\n');print(view['view_id'])
