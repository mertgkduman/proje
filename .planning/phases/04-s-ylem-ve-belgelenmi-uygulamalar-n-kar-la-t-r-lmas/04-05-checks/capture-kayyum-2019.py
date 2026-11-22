import datetime,hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import readable_bytes
from arsiv_gorunum import build_view,validate_view

url='https://www.tip.org.tr/parti-aciklamalari/kayyum-saray-darbesidir';root=Path('data/practices/sources/tip')
raw=subprocess.run(['curl','-fsSL','--connect-timeout','10','--max-time','30','--retry','1','--retry-delay','1',url],check=True,stdout=subprocess.PIPE).stdout
at=datetime.datetime.now(datetime.timezone.utc).isoformat();sha=hashlib.sha256(raw).hexdigest();target=root/'objects'/sha;target.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 dest=target/name
 if dest.exists(): assert dest.read_bytes()==content
 else: dest.write_bytes(content)
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']='0405-tip-kayyum-2019-v1';validate_view(root,view)
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/kayyum-2019-capture.json')
out.write_text(json.dumps(dict(url=url,accessed_at=at,sha256=sha,bytes=len(raw),view=view),ensure_ascii=False,indent=2)+'\n');print('OK',sha,at,len(raw))
