import json,sys
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent; local=c/'ankara-workshop-emep-sources'; root=Path('data/practices/sources/emep'); now=datetime.now(timezone.utc).isoformat(timespec='seconds'); entries=[]
specs=[
 ('emep','2025-11-03','Emek Partisi','party','party_publication',local/'emep-november.html.bin','710db28b537f9341ec2c24a3a4fb5be7650b8dd72548cbabce930102707be4d6','https://www.emep.org/demokrasi-ve-baris-icin-bulusuyoruz-mucadelenin-olanaklarini-konusuyoruzcalistayi-sonuc-metni','DEM Parti, EHP, EMEP, SMF, TİP ve TÖP olarak düzenlediğimiz'),
 ('dem','2025-11-03','DEM Parti','unknown','other',Path('data/practices/sources/dem/objects/daa8f7ee3a2b7db149f5597ea9f898bac547f3634aae49127b49c988ab4072e5/original.html.bin'),'daa8f7ee3a2b7db149f5597ea9f898bac547f3634aae49127b49c988ab4072e5','https://www.demparti.org.tr/tr/demokrasi-ve-baris-icin-bulusuyoruz-mucadelenin-olanaklarini-konusuyoruz-calistayi-sonuc-metni/22315/',"DEM Parti, EHP, EMEP, SMF, TİP ve TÖP olarak 1-2 Kasım tarihlerinde Ankara'da düzenlediğimiz"),
 ('ilke','2025-11-02','İlke TV','news','journalism',Path('data/practices/sources/dem/objects/94bef19cf3b6aa09b86728a5b83ce64fdbf2620b391b03c3096039a0154abec3/original.html.bin'),'94bef19cf3b6aa09b86728a5b83ce64fdbf2620b391b03c3096039a0154abec3','https://ilketv.com.tr/tayip-temel-chpye-yonelik-saldirilar-surecin-toplumsallasmasini-engelliyor/','Halkların Eşitlik ve Demokrasi Partisi (DEM Parti), Emekçi Hareket Partisi (EHP), Toplumsal Özgürlük Partisi (TÖP), Emek Partisi (EMEP), Türkiye İşçi Partisi (TİP) ve Sosyalist Meclisler Federasyonu’nun (SMF) ortak düzenlediği “Demokrasi ve Barış İçin Buluşuyoruz, Mücadelenin Olanaklarını Konuşuyoruz” başlıklı çalıştay, Ankara Makine Mühendisleri Odası Eğitim ve Kültür Merkezi’nde ikinci gününde devam etti.')]
def add(table,**values): entries.append({'kind':table,'values':values})
for role,day,publisher,skind,akind,path,digest,url,exact in specs:
 raw=path.read_bytes(); assert sha256(raw).hexdigest()==digest; assert exact in html_source_text(raw),(role,exact); obj=root/'objects'/digest;obj.mkdir(parents=True,exist_ok=True); original=obj/'original.html.bin'; readable=obj/'readable.html'
 for target,blob in ((original,raw),(readable,readable_bytes(raw,'html',legacy=False))):
  if target.exists(): assert target.read_bytes()==blob
  else: target.write_bytes(blob)
 doc='0410-ankara-workshop-'+role;ver=doc+'-v1';add('document',id=doc,party_id='emep',title={'emep':'EMEP 3 Kasım ortak çalıştay sonuç metni','dem':'DEM Parti 3 Kasım ortak çalıştay sonuç metni','ilke':'İlke TV çalıştay ikinci günü'}[role],source_kind=skind)
 add('document_version',id=ver,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day',date_unknown_reason=None,version_label='Özgün yayımlanan HTML',accessed_at=now,verified_at=now,mime='text/html',sha256=digest,original_path=str(original.relative_to(root)),readable_path=str(readable.relative_to(root)))
 add('source_attribution',version_id=ver,kind=akind,publisher=publisher,author=None,social_handle=None,published_at=day,date_precision='day',public_url=url,basis='DEM Parti tarafından yayımlanmış ortak metin; başka partinin kaynağı olduğundan other/unknown sınıfında, yayımcı açıkça belirtilmiştir.' if role=='dem' else 'Özgün yayımın gövde ve tarihi incelendi.')
 view=build_view(raw,url,root,fetch_assets=False);view['version_id']=ver;validate_view(root,view);add('archive_view',**view)
 add('passage',id=doc+'-p',version_id=ver,exact=exact,prefix=None,suffix=None,article=None,section={'emep':'Altı kurumun ortak düzenlemesi','dem':'Ankara ve 1–2 Kasım tarihleri','ilke':'Ankarada ikinci gün ve düzenleyiciler'}[role],pdf_page_index=None,printed_page=None)
 print(role,digest)
with (c/'ankara-workshop-emep-source-draft.json').open('x') as f:json.dump({'entries':entries},f,ensure_ascii=False,indent=2);f.write('\n')
print('ANKARA_WORKSHOP_EMEP_CAPTURE_OK',len(entries))
