"""Disiplin sürecindeki ilgili kaynakların özgün ve pasif kopyaları."""
import datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/dem')
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
items=[('kiziltepe-board', 'https://www.demparti.org.tr/tr/zeyni-ipek-kiziltepe-halkinin-iradesine-layik-olamamistir/20622/', 'https://www.demparti.org.tr/tr/zeyni-ipek-kiziltepe-halkinin-iradesine-layik-olamamistir/20622/', '2024-12-26', 'DEM Parti'), ('kiziltepe-decision', 'https://amidahaber.com/politika/dem-parti-belediye-baskanini-ihrac-etti-206304h', 'https://amidahaber.com/politika/dem-parti-belediye-baskanini-ihrac-etti-206304h', '2024-12-27', 'Amida Haber'), ('kiziltepe-reply', 'https://www.turkiyegazetesi.com.tr/gundem/demli-belediye-baskani-zeyni-ipek-santaj-yapildigi-gerekcesiyle-istifa-ettigini-duyurdu-1082632', 'https://www.turkiyegazetesi.com.tr/gundem/demli-belediye-baskani-zeyni-ipek-santaj-yapildigi-gerekcesiyle-istifa-ettigini-duyurdu-1082632', '2024-12-25', 'Türkiye Gazetesi')]
out=[]
for name,url,final,date,publisher in items:
 raw=Path('/tmp/gsd-dem-'+name+'.html').read_bytes(); text=html_source_text(raw); sha=hashlib.sha256(raw).hexdigest();folder=root/'objects'/sha;folder.mkdir(parents=True,exist_ok=True)
 for fn,body in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
  p=folder/fn
  if p.exists(): assert p.read_bytes()==body
  else: p.write_bytes(body)
 view=build_view(raw,final,root,fetch_assets=False);view['version_id']='0406-'+name.replace('_','-')+'-v1';validate_view(root,view)
 out.append(dict(id=name,original_url=url,final_url=final,document_date=date,publisher=publisher,accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',view=view))
 print(name,sha,len(raw),len(text),view['view_id'],flush=True)
(checks/'kiziltepe-2024-capture.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
