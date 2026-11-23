import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');now=datetime.now(timezone.utc).isoformat(timespec='seconds');entries=[]
sources=[('session','/tmp/gsd0410-fund/session.html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/3/Tam/5e3c67e6-7f96-4c37-9401-393802259f00.html','7 Ekim 2026 Genel Kurul tam tutanağı','BAYHAN (','Bayhan konuşmacı başlığı'),('summary','/tmp/gsd0410-fund/summary.html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/3/Ozet/b749992e-fb8b-44ef-afd3-4a0522a593f1.html','7 Ekim 2026 Genel Kurul tutanak özeti','Bayhan','Bayhan aynı konuda grubu bulunmayan milletvekili olarak')]
for role,path,url,title,exact,section in sources:
 raw=Path(path).read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);ident='0410-emep-fund-2026-'+role;version=ident+'-v1'
 for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=True))]:
  p=obj/name
  if p.exists():assert p.read_bytes()==content
  else:p.write_bytes(content)
 view=build_view(raw,url,root,fetch_assets=False,http_charset='windows-1254');view['version_id']=version;validate_view(root,view);assert exact in html_source_text(raw)
 entries.extend([dict(kind='document',values=dict(id=ident,party_id='emep',title=title,source_kind='official')),dict(kind='document_version',values=dict(id=version,document_id=ident,original_url=url,final_url=url,document_date='2026-10-07',date_precision='day',date_unknown_reason=None,version_label=title+'; yayın zamanı bilinmiyor',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')),dict(kind='archive_view',values=view),dict(kind='source_attribution',values=dict(version_id=version,kind='official',publisher='TBMM Tutanak Hizmetleri Başkanlığı',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Birleşim tarihi ile tutanak yayım tarihi ayrı.')),dict(kind='passage',values=dict(id=ident+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None))]);print(role,sha,view['view_id'])
out=Path(__file__).parent/'fund-session-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=entries,status='source_read_partial',note='Genel Kurul 3. birleşimde fon piyasası hakkında Bayhan grubu bulunmayan milletvekili sıfatıyla konuştu. Eleştiriler kendisine atfedilir; genel kurul ve sonraki komisyon işlemleri ayrıdır. ASCII pasajlar windows-1254 kaynağına uyumludur ancak ayrıntılı içerik kanıtı için ek pasaj gerekir.'),f,ensure_ascii=False,indent=2);f.write('\n')
