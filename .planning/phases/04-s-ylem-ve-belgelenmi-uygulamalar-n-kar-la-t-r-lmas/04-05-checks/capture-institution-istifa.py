import datetime, hashlib, json, sys, subprocess
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import readable_bytes, html_source_text
from arsiv_gorunum import build_view, validate_view

url='https://www.cumhuriyet.com.tr/siyaset/tipin-uc-il-yonetimi-istifa-etti-statukocu-bir-anlayisla-yol-2229384'
root=Path('data/practices/sources/tip')
raw=subprocess.run(['curl','-fsSL','--connect-timeout','10','--max-time','30','--retry','1','--retry-delay','1',url],check=True,stdout=subprocess.PIPE).stdout
at=datetime.datetime.now(datetime.timezone.utc).isoformat(); final_url=url
digest=hashlib.sha256(raw).hexdigest(); target=root/'objects'/digest
target.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    dest=target/name
    if dest.exists(): assert dest.read_bytes()==content
    else: dest.write_bytes(content)
view=build_view(raw,final_url,root,fetch_assets=False,http_charset='utf-8');view['version_id']='0405-tip-istifa-cumhuriyet-v1';validate_view(root,view)
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
(out/'institution-istifa-capture.json').write_text(json.dumps(dict(url=url,final_url=final_url,accessed_at=at,sha256=digest,bytes=len(raw),view=view),ensure_ascii=False,indent=2)+'\n')
print('OK',digest,at)
text=html_source_text(raw)
for term in ["TİP'TEN", "ihraç", "istifa"]:
    i=text.find(term); print(term,repr(text[max(0,i-100):i+600]))
