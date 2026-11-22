"""10/437 imzalı Meclis araştırması önergesi tutanağını özgün PDF olarak sakla."""
import datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import readable_bytes
root=Path('data/practices/sources/dem');checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
url='https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y2/T10/WebOnergeMetni/21c93b44-ef81-4790-9a6e-b2350fafc1d7.pdf';raw=Path('/tmp/gsd-dem-10437.pdf').read_bytes();assert raw.startswith(b'%PDF-');sha=hashlib.sha256(raw).hexdigest();folder=root/'objects'/sha;folder.mkdir(parents=True,exist_ok=True)
for name,data in [('original.pdf',raw),('readable.html',readable_bytes(raw,'pdf',legacy=False))]:
 p=folder/name
 if p.exists():assert p.read_bytes()==data
 else:p.write_bytes(data)
record=dict(original_url=url,final_url=url,document_date=None,publisher='TBMM',accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=sha,original_path='objects/'+sha+'/original.pdf',readable_path='objects/'+sha+'/readable.html')
(checks/'10437-pdf-capture.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(sha,len(raw))
