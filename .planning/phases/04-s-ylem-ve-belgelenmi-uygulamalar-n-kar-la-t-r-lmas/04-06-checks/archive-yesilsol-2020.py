import datetime,hashlib,json
from pathlib import Path
from arsiv import readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent;root=Path("data/practices/sources/dem");out={}
p=c/"yesilsol-2020-evidence/hdp-14267.html.bin";raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest();assert h=="4c33779603e24a832bb4c000727b9c1a9c91a96a8b111b169acca420ab21243b";folder=root/"objects"/h;folder.mkdir(parents=True,exist_ok=True)
for name,body in [("original.html.bin",raw),("readable.html",readable_bytes(raw,"html",legacy=False))]:
 f=folder/name
 if f.exists(): assert f.read_bytes()==body
 else:f.write_bytes(body)
url="https://www.hdp.org.tr/tr/gasp-edilen-halkin-iradesidir-sessiz-kalmayacagiz/14267/";v=build_view(raw,url,root,fetch_assets=False);v["version_id"]="0406-yesilsol-2020-hdp-v1";validate_view(root,v);out["hdp"]=dict(url=url,accessed_at=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),sha256=h,original_path=f"objects/{h}/original.html.bin",readable_path=f"objects/{h}/readable.html",view=v)
p=c/"yesilsol-2020-evidence/birgun-20200519.pdf";raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest();assert h=="ff2a7d6312825665a6e74c54f5b1164045c0cc0324eef5237400bb9507085d22";folder=root/"objects"/h;folder.mkdir(parents=True,exist_ok=True);f=folder/"original.pdf"
if f.exists(): assert f.read_bytes()==raw
else:f.write_bytes(raw)
out["birgun"]=dict(url="https://static.birgun.net/belge/2020/05/19/19-mayis-birgun-atejcd.pdf",accessed_at=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),sha256=h,original_path=f"objects/{h}/original.pdf",readable_path=None)
(c/"yesilsol-2020-capture.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n");print(json.dumps(out,ensure_ascii=False,indent=2))
