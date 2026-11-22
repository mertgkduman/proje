"""Hakkâri ön seçimindeki iki tur ve sonraki itiraz için başlangıç kaynakları."""
import datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import readable_bytes,html_source_text
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/dem'); checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
items=[('hakkari_round1_alt','https://www.yuksekovahaber.com.tr/haber/hakkaride-dem-partinin-on-secimi-ikinci-tura-kaldi-260006.htm','2024-01-13','Yüksekova Haber'),('hakkari_round2','https://www.yuksekovahalkinsesigazetesi.com/dem-partinin-hakkari-adaylari-belli-oldu','2024-01-14','Yüksekova Halkın Sesi'),('hakkari_speech','https://www.elipshaber.com/dem-partinin-hakkari-ve-batman-adaylari-belli-oldu','2024-01-14','Elips Haber')]
out=[]
for name,url,date,publisher in items:
 raw=Path('/tmp/gsd-dem-'+name+'.html').read_bytes();html_source_text(raw);sha=hashlib.sha256(raw).hexdigest();folder=root/'objects'/sha;folder.mkdir(parents=True,exist_ok=True)
 for fn,body in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
  p=folder/fn
  if p.exists():assert p.read_bytes()==body
  else:p.write_bytes(body)
 view=build_view(raw,url,root,fetch_assets=False);view['version_id']='0406-'+name.replace('_','-')+'-v1';validate_view(root,view)
 out.append(dict(id=name,url=url,date=date,publisher=publisher,accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',view=view))
 print(name,sha,len(raw),view['view_id'])
(checks/'hakkari-rounds-captures.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
