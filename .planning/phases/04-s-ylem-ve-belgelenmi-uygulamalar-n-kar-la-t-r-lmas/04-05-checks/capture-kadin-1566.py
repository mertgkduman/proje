import datetime,hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import readable_bytes
from arsiv_gorunum import build_view,validate_view

root=Path('data/practices/sources/tip'); results=[]
sources=[('detail','https://tbmm.gov.tr/Yasama/KanunTeklifi/5c026b7d-af8e-41c7-91ef-018a6feefb2b','html'),('proposal','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y1/T2/WebOnergeMetni/e3e93e7b-6d23-4c17-8f3f-3d8f56f93f0b.pdf','pdf')]
for name,url,kind in sources:
 raw=subprocess.run(['curl','-fsSL','--connect-timeout','10','--max-time','60','--retry','1','--retry-delay','1',url],check=True,stdout=subprocess.PIPE).stdout
 at=datetime.datetime.now(datetime.timezone.utc).isoformat();sha=hashlib.sha256(raw).hexdigest(); target=root/'objects'/sha;target.mkdir(parents=True,exist_ok=True)
 if kind=='pdf': assert raw.startswith(b'%PDF-')
 dest=target/('original.pdf' if kind=='pdf' else 'original.html.bin')
 if dest.exists(): assert dest.read_bytes()==raw
 else: dest.write_bytes(raw)
 result=dict(name=name,url=url,accessed_at=at,sha256=sha,bytes=len(raw))
 if kind=='html':
  readable=target/'readable.html';content=readable_bytes(raw,'html',legacy=False)
  if readable.exists(): assert readable.read_bytes()==content
  else: readable.write_bytes(content)
  view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']='0405-tip-281566-v1';validate_view(root,view);result['view']=view
 results.append(result);print(name,sha,at,len(raw),flush=True)
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/kadin-1566-capture.json');out.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
