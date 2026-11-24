"""DEM ve TBMM'nin 2 Temmuz 2024 kaynaklarının değişmez baytlarını arşivle."""
import datetime, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root=Path('data/practices/sources/dem')
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
items=[
 ('party','https://www.demparti.org.tr/tr/madimak-katliami/20178/','d578745de6a34bebe468842af9120d7d25d97b0cca44258256bc239618a44b4a','DEM Parti','Grup Başkanvekillerimiz'),
 ('tbmm','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/2/97/Tam/ea0a7bcb-b641-4f4d-9f3d-7f8d14dae6a7.html','bb1eba84d477f1451d13a51b956f825e16cb7899381ea1c4ed3327f564045299','TBMM','6131 grup numaralı'),
]
out=[]
for name,url,expected,publisher,anchor in items:
 raw=Path('/tmp/gsd-dem-sivas-2024-'+name+'.html').read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha==expected
 assert anchor in html_source_text(raw)
 folder=root/'objects'/sha;folder.mkdir(parents=True,exist_ok=True)
 for filename,body in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
  path=folder/filename
  if path.exists(): assert path.read_bytes()==body
  else: path.write_bytes(body)
 view=build_view(raw,url,root,fetch_assets=False);view['version_id']='0406-sivas-2024-'+name+'-v1';validate_view(root,view)
 out.append(dict(id='0406-sivas-2024-'+name,original_url=url,final_url=url,document_date='2024-07-02',publisher=publisher,accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',view=view))
 print(name,sha,view['view_id'])
(checks/'sivas-2024-antecedents-capture.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
