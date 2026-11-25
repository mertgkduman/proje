import json, sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

c = Path(__file__).resolve().parent
root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat()
entries = []
def add(k, **values): entries.append(dict(kind=k, values=values))
specs = [
 ('hdp', 'HDP yayımında 18 Mayıs ortak bildirisi', 'unknown', 'other', 'Halkların Demokratik Partisi', '2020-05-18', 'text/html', 'hdp-14267.html.bin', '9e2db9a324041600d0ef6268c72b9c81210ef5b5e746eed58523cf7a664a0478', 'https://www.hdp.org.tr/tr/gasp-edilen-halkin-iradesidir-sessiz-kalmayacagiz/14267/', '2026-11-24T22:58:13.275239+00:00'),
 ('birgun', 'BirGün 19 Mayıs 2020, sayfa 8', 'news', 'journalism', 'BirGün', '2020-05-19', 'application/pdf', 'birgun-2020-05-19.pdf', 'ff2a7d6312825665a6e74c54f5b1164045c0cc0324eef5237400bb9507085d22', 'https://static.birgun.net/belge/2020/05/19/19-mayis-birgun-atejcd.pdf', '2026-11-24T22:58:34.954239+00:00')]
for key,title,kind,attr,publisher,day,mime,filename,digest,url,accessed in specs:
 raw=(c.parent/'04-09-checks'/'joint-2020-search'/filename).read_bytes(); assert sha256(raw).hexdigest()==digest
 obj=root/'objects'/digest; obj.mkdir(parents=True,exist_ok=True); ext='html.bin' if mime=='text/html' else 'pdf'; original=obj/('original.'+ext); readable=obj/'readable.html'
 for path,data in ((original,raw),(readable,readable_bytes(raw,'html' if mime=='text/html' else 'pdf',legacy=False))):
  if path.exists(): assert path.read_bytes()==data
  else: path.write_bytes(data)
 doc='0410-joint-2020-'+key; vid=doc+'-v1'
 add('document',id=doc,party_id='emep',title=title,source_kind=kind)
 add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day',date_unknown_reason=None,version_label='Erişilen özgün nüsha.',accessed_at=accessed,verified_at=now,mime=mime,sha256=digest,original_path=str(original.relative_to(root)),readable_path=str(readable.relative_to(root)))
 add('source_attribution',version_id=vid,kind=attr,publisher=publisher,author='Haber Merkezi' if key=='birgun' else None,social_handle=None,published_at=day,date_precision='day',public_url=url,basis='HDP ortak imzalı bildiriyi yayımlamıştır; yayımlayan HDP ve imzacı EMEP ayrı kurumlardır.' if key=='hdp' else '19 Mayıs basılı sayı, sayfa 8; imzacılar haber metninde listelenir.')
 if key=='hdp':
  view=build_view(raw,url,root,fetch_assets=False); view['version_id']=vid; validate_view(root,view); add('archive_view',**view); body=html_source_text(raw)
  anchors=[('title','Ortak metnin başlığı','Gasp edilen halkın iradesidir; sessiz kalmayacağız!'),('date','Yayım tarihi','18 Mayıs 2020'),('signature','EMEP ortak imzacı listesinde','Emek Partisi (EMEP)'),('statement','Ortak bildirinin beş belediye ifadesi',"HDP'li beş belediyeye daha kayyım atadı.")]
 else:
  body=pdf_page_text(original,7); anchors=[('title','Basılı haber başlığı','Gasp edilen halkın iradesidir;'),('signature','Basılı haber EMEP imza listesi','Parti, Emek Partisi')]
 for suffix,section,exact in anchors:
  assert exact in body,(key,exact)
  add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=7 if key=='birgun' else None,printed_page='8' if key=='birgun' else None)
out=c/'joint-2020-emep-source-records.json'
with out.open('x') as f: json.dump({'party_id':'emep','entries':entries},f,ensure_ascii=False,indent=2); f.write('\n')
print('JOINT_EMEP_CAPTURE_OK',len(entries))
