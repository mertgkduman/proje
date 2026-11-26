import json,sys
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent; root=Path('data/practices/sources/emep'); src=c/'trelle-emep-2019-sources'; meta=json.loads((src/'capture.json').read_text()); now=datetime.now(timezone.utc).isoformat(); entries=[]
def add(table,**values): entries.append(dict(kind=table,values=values))
specs=[('call','evrensel-394314.html.bin','2019-12-30','Evrensel: EMEP yılbaşı dayanışma çağrısı',[('quote','Haberin aktardığı parti açıklaması','Yeni yıla dayanışmayla, omuz omuza giriyoruz.'),('specific','Trelleborg çağrısı','Yeni yılda geri sayımı Trelleborg iş&ccedil;isiyle birlikte yapacağız.'),('plan','31 Aralık planı','yarın (31 Aralık Salı)')]),('visit','evrensel-394425.html.bin','2020-01-01','Evrensel: EMEP grev çadırında yeni yılı karşıladı',[('meeting','Yılbaşı buluşması','Emek Partisi yeni yıla grevdeki Trelleborg iş&ccedil;ileriyle girdi.'),('role','Kocaeli il başkanı','Emek Partisi Kocaeli İl Başkanı Arzu Erkan')])]
for key,filename,day,title,anchors in specs:
 m=next(x for x in meta if x.get('file')==filename); raw=(src/filename).read_bytes(); digest=sha256(raw).hexdigest(); assert digest==m['sha256']; obj=root/'objects'/digest; obj.mkdir(parents=True,exist_ok=True); orig=obj/'original.html.bin'; readable=obj/'readable.html'
 for path,data in [(orig,raw),(readable,readable_bytes(raw,'html',legacy=False))]:
  if path.exists(): assert path.read_bytes()==data
  else: path.write_bytes(data)
 doc='0410-trelle-2019-'+key; vid=doc+'-v1'; add('document',id=doc,party_id='emep',title=title,source_kind='news'); add('document_version',id=vid,document_id=doc,original_url=m['requested_url'],final_url=m['final_url'],document_date=day,date_precision='day',date_unknown_reason=None,version_label='Erişilen haber; 1 Ocak haberi 2 Ocakta güncellenmiştir.' if key=='visit' else 'Erişilen tarihli haber.',accessed_at=m['retrieved_at_utc'],verified_at=now,mime='text/html',sha256=digest,original_path=str(orig.relative_to(root)),readable_path=str(readable.relative_to(root))); add('source_attribution',version_id=vid,kind='journalism',publisher='Evrensel',author=None,social_handle=None,published_at=day,date_precision='day',public_url=m['final_url'],basis='Gazete haberi; parti açıklaması gazete tarafından aktarılmıştır.' if key=='call' else 'Gazetenin yılbaşı sonrası haberi; erişilen sürüm 2 Ocak güncellemelidir.')
 view=build_view(raw,m['final_url'],root,fetch_assets=False); view['version_id']=vid; validate_view(root,view); add('archive_view',**view); body=html_source_text(raw)
 for suffix,section,exact in anchors:
  assert exact in body,(key,exact)
  add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
with (c/'trelle-2019-emep-source-draft.json').open('x') as f: json.dump(dict(party_id='emep',entries=entries),f,ensure_ascii=False,indent=2); f.write('\n')
print('TRELLE_CAPTURE_OK',len(entries))
