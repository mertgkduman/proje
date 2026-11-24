import datetime,hashlib,json
from pathlib import Path
from arsiv import readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent; root=Path("data/practices/sources/dem"); out={}
items=[("dem","dem-17952.html.bin","https://www.demparti.org.tr/en/we-urge-the-akp-government-to-respect-the-will-of-the-people-of-van/17952/"),("appeal","dem-objection-transcript.html.bin","https://www.solmedya.com/2024/04/03/dem-partinin-30-sayfalik-abdullah-zeydan-itirazinin-tam-metni/"),("result","bianet-293849.html.bin","https://bianet.org/haber/ysk-abdullah-zeydan-in-baskanligini-iade-etti-293849")]
for key,name,url in items:
 p=c/"van-2024-evidence"/name; raw=p.read_bytes(); h=hashlib.sha256(raw).hexdigest(); folder=root/"objects"/h; folder.mkdir(parents=True,exist_ok=True)
 for fname,body in [("original.html.bin",raw),("readable.html",readable_bytes(raw,"html",legacy=False))]:
  f=folder/fname
  if f.exists(): assert f.read_bytes()==body
  else: f.write_bytes(body)
 view=build_view(raw,url,root,fetch_assets=False); view["version_id"]="0406-van-2024-"+key+"-v1";validate_view(root,view)
 out[key]=dict(url=url,accessed_at=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),sha256=h,original_path=f"objects/{h}/original.html.bin",readable_path=f"objects/{h}/readable.html",view=view)
p=c/"van-2024-evidence/dem-april2.pdf";raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest();folder=root/"objects"/h;folder.mkdir(parents=True,exist_ok=True);f=folder/"original.pdf"
if f.exists(): assert f.read_bytes()==raw
else: f.write_bytes(raw)
out["dated_pdf"]=dict(url="https://civaka-azad.org/wp-content/uploads/2024/04/We_urge_the_AKP_Government_to_Respect_the_Will_of_the_People_of_Van.pdf",accessed_at=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),sha256=h,original_path=f"objects/{h}/original.pdf",readable_path=None)
(c/"van-2024-capture.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n");print(json.dumps(out,ensure_ascii=False,indent=2))
