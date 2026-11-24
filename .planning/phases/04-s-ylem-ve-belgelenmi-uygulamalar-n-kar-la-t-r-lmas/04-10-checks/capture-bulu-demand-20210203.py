import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
D=Path(__file__).parent;root=Path('data/practices/sources/emep')
raw=Path('/tmp/gsd-emep-bulu-20210203.html').read_bytes();url='https://www.emep.org/bastirilmak-istenen-ozerk-universite-demokratik-turkiye-talebidir'
text=html_source_text(raw)
for exact in ['Melih Bulu istifa etsin!','Rektörler atanmasın, seçimle belirlensin!']: assert exact in text
digest=hashlib.sha256(raw).hexdigest();obj=root/'objects'/digest;obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=obj/name
 if p.exists(): assert p.read_bytes()==content
 else:p.write_bytes(content)
now=datetime.now(timezone.utc).isoformat(timespec='seconds');doc='0410-emep-bulu-demand-20210203';version=doc+'-v1'
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view)
entries=[dict(kind='document',values=dict(id=doc,party_id='emep',title='Gürkan: özerk üniversite ve rektörlük talebi',source_kind='party')),
 dict(kind='document_version',values=dict(id=version,document_id=doc,original_url=url,final_url=url,document_date='2021-02-03',date_precision='day',date_unknown_reason=None,version_label='3 Şubat 2021 tarihli parti yayını',accessed_at=now,verified_at=now,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html')),
 dict(kind='archive_view',values=view),
 dict(kind='passage',values=dict(id=doc+'-resign-p',version_id=version,exact='Melih Bulu istifa etsin!',prefix=None,suffix=None,article=None,section='Bulu istifa talebi',pdf_page_index=None,printed_page=None)),
 dict(kind='passage',values=dict(id=doc+'-election-p',version_id=version,exact='Rektörler atanmasın, seçimle belirlensin!',prefix=None,suffix=None,article=None,section='Rektörlerin seçilmesi talebi',pdf_page_index=None,printed_page=None)),
 dict(kind='source_attribution',values=dict(version_id=version,kind='party_publication',publisher='Emek Partisi',author='Selma Gürkan',social_handle=None,published_at='2021-02-03',date_precision='day',public_url=url,basis='Özgün parti sayfasının yayın tarihi, yazar ve genel başkan yardımcısı imzası.'))]
with (D/'bulu-demand-20210203-source-draft.json').open('x') as f:json.dump(dict(status='source_read_package_pending',entries=entries),f,ensure_ascii=False,indent=2);f.write('\n')
print(digest,view['view_id'])
