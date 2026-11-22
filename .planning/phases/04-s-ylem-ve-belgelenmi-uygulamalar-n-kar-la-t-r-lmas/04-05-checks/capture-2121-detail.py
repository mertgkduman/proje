import datetime, hashlib, json, sys, subprocess
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import readable_bytes, html_source_text
from arsiv_gorunum import build_view, validate_view

url='https://www.tbmm.gov.tr/Yasama/KanunTeklifi/c3422565-793b-4f23-90d9-018f0fd3796b'
root=Path('data/practices/sources/tip')
raw=subprocess.run(['curl','-fsSL','--connect-timeout','10','--max-time','30','--retry','1','--retry-delay','1',url],check=True,stdout=subprocess.PIPE).stdout
at=datetime.datetime.now(datetime.timezone.utc).isoformat(); final_url=url
digest=hashlib.sha256(raw).hexdigest(); target=root/'objects'/digest
target.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    dest=target/name
    if dest.exists(): assert dest.read_bytes()==content
    else: dest.write_bytes(content)
view=build_view(raw,final_url,root,fetch_assets=False,http_charset='utf-8');view['version_id']='0405-tip-282121-v1';validate_view(root,view)
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
(out/'2121-detail-capture.json').write_text(json.dumps(dict(url=url,final_url=final_url,accessed_at=at,sha256=digest,bytes=len(raw),view=view),ensure_ascii=False,indent=2)+'\n')
print('OK',digest,at)
text=html_source_text(raw)
for term in ['Teklif ile','KOM&#x130;SYONDA','2 / 2121','24/04/2024']:
    i=text.find(term); print(term,repr(text[i:i+650]))
