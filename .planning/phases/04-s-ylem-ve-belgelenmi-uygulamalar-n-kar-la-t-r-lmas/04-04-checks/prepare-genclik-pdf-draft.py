"""Bind the captured youth regulation while leaving historical dating open."""
import hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text
root=Path('data/practices/sources/yeni-parti'); h='499806c4492fd1e12448cb7d1fb854302b509aa119ef783606fa565430e1f30d'; src=root/h; raw=(src/'original.pdf').read_bytes(); assert hashlib.sha256(raw).hexdigest()==h
exact='Gençlik kollarının delegelik dahil her kademedeki seçimlerinde %50 cinsiyet kotası\nuygulanır.'; assert exact in pdf_page_text(src/'original.pdf',13)
dst=root/'objects'/h;dst.mkdir(parents=True,exist_ok=True)
for name in ('original.pdf','readable.html'):
 a,b=src/name,dst/name
 if b.exists():assert a.read_bytes()==b.read_bytes()
 else:shutil.copyfile(a,b)
u='https://api.yeni-parti.org.tr/uploads/belgeler/yonetmelik-1790069915474-30185980.pdf';at='2026-11-21T19:58:22.098597+00:00';i='0404-genclik-yonetmelik'
entries=[dict(kind='document',values=dict(id=i,party_id='yeni-parti',title='Gençlik Kolları Çalışma Yönetmeliği',source_kind='party')),dict(kind='document_version',values=dict(id=i+'-v1',document_id=i,original_url=u,final_url=u,document_date=None,version_label='Yakalanan yönetmelik PDF; tarihsel sürüm araştırılıyor',accessed_at=at,verified_at=at,mime='application/pdf',sha256=h,original_path='objects/'+h+'/original.pdf',readable_path='objects/'+h+'/readable.html',date_precision='unknown',date_unknown_reason='Dizindeki 22 Eylül bilgisinin bu PDF baytlarının tarihsel yayımı ve yürürlüğüyle bağı doğrulanmadı.')),dict(kind='passage',values=dict(id=i+'-p',version_id=i+'-v1',exact=exact,prefix=None,suffix=None,article='15(1)',section='Cinsiyet kotası',pdf_page_index=13,printed_page='12')),dict(kind='source_attribution',values=dict(version_id=i+'-v1',kind='party_publication',publisher='Yeni Parti',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=u,basis='PDF başlığı ve içeriği Yeni Parti Gençlik Kolları yönetmeliği olarak tanımlıyor; alan ve tarihsel sürüm ayrıca araştırılıyor.'))]
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/genclik-pdf-records-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries),ensure_ascii=False,indent=2)+'\n');print('GENCLIK_PDF_DRAFT',len(entries))
