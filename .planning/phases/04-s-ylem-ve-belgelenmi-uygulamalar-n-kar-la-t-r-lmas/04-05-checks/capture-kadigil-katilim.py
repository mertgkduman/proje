import datetime,hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import readable_bytes
from arsiv_gorunum import build_view,validate_view

root=Path('data/practices/sources/tip'); out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); results=[]
for name,url in [('bio','https://tip.org.tr/parti-sozcusu'),('bianet','https://bianet.org/haber/sera-kadigil-chp-den-istifa-etti-tip-e-katildi-246303')]:
 proc=subprocess.run(['curl','-fsSL','--connect-timeout','10','--max-time','30','--retry','1','--retry-delay','1',url],stdout=subprocess.PIPE)
 if proc.returncode:
  results.append(dict(name=name,url=url,attempted_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),curl_exit=proc.returncode,status='unavailable'))
  continue
 raw=proc.stdout
 at=datetime.datetime.now(datetime.timezone.utc).isoformat(); sha=hashlib.sha256(raw).hexdigest(); target=root/'objects'/sha;target.mkdir(parents=True,exist_ok=True)
 for key,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
  dest=target/key
  if dest.exists(): assert dest.read_bytes()==content
  else: dest.write_bytes(content)
 view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']='0405-tip-kadigil-'+name+'-v1';validate_view(root,view)
 results.append(dict(name=name,url=url,accessed_at=at,sha256=sha,bytes=len(raw),view=view))
 print(name,sha,at,len(raw),flush=True)
(out/'kadigil-katilim-capture.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
