import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

root=Path('data/practices/sources/yeni-parti');capture=Path('/tmp/gsd-0404-uyelik-cesme.html');raw=capture.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest=='168f132c8999a2aced91a47f554ebac322aeeb31e9ac524942b534fae9aacade'
folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    dest=folder/name
    if dest.exists():assert dest.read_bytes()==content
    else:dest.write_bytes(content)
url='https://www.cesmeninsesi.com.tr/haber/yeni-partide-online-uyelik-sistemi-acildi-basvuru-nasil-yapilacak-1786521038';ident='0404-cevrimici-uyelik-cesme'
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view)
text=html_source_text(raw);exact='YENİ Parti’de teşkilatlanma çalışmaları sürerken, partiye katılmak isteyen vatandaşlar için online üyelik sistemi de kullanıma açıldı. YENİ Parti Çeşme İlçe Başkanlığı, çevrim içi üyelik başvurusunun nasıl yapılacağını anlatan 12 sayfalık bir rehber hazırlayarak, kimlik bilgilerinin girilmesinden aidat ödemesine ve Yargıtay kayıt sürecine kadar bütün aşamaları tek tek anlattı.';assert exact in text and '2026-08-12T10:46:00+03:00' in text
access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds');checked=datetime.now(timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='yeni-parti',title='Çeşme ilçe çevrim içi üyelik rehberi haberi',source_kind='news')),('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date='2026-08-12',version_label='Çeşme’nin Sesi haberinin yakalanan HTML sürümü',accessed_at=access,verified_at=checked,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='day',date_unknown_reason=None)),('archive_view',view),('passage',dict(id=ident+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='İlçe rehberi ve çevrim içi sistem haberi',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=ident+'-v1',kind='journalism',publisher='Çeşme’nin Sesi',author=None,social_handle=None,published_at='2026-08-12',date_precision='day',public_url=url,basis='Yayıncı sayfa başlığı ve 12 Ağustos yayın zamanı okundu; ayrı yazar adı belirtilmedi.'))]
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/membership-online-source-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=[dict(kind=k,values=v) for k,v in rows]),ensure_ascii=False,indent=2)+'\n');print(view['view_id'])
