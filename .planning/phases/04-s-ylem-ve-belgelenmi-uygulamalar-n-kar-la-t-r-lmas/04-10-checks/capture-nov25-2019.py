import json,sys
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent; source=c/'nov25-2019-sources'; root=Path('data/practices/sources/emep'); reading=json.loads((source/'reading.json').read_text()); now=datetime.now(timezone.utc).isoformat(timespec='seconds'); entries=[]
specs=[
 ('emep-3413.html.bin','party','2019-11-25','EMEP 25 Kasım 2019 açıklaması','party','party_publication','Emek Partisi','EMEP Genel Merkezi', [('ban','Vali ve yasakla ilgili parti açıklaması','iktidarın valisi İstanbul 25 Kasım’ını yasaklıyor.'),('call','EMEP kadınları sokağa çağırıyor','tüm kadınları sokaklarda buluşmaya çağırıyoruz')]),
 ('odak-ban.html.bin','ban','2019-11-24','Beyoğlu 24 Kasım yürüyüş yasağı haberi','journalism','journalism','Odak Dergisi',None,[('time','25 Kasım Tünel çağrısı','25.11.2019 günü saat 19:00’da idaremiz Tünel Meydanda'),('decision','Aktarılan 24 Kasım kaymakamlık kararı','Beyoğlu Kaymakamlığının 24/11/2019 tarih ve 34255955.17381.2019/2804 sayılı kararı')]),
 ('gazeteemek-event.html.bin','event','2019-11-25','25 Kasım Tünel yürüyüşü haberi','journalism','journalism','Gazete Emek','Haber Merkezi',[('narrow','Haberde güzergâh ve yasak değişikliği','yürüyüş güzergahını kısaltarak yasağı kaldırdı.'),('walk','Haberde Tünel buluşması','İstanbul 25 Kasım Kadın Platformu, 25 Kasım Kadına Yönelik Şiddetle Mücadele Günü kapsamında Taksim’de bulunan Tünel Meydanı’nda bir araya geldi.'),('police','Haberde sonraki polis müdahalesi','polisler basın açıklamasının ardından dağılan kadınlara biber gazıyla müdahale etti.')]),
 ('tbmm-22-akbasoglu.html.bin','floor',None,'26 Kasım 2019 TBMM 22. birleşimde Akbaşoğlu konuşması','official','official','TBMM Tutanak Hizmetleri Başkanlığı','Muhammet Emin Akbaşoğlu',[('walk','Beyoğlu yürüyüşü hakkında milletvekili beyanı',"Taksim Tüneli'nde başlayan, yaklaşık 100 metre mesafede"),('response','Müdahale hakkında milletvekili beyanı','bu grubun, dağıtılması sağlanmış.')])
]
def add(table,**values):entries.append(dict(kind=table,values=values))
for filename,role,day,title,skind,akind,publisher,author,anchors in specs:
 row=next(v for v in reading['sources'] if v['original_path']==filename);raw=(source/filename).read_bytes();digest=sha256(raw).hexdigest();assert digest==row['sha256'];url=row['url'];obj=root/'objects'/digest;obj.mkdir(parents=True,exist_ok=True);original=obj/'original.html.bin';readable=obj/'readable.html'
 for path,blob in ((original,raw),(readable,readable_bytes(raw,'html',legacy=False))):
  if path.exists():assert path.read_bytes()==blob
  else:path.write_bytes(blob)
 doc='0410-nov25-2019-'+role;ver=doc+'-v1';add('document',id=doc,party_id='emep',title=title,source_kind=skind)
 add('document_version',id=ver,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'TBMM web sayfasının ilk yayımlanma günü bilinmiyor; konuşma tutanağı 26 Kasım 2019 birleşimindedir.',version_label=title,accessed_at=now,verified_at=now,mime='text/html',sha256=digest,original_path=str(original.relative_to(root)),readable_path=str(readable.relative_to(root)))
 add('source_attribution',version_id=ver,kind=akind,publisher=publisher,author=author,social_handle=None,published_at=day,date_precision='day' if day else 'unknown',public_url=url,basis=row['reading'])
 view=build_view(raw,url,root,fetch_assets=False);view['version_id']=ver;validate_view(root,view);add('archive_view',**view)
 text=html_source_text(raw)
 for suffix,section,exact in anchors:
  assert exact in text,(role,suffix)
  add('passage',id=doc+'-'+suffix+'-p',version_id=ver,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
 print(role,digest)
with (c/'nov25-2019-source-draft.json').open('x') as f:json.dump({'entries':entries},f,ensure_ascii=False,indent=2);f.write('\n')
print('NOV25_CAPTURE_OK',len(entries))
