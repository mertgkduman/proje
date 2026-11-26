import json,sys
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent; root=Path('data/practices/sources/emep'); source=c/'idlib-2020-emep-sources'; capture=json.loads((source/'capture.json').read_text()); now=datetime.now(timezone.utc).isoformat(); entries=[]
def add(table,**values): entries.append(dict(kind=table,values=values))
specs=[('call','EMEP Genel Merkezi: TSK ve bütün yabancı güçler Suriye’den çekilsin','party_publication','party','Emek Partisi','2020-02-28','text/html','emep-3479.html.bin'),('bm','BM S/2020/187: Türkiye ve Rusya’nın İdlib ek protokolü','official','official','Birleşmiş Milletler','2020-03-06','application/pdf','un-s-2020-187.pdf')]
for key,title,kind,attribution,publisher,day,mime,filename in specs:
 meta=next(x for x in capture if x.get('file')==filename); raw=(source/filename).read_bytes(); digest=sha256(raw).hexdigest(); assert digest==meta['sha256']; obj=root/'objects'/digest; obj.mkdir(parents=True,exist_ok=True); orig=obj/('original.pdf' if mime=='application/pdf' else 'original.html.bin'); readable=obj/'readable.html'
 for path,data in ((orig,raw),(readable,readable_bytes(raw,'pdf' if mime=='application/pdf' else 'html',legacy=False))):
  if path.exists(): assert path.read_bytes()==data
  else: path.write_bytes(data)
 doc='0410-idlib-2020-'+key; vid=doc+'-v1'; add('document',id=doc,party_id='emep',title=title,source_kind=kind); add('document_version',id=vid,document_id=doc,original_url=meta['requested_url'],final_url=meta['final_url'],document_date=day,date_precision='day',date_unknown_reason=None,version_label='EMEP Genel Merkezi açıklaması.' if key=='call' else '6 Mart tarihli BM mektubu ve 5 Mart tarihli ek protokol.',accessed_at=meta['retrieved_at_utc'],verified_at=now,mime=mime,sha256=digest,original_path=str(orig.relative_to(root)),readable_path=str(readable.relative_to(root))); add('source_attribution',version_id=vid,kind=attribution,publisher=publisher,author=None,social_handle=None,published_at=day,date_precision='day',public_url=meta['final_url'],basis='EMEP Genel Merkezi tarihli Türkçe asıl yayın.' if key=='call' else 'BM Güvenlik Konseyi mektubu ve Türkiye-Rusya ek protokolü.')
 if mime=='text/html':
  view=build_view(raw,meta['final_url'],root,fetch_assets=False); view['version_id']=vid; validate_view(root,view); add('archive_view',**view); body=html_source_text(raw)
 else: body=None
 anchors={'call':[('quote','İdlib’de ateş altındaki askerlerin çekilmesi','İdlib’de ateş altındaki askerleri acilen geri\nçekmeye çağırıyoruz.',None,None),('all','Suriye’de bütün askerî güçlerin çekilmesi','buradaki tüm\naskeri güçlerin geri çekilmesinden geçmektedir.',None,None)],'bm':[('signature','S/2020/187 eki, 5 Mart Moskova imzası.','Done in Moscow on 5 March, 2020',1,'2'),('start','S/2020/187 eki madde 1, İdlib temas hattında ateşkesin öngörülen başlangıcı.','starting from 00:01 of March 6, 2020.',1,'2'),('patrol','S/2020/187 eki madde 3, 15 Mart için ortak devriye düzenlemesi.','joint Turkish-Russian patrolling will begin',1,'2'),('transmission','S/2020/187 mektubu, BM’ye 6 Mart iletimi.','Letter dated 6 March 2020',0,None)]}
 for suffix,section,exact,page,printed in anchors[key]:
  text=body if page is None else pdf_page_text(orig,page); assert exact in text,(key,suffix); add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article='1' if suffix=='start' else ('3' if suffix=='patrol' else None),section=section,pdf_page_index=page,printed_page=printed)
with (c/'idlib-2020-emep-source-draft.json').open('x') as f: json.dump(dict(party_id='emep',entries=entries),f,ensure_ascii=False,indent=2); f.write('\n')
print('IDLIB_CAPTURE_OK',len(entries))
