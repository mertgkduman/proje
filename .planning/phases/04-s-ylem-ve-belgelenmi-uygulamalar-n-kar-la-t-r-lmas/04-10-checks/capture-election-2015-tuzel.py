import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');raw=Path('/tmp/gsd0410-election2015/tuzel.html').read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);url='https://anlatilaninotesi.com.tr/20150918/1017829271.html';ident='0410-emep-election-2015-tuzel';version=ident+'-v1';now=datetime.now(timezone.utc).isoformat(timespec='seconds')
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);text=html_source_text(raw)
exact='Ama bu y&#246;nde bir ittifak sağlanmadı. Biz de destek a&#231;ıklaması yaptık.';assert exact in text
entries=[dict(kind='document',values=dict(id=ident,party_id='emep',title='Tüzel’in 18 Eylül 2015 seçim açıklamasına ilişkin haber',source_kind='journalism')),dict(kind='document_version',values=dict(id=version,document_id=ident,original_url=url,final_url=url,document_date='2015-09-18',date_precision='day',date_unknown_reason=None,version_label='18 Eylül 2015 tarihli haber; 5 Ekim güncellemesi',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')),dict(kind='archive_view',values=view),dict(kind='source_attribution',values=dict(version_id=version,kind='journalism',publisher='Sputnik Türkiye',author=None,social_handle=None,published_at='2015-09-18',date_precision='day',public_url=url,basis='Sputnik Türkiye haberi Levent Tüzel’in Radikal’e açıklamasını aktarır; doğrudan görüşme kaynağı olarak gösterilmez.')),dict(kind='passage',values=dict(id=ident+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Tüzel’e atfedilen ittifak ve destek ayrımı',pdf_page_index=None,printed_page=None))]
out=Path(__file__).parent/'election-2015-tuzel-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=entries,status='source_read_package_pending',note='Tüzel’in Radikal’e sözlerini Sputnik aktarır; açıklama Gürkan’ın ayrı 18 Eylül beyanıyla kişi ve kapsam farkı korunarak ele alınır.'),f,ensure_ascii=False,indent=2);f.write('\n')
print('ELECTION2015_TUZEL_SOURCE_OK',sha,view['view_id'])
