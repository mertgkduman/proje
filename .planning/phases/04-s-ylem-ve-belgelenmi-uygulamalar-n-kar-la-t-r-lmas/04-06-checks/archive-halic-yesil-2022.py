import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent;root=Path('data/practices/sources/dem');raw=(c/'halic-2022-evidence/bianet-267592.html.bin').read_bytes();h=hashlib.sha256(raw).hexdigest();assert h=='a086de25cf9ac44d84a409f658b25d16a6e9f33b801089d56e066806fd10625e';folder=root/'objects'/h;folder.mkdir(parents=True,exist_ok=True)
for name,body in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=folder/name
 if p.exists():assert p.read_bytes()==body
 else:p.write_bytes(body)
url='https://bianet.org/haber/emek-ve-ozgurluk-ittifaki-halkla-bulustu-birlikte-kazanacagiz-267592';requested='https://www.bianet.org/haber/emek-ve-ozgurluk-ittifaki-halkla-bulustu-birlikte-kazanacagiz-267592'
v=build_view(raw,url,root,fetch_assets=False);v['version_id']='0406-halic-2022-bianet-v1';validate_view(root,v);text=html_source_text(raw);assert 'Yeşil Sol Parti Eş Genel Başkanları İbrahim Akın ve Ayşe Erdem' in text and 'Haliç Kongre Merkezi' in text
out=dict(url=requested,final_url=url,accessed_at=datetime.datetime.fromtimestamp(Path('/tmp/gsd-dem-bianet-alt0.html').stat().st_mtime,datetime.timezone.utc).isoformat(),sha256=h,original_path=f'objects/{h}/original.html.bin',readable_path=f'objects/{h}/readable.html',view=v)
(c/'halic-2022-capture.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
