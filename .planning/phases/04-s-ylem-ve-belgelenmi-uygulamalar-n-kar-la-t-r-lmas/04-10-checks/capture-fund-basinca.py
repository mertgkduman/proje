import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');raw=Path('/tmp/gsd0410-fund/basinca.html').read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);url='https://basinca.com/haber/emep-li-bayhan-dan-fon-krizi-cikisi-kaynak-yok-diyenlerden-hesap-sorun';ident='0410-emep-fund-2026-basinca';version=ident+'-v1';now=datetime.now(timezone.utc).isoformat(timespec='seconds')
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);text=html_source_text(raw)
entries=[dict(kind='document',values=dict(id=ident,party_id='emep',title='Bayhan’ın fon krizi Genel Kurul konuşması',source_kind='journalism')),dict(kind='document_version',values=dict(id=version,document_id=ident,original_url=url,final_url=url,document_date='2026-10-07',date_precision='day',date_unknown_reason=None,version_label='7 Ekim 2026 tarihli haber',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')),dict(kind='archive_view',values=view),dict(kind='source_attribution',values=dict(version_id=version,kind='journalism',publisher='Basınca',author='Basınca Haber Masası',social_handle=None,published_at='2026-10-07',date_precision='day',public_url=url,basis='Haberde Haber Masası künyesi ve editör Kemal Vanlı ayrı gösterilir.'))]
for key,exact,section in [('speaker','Emek Partisi (EMEP) İstanbul Milletvekili İskender Bayhan, kürsüde fon krizini değerlendirdi.','Bayhan konuşmasının konusu'),('critique','Borsa ve bankalara yönelik eleştirilerini sürdüren Bayhan','Bayhan’ın banka ve borsa eleştirisi')]:
 assert exact in text;entries.append(dict(kind='passage',values=dict(id=ident+'-'+key+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)))
out=Path(__file__).parent/'fund-basinca-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=entries,status='source_read_package_pending',note='7 Ekim konuşmasını haberleştirir; Bayhan grup adına değil, grubu bulunmayan milletvekili olarak söz almıştır. Eleştirileri kendi görüşleridir.'),f,ensure_ascii=False,indent=2);f.write('\n')
print('FUND_BASINCA_CAPTURE_OK',sha,view['view_id'])
