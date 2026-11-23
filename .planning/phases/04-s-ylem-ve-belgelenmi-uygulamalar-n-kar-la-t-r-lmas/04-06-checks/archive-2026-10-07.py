"""7 Ekim fon görüşmesinin iki özgün ve pasif TBMM kaynağını hazırla."""
import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/dem'); checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
items=[('full','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/3/Tam/5e3c67e6-7f96-4c37-9401-393802259f00.html','248d35a6070a1858effe9173b47f9a2824c090fa85f74fa1fb5ae2eab6631a1c'),('summary','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/3/Ozet/b749992e-fb8b-44ef-afd3-4a0522a593f1.html','b45a47227d6aaee3bd0acd01293285abf7db69ffcf32db2cea559fcbeec6e2d0')]
result=[]
for name,url,expected in items:
 raw=Path('/tmp/gsd-dem-2026-10-07-'+name+'.html').read_bytes(); digest=hashlib.sha256(raw).hexdigest(); assert digest==expected
 folder=root/'objects'/digest; folder.mkdir(parents=True,exist_ok=True)
 for fn,body in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=True))]:
  path=folder/fn
  if path.exists(): assert path.read_bytes()==body
  else: path.write_bytes(body)
 view=build_view(raw,url,root,fetch_assets=False,http_charset='windows-1254'); view['version_id']='0406-2026-10-07-'+name+'-v1';validate_view(root,view)
 result.append(dict(id=name,original_url=url,final_url=url,document_date='2026-10-07',publisher='TBMM',accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',view=view))
 print(name,digest,len(raw),len(html_source_text(raw)),view['view_id'])
(checks/'2026-10-07-fon-captures.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
