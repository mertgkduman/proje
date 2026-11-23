import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');raw=Path('/tmp/gsd0410-disability/party.html').read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);url='https://www.emep.org/engelsiz-bir-yasam-icin-gerekli-adimlar-hizla-atilsin';ident='0410-emep-disability-2024';version=ident+'-v1';now=datetime.now(timezone.utc).isoformat(timespec='seconds')
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);text=html_source_text(raw)
rows=[dict(kind='document',values=dict(id=ident,party_id='emep',title='Engelsiz bir yaşam için gerekli adımlar',source_kind='party')),dict(kind='document_version',values=dict(id=version,document_id=ident,original_url=url,final_url=url,document_date='2024-05-14',date_precision='day',date_unknown_reason=None,version_label='14 Mayıs 2024 tarihli parti açıklaması',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')),dict(kind='archive_view',values=view),dict(kind='source_attribution',values=dict(version_id=version,kind='party_publication',publisher='Emek Partisi',author='Selma Gürkan',social_handle=None,published_at='2024-05-14',date_precision='day',public_url=url,basis='Parti sitesinde yayımlanan, genel başkan yardımcısı Selma Gürkan imzalı açıklama.'))]
for key,exact,section in [('disaster','Acil afet eylem planlarında engellilere yönelik önlemler mutlaka yer alsın.','Afet planında engellilere yönelik önlem talebi'),('transport','Tekerlekli sandalye kullanıcılarının tekerlekli sandalyesi ile binebileceği taksi ve turizm taşımacılığı için gerekli düzenleme ivedilikle yapılsın.','Erişilebilir taşıma talebi'),('care','Ağır engelli bireye bakmak için sosyal yardımlar kapsamında “evde bakım ücreti” alan kişiye sigorta yapılsın ve insanca yaşayacak bir ücret verilsin.','Evde bakım sigortası talebi')]:
 assert exact in text;rows.append(dict(kind='passage',values=dict(id=ident+'-'+key+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)))
out=Path(__file__).parent/'disability-policy-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=rows,status='source_read_package_pending',note='14 Mayıs 2024 imzalı talep açıklaması; önlemlerin uygulandığı veya bütün afet ve turizm politikasını kapsadığı çıkarılmaz.'),f,ensure_ascii=False,indent=2);f.write('\n')
print('DISABILITY_SOURCE_OK',sha,view['view_id'])
