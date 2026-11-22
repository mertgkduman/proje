import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');raw=Path('/tmp/gsd0410-women-conference-2025.html').read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);url='https://www.emep.org/emek-partisi-3-kadin-konferansi-sonuc-ve-kararlari';ident='0410-emep-women-conference-2025-party';version=ident+'-v1';now=datetime.now(timezone.utc).isoformat(timespec='seconds')
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);text=html_source_text(raw)
passages=[('event','Kadın kitleleri içerisindeki çalışmamızı değerlendirmek üzere 31 Mayıs-1 Haziran 2025 tarihlerinde gerçekleştirdiğimiz 3. Konferansımızda','Üçüncü kadın konferansının tarih aralığı'),('author','GENEL YÖNETİM KURULU (GYK)','Sonuç bildirgesinin parti kurulu atfı')]
rows=[dict(kind='document',values=dict(id=ident,party_id='emep',title='Emek Partisi 3. Kadın Konferansı sonuç ve kararları',source_kind='party')),dict(kind='document_version',values=dict(id=version,document_id=ident,original_url=url,final_url=url,document_date='2025-07-01',date_precision='day',date_unknown_reason=None,version_label='1 Temmuz 2025 parti bildirgesi; konferans 31 Mayıs–1 Haziran',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')),dict(kind='archive_view',values=view),dict(kind='source_attribution',values=dict(version_id=version,kind='party_publication',publisher='Emek Partisi',author='Genel Yönetim Kurulu',social_handle=None,published_at='2025-07-01',date_precision='day',public_url=url,basis='Partinin kendi sonuç ve kararlar yayını; tarihli konferans bildirgesi.'))]
for suffix,exact,section in passages:
 assert exact in text;rows.append(dict(kind='passage',values=dict(id=ident+'-'+suffix+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)))
out=Path(__file__).parent/'women-conference-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=rows,status='source_read_package_pending',note='GYK 1 Temmuz 2025 yayını üçüncü kadın konferansını 31 Mayıs–1 Haziran aralığında bildiriyor. Parti kendi yayınıdır; bağımsız tanıklık veya daha sonra gerçekleşmiş sonuç varsayılmaz.'),f,ensure_ascii=False,indent=2);f.write('\n')
print(sha,view['view_id'])
