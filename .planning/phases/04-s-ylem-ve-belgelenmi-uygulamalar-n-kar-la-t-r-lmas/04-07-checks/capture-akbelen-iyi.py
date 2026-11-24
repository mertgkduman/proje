import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/iyi');here=Path(__file__).resolve().parent;src=here.parent/'04-11-checks/akbelen-2023-tam-original.html'
sources=[('floor',src,'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak20230120/28/1/18/Tam/66113233-be03-41b2-a64a-097e527f8129.html','2023-08-08','TBMM'),('news',Path('/tmp/gsd-iyi-akbelen-bizim.html'),'https://www.bizimankara.com.tr/aksener-26-agustosta-onemli-bir-aciklama-yapacak','2023-08-07','Bizim Ankara'),('anka',Path('/tmp/gsd-iyi-akbelen-anka.html'),'https://ankahaber.net/haber/detay/kursad_zorlu_aksenerin_26_agustosta_aciklama_yapacagini_duyurdu_turk_siyasetinde_onemli_bir_baslangic_olacagini_ifade_etmek_istiyorum_149851','2023-08-07','ANKA')]
result={}
for key,path,url,day,publisher in sources:
 raw=path.read_bytes();h=hashlib.sha256(raw).hexdigest();folder=root/'objects'/h;folder.mkdir(parents=True,exist_ok=True)
 for name,body in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
  p=folder/name
  if p.exists():assert p.read_bytes()==body
  else:p.write_bytes(body)
 view=build_view(raw,url,root,fetch_assets=False);view['version_id']='0407-akbelen-2023-'+key+'-v1';validate_view(root,view)
 result[key]=dict(url=url,date=day,publisher=publisher,sha256=h,accessed_at=datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat(),original_path=f'objects/{h}/original.html.bin',readable_path=f'objects/{h}/readable.html',view=view)
text=html_source_text(src.read_bytes());assert 'İYİ Parti Grubu adına Muğla Milletvekili Metin Ergun.' in text and 'Genel görüşme açılması kabul edilmemiştir.' in text
text=html_source_text(sources[1][1].read_bytes());assert 'yarın TBMM’de olacağız. Bu öneriyi destekleyeceğiz.' in text
result['floor']['accessed_at']='2026-11-24T19:05:34.995610+00:00'
result['limitations']=['7 Ağustos ANKA basın toplantısı haberi ve onu aktaran Bizim Ankara haberi ayrı bağımsız tanıklık olarak sayılmadı.','8/14 genel görüşme açılmaması 4/13 çağrı ve 4/15 devam önergesinden ayrıdır.','Parti grubunun söz alması veya Meclisin sonucu bireysel oy dökümü ve maden izninin iptali değildir.','TBMM özgün erişim zamanı Saadet şeridinin ilk indirme kaydından alındı.']
(here/'akbelen-iyi-capture.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
