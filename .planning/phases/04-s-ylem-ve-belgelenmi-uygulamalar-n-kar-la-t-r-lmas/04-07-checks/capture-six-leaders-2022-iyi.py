import datetime, hashlib, json
from pathlib import Path
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

root=Path('data/practices/sources/iyi');here=Path(__file__).resolve().parent;other=here.parent/'04-11-checks';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
sources=[
 ('august','/tmp/gsd-iyi-aug21-karar.html','https://www.karar.com/guncel-haberler/altili-masa-altinci-kez-toplandi-12-subattan-cok-daha-kararli-ve-1682400','2022-08-21','Karar'),
 ('october',str(other/'six-leaders-2022-10-02-independent-original.html'),'https://www.indyturk.com/node/559216/haber/6-lider-chp-genel-merkezinde-bulu%C5%9Ftu-g%C3%B6sterece%C4%9Fimiz-ortak-aday-t%C3%BCrkiye%E2%80%99nin-13','2022-10-02','Independent Türkçe'),
 ('dp-primary',str(other/'six-leaders-2022-08-21-dp-original.html'),'https://dp.org.tr/haber/alti-siyasi-parti-genel-baskaninin-ortak-aciklamasi-ankara-21-agustos-2022','2022-08-21','Demokrat Parti'),
 ('chp-primary',str(other/'six-leaders-2022-10-02-chp-original.html'),'https://chp.org.tr/haberler/alti-siyasi-parti-genel-baskaninin-ortak-aciklamasi-ankara-2-ekim-2022','2022-10-02','Cumhuriyet Halk Partisi')]
result={}
for key,filename,url,day,publisher in sources:
 src=Path(filename);raw=src.read_bytes();h=hashlib.sha256(raw).hexdigest();folder=root/'objects'/h;folder.mkdir(parents=True,exist_ok=True)
 for name,body in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
  target=folder/name
  if target.exists():assert target.read_bytes()==body
  else:target.write_bytes(body)
 view=build_view(raw,url,root,fetch_assets=False);view['version_id']='0407-six-leaders-'+key+'-v1';validate_view(root,view)
 result[key]=dict(url=url,date=day,publisher=publisher,sha256=h,accessed_at=datetime.datetime.fromtimestamp(src.stat().st_mtime,datetime.timezone.utc).isoformat(),original_path=f'objects/{h}/original.html.bin',readable_path=f'objects/{h}/readable.html',view=view)
raw=html_source_text(Path(sources[0][1]).read_bytes());assert '2 Ekim 2022 Pazar günü saat 14.00’da CHP Genel Merkezinde' in raw
raw=html_source_text(Path(sources[1][1]).read_bytes());assert 'İYİ Parti Genel Başkanı Meral Akşener, CHP Genel Merkezi’ne ulaştı.' in raw and 'Saat 14.11’de başlayan görüşmenin' in raw
result['dp-primary']['accessed_at']='2026-11-24T18:11:23.838927+00:00';result['october']['accessed_at']='2026-11-24T18:11:50.066013+00:00'
result['limits']=['21 Ağustos ortak metni DP özgün nüshası ve onu aktaran Karar haberi birlikte okundu; DP yayımcıdır ve İYİ katılımcıdır.','CHP 2 Ekim ortak metni araştırma kopyasıdır; başka parti yayını İYİ yayını olarak kaydedilmez.','14.00 planlanan, 14.11 haberin bildirdiği fiilî başlangıçtır; kararlaştırılan politika uygulaması çıkarılmaz.']
(here/'six-leaders-2022-iyi-capture.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
