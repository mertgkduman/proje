"""TBMM haberinin özgün ve pasif kopyasını arşivle."""
import datetime, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import readable_bytes
from arsiv_gorunum import build_view, validate_view
root=Path('data/practices/sources/dem')
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
url='https://tbmm.gov.tr/Haber/mekke-anlasmasi-nin-onaylanmasinin-20261105015200'
raw=Path('/tmp/gsd-dem-2026-3961-news.html').read_bytes()
sha=hashlib.sha256(raw).hexdigest(); folder=root/'objects'/sha; folder.mkdir(parents=True,exist_ok=True)
for filename,data in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 path=folder/filename
 if path.exists(): assert path.read_bytes()==data
 else: path.write_bytes(data)
view=build_view(raw,url,root,fetch_assets=False);view['version_id']='0406-tbmm-2026-3961-news-v1';validate_view(root,view)
record=dict(original_url=url,final_url=url,document_date='2026-11-04',publisher='TBMM',accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',view=view)
(checks/'tbmm-2026-3961-news-capture.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(sha,view['view_id'])
