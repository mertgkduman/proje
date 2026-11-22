import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text,readable_bytes

root=Path('data/practices/sources/yeni-parti');capture=Path('/tmp/gsd-0404-16kasim-tuzuk.pdf');raw=capture.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest=='a46c73ade5a7800e3df4a4c3baafc5d4e8d14e077964652cbdda1b6a7c9d0bf0'
folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.pdf',raw),('readable.html',readable_bytes(raw,'pdf',legacy=False))]:
    dest=folder/name
    if dest.exists():assert dest.read_bytes()==content
    else:dest.write_bytes(content)
page=pdf_page_text(capture,137);start=page.index('GEÇICI MADDE 6');end=page.index('(2) Parti Meclisi;',start);exact=page[start:end].strip();assert '09/11/2026' in exact and 'yüz altmış (160)' in exact and 'otuz (30)' in exact
url='https://api.yeni-parti.org.tr/uploads/yayinlar/yayin-1794902310469-811605043.pdf';ident='0404-sonraki-tuzuk-16kasim';access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds');checked=datetime.now(timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='yeni-parti',title='Daha sonra üretilen Yeni Parti tüzüğü PDF',source_kind='party')),('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date=None,version_label='PDF üstverisi 16 Kasım dönüşümü; kesim sonrası sürüm, yayın tarihi bilinmiyor',accessed_at=access,verified_at=checked,mime='application/pdf',sha256=digest,original_path='objects/'+digest+'/original.pdf',readable_path='objects/'+digest+'/readable.html',date_precision='unknown',date_unknown_reason='Belgenin yayın tarihi belirtilmedi; XMP üretim tarihi ve HTTP değişiklik zamanı yayın tarihi sayılmaz.')),('passage',dict(id=ident+'-gecici6-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article='Geçici Madde 6',section='Kurucular Kurulu tarih notu ve Parti Meclisi sayısı',pdf_page_index=137,printed_page=138)),('source_attribution',dict(version_id=ident+'-v1',kind='party_publication',publisher='Yeni Parti',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='PDF kapak ve son sayfasında Yeni Parti adı ve yayın iletişim bilgileri yer alır; 16 Kasım XMP dönüşümü yayın tarihi olarak kullanılmaz.'))]
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/postcutoff-charter-pdf-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated_postcutoff_context',source_root=str(root),entries=[dict(kind=k,values=v) for k,v in rows]),ensure_ascii=False,indent=2)+'\n');print(repr(exact))
