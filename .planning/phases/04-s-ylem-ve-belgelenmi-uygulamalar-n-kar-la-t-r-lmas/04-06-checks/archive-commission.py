"""10/1831 ortak komisyonunun 2025 süreci: kaynakların pasif kopyaları."""
import datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/dem')
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
items=[('komisyon_12subat','https://www.tbmm.gov.tr/Tutanaklar/TutanakGoster/4101','2025-02-12','Türkiye Büyük Millet Meclisi','pdf'),('dem_12subat','https://www.demparti.org.tr/tr/kadinlarin-katledildigi-ve-emeklerinin-yok-sayildigi-turkiyede-herkesi-ciddiyete-davet-ediyoruz/20728/','2025-02-12','DEM Parti','html'),('aa_komisyon','https://www.aa.com.tr/tr/politika/kadina-karsi-siddet-ve-ayrimciligin-onlenmesine-yonelik-meclis-arastirma-komisyonu-taslak-raporunu-tamamladi/3578151','2025-05-24','Anadolu Ajansı','html')]
out=[]
for name,url,date,publisher,kind in items:
 raw=Path('/tmp/gsd-dem-'+name+'.html').read_bytes();assert (raw.startswith(b'%PDF-'))==(kind=='pdf')
 sha=hashlib.sha256(raw).hexdigest();folder=root/'objects'/sha;folder.mkdir(parents=True,exist_ok=True);original='original.pdf' if kind=='pdf' else 'original.html.bin'
 for fn,body in [(original,raw),('readable.html',readable_bytes(raw,kind,legacy=False))]:
  p=folder/fn
  if p.exists(): assert p.read_bytes()==body
  else:p.write_bytes(body)
 view=None
 if kind=='html':
  view=build_view(raw,url,root,fetch_assets=False);view['version_id']='0406-'+name.replace('_','-')+'-v1';validate_view(root,view)
 out.append(dict(id=name,url=url,date=date,publisher=publisher,accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=sha,mime='application/pdf' if kind=='pdf' else 'text/html',original_path='objects/'+sha+'/'+original,readable_path='objects/'+sha+'/readable.html',view=view))
 print(name,sha,len(raw),None if view is None else view['view_id'],flush=True)
(checks/'commission-captures.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
