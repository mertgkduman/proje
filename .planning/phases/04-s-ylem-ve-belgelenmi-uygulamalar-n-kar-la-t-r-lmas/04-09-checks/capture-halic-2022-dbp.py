import json,sys
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent;src=c/'halic-2022-dbp-sources/bianet.html.bin';raw=src.read_bytes();digest=sha256(raw).hexdigest();assert digest=='a086de25cf9ac44d84a409f658b25d16a6e9f33b801089d56e066806fd10625e'
root=Path('data/practices/sources/dbp');obj=root/'objects'/digest;obj.mkdir(parents=True,exist_ok=True);orig=obj/'original.html.bin';readable=obj/'readable.html'
for p,b in ((orig,raw),(readable,readable_bytes(raw,'html',legacy=False))):
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
url='https://bianet.org/haber/emek-ve-ozgurluk-ittifaki-halkla-bulustu-birlikte-kazanacagiz-267592';now=datetime.now(timezone.utc).isoformat(timespec='seconds');doc='0409-halic-2022-bianet';vid=doc+'-v1';entries=[]
def add(k,**v):entries.append({'kind':k,'values':v})
add('document',id=doc,party_id='dbp',title='Bianet, Emek ve Özgürlük İttifakı Haliç halk buluşması',source_kind='news')
add('document_version',id=vid,document_id=doc,original_url='https://www.bianet.org/haber/emek-ve-ozgurluk-ittifaki-halkla-bulustu-birlikte-kazanacagiz-267592',final_url=url,document_date='2022-09-24',date_precision='day',date_unknown_reason=None,version_label='Erişilen özgün HTML; 24 Eylül 23.08 güncellenmiş.',accessed_at='2026-11-24T21:10:46.271077+00:00',verified_at=now,mime='text/html',sha256=digest,original_path=str(orig.relative_to(root)),readable_path=str(readable.relative_to(root)))
add('source_attribution',version_id=vid,kind='journalism',publisher='Bianet',author='Ruken Tuncel',social_handle=None,published_at='2022-09-24',date_precision='day',public_url=url,basis='Haber 15.24 yayımlanmış, erişilen nüsha 23.08 güncellenmiştir; sonraki içerik ilk sürüme atfedilmez.')
view=build_view(raw,url,root,fetch_assets=False);view['version_id']=vid;validate_view(root,view);add('archive_view',**view)
body=html_source_text(raw);start=body.index('Demokratik Bölgeler Partisi (DBP) Eş Genel Başkanı Keskin Bayındır');end=body.index('yer aldı.',start)+len('yer aldı.')
anchors=[('event','Haliçte ortak halk buluşması',"Haliç Kongre Merkezi'nde yol haritasını açıklamak üzere toplandı."),('identity','DBP eş genel başkanı kimliği','Demokratik Bölgeler Partisi (DBP) Eş Genel Başkanı Keskin Bayındır'),('attendance','Buluşmada sayılan kişiler',body[start:end]),('declaration','Halk buluşmasında deklarasyon açıklanması','deklarasyonun </a></strong>açıklanması ile devam etti.')]
for key,section,exact in anchors:
 assert exact in body
 add('passage',id=doc+'-'+key,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
with (c/'halic-2022-dbp-source-records.json').open('x') as f:json.dump({'party_id':'dbp','entries':entries},f,ensure_ascii=False,indent=2);f.write('\n')
print('HALIC2022_DBP_CAPTURE_OK',digest,len(entries),view['manifest_path'])
