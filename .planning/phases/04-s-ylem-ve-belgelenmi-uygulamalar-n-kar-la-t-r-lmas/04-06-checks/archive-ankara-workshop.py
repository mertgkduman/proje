import datetime, hashlib, json
from pathlib import Path
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root=Path('data/practices/sources/dem')
checks=Path(__file__).resolve().parent
sources=[
 ('dem','https://www.demparti.org.tr/tr/demokrasi-ve-baris-icin-bulusuyoruz-mucadelenin-olanaklarini-konusuyoruz-calistayi-sonuc-metni/22315/',Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/tip-publication-catalog/party-statements-02/015-dem.html.bin'),'2025-11-03','2026-11-24T16:32:56.056585+00:00'),
 ('ilke','https://ilketv.com.tr/tayip-temel-chpye-yonelik-saldirilar-surecin-toplumsallasmasini-engelliyor/',Path('/tmp/gsd-dem-ankara-2025-ilke.html'),'2025-11-02',datetime.datetime.now(datetime.timezone.utc).isoformat()),
]
result={}
for key,url,source,date,accessed in sources:
 raw=source.read_bytes(); text=html_source_text(raw)
 if key=='dem': assert 'DEM Parti, EHP, EMEP, SMF, TİP ve TÖP olarak 1-2 Kasım' in text and '3 Kasım 2025' in text
 else: assert 'başlıklı çalıştay, Ankara Makine Mühendisleri Odası Eğitim ve Kültür Merkezi’nde ikinci gününde devam etti.' in text and '2 Kasım 2025 14:15' in text
 sha=hashlib.sha256(raw).hexdigest(); folder=root/'objects'/sha;folder.mkdir(parents=True,exist_ok=True)
 for name,body in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
  p=folder/name
  if p.exists(): assert p.read_bytes()==body
  else:p.write_bytes(body)
 view=build_view(raw,url,root,fetch_assets=False);view['version_id']='0406-ankara-workshop-'+key+'-v1';validate_view(root,view)
 result[key]=dict(url=url,date=date,accessed_at=accessed,sha256=sha,original_path=f'objects/{sha}/original.html.bin',readable_path=f'objects/{sha}/readable.html',view=view)
result['notes']=['DEM kaynak baytları TİP kataloğundaki 24 Kasım 2026 capture kopyasıdır; özgün erişim zamanı katalog makbuzundan alındı.','İlke TV 2 Kasım tarihli haberi ikinci günün sürdüğünü bildirir; haber ajansı kaynak zinciri ayrıca kontrol edilmelidir.','3 Kasım DEM yayın tarihidir; sonuç bildirgesinin ilk kez o tarihte açıklandığı varsayılmaz.']
(checks/'ankara-workshop-capture.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
