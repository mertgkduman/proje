"""Silopi sevki sonrası Ormanlı ve destek açıklamalarının özgün haberleri."""
import datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/dem');checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks'); out=[]
for name,date in [('3jul','2025-07-03'),('5jul','2025-07-05')]:
 url='https://www.rudaw.net/turkish/categories/turkey/'+('882010' if name=='3jul' else '882318');raw=Path('/tmp/gsd-dem-ormanli-'+name+'.html').read_bytes(); sha=hashlib.sha256(raw).hexdigest(); folder=root/'objects'/sha;folder.mkdir(parents=True,exist_ok=True)
 for filename,data in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
  path=folder/filename
  if path.exists():assert path.read_bytes()==data
  else:path.write_bytes(data)
 view=build_view(raw,url,root,fetch_assets=False);view['version_id']='0406-silopi-reply-'+name+'-v1';validate_view(root,view)
 out.append(dict(id=name,original_url=url,final_url=url,document_date=date,publisher='Rûdaw',accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',view=view)); print(name,sha,view['view_id'])
(checks/'silopi-reply-captures.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
