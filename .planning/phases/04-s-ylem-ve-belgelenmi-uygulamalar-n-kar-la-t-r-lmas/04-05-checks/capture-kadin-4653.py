import datetime,hashlib,json,subprocess
from pathlib import Path

url='https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y6/T2/WebOnergeMetni/14cbec28-d778-4864-a43c-f95f23c46699.pdf'
raw=subprocess.run(['curl','-fsSL','--connect-timeout','10','--max-time','60','--retry','1','--retry-delay','1',url],check=True,stdout=subprocess.PIPE).stdout
at=datetime.datetime.now(datetime.timezone.utc).isoformat();assert raw.startswith(b'%PDF-');sha=hashlib.sha256(raw).hexdigest()
dest=Path('data/practices/sources/tip/objects')/sha/'original.pdf';dest.parent.mkdir(parents=True,exist_ok=True)
if dest.exists(): assert dest.read_bytes()==raw
else: dest.write_bytes(raw)
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/kadin-4653-capture.json')
out.write_text(json.dumps(dict(url=url,accessed_at=at,sha256=sha,bytes=len(raw)),ensure_ascii=False,indent=2)+'\n')
print('OK',sha,at,len(raw))
