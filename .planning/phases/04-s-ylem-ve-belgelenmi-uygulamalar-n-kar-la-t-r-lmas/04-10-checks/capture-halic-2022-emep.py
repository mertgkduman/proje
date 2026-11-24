import json,sys
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent;source=c/'halic-2022-emep-sources';root=Path('data/practices/sources/emep');reading=json.loads((source/'reading.json').read_text());now=datetime.now(timezone.utc).isoformat(timespec='seconds');entries=[]
specs=[
 ('august','2022-08-25','Emek Partisi','party','party_publication','Altı bileşenin ortak halk buluşması kararı',[('six','Altı kurucu bileşen','Emekçi&nbsp;Hareket&nbsp;Partisi&nbsp;(EHP),&nbsp;Emek&nbsp;Partisi&nbsp;(EMEP),&nbsp;HalklarınDemokratik&nbsp;Partisi&nbsp;(HDP),&nbsp;Sosyalist&nbsp;Meclisler&nbsp;Federasyonu(SMF),&nbsp;Türkiye&nbsp;İşçi&nbsp;Partisi&nbsp;(TİP)&nbsp;ve&nbsp;Toplumsal&nbsp;Özgürlük&nbsp;Partisi(TÖP)'),('plan','Eylül sonunda halk buluşması','Kurumlarımızın girişimiyle, Eylül ayı sonunda kitlesel bir halkbuluşması')]),
 ('call','2022-09-14','Emek Partisi','party','party_publication','Ercüment Akdeniz 24 Eylül halk buluşması çağrısı',[('call','24 Eylül tarihli çağrı','24 Eylül’de yapılacak halk buluşmamıza bekliyoruz.'),('declaration','Ortak deklarasyonun ilan hedefi','24 Eylül’de açıklayacağımız ortak deklarasyon bir seçim bildirgesi değildir.')]),
 ('akdeniz','2022-09-25','Emek Partisi','party','party_publication','Ercüment Akdenizin Haliç konuşması',[('speech','EMEP başkanına atfedilen Haliç konuşması','Emek Partisi Genel Başkanı Ercüment Akdeniz&#8217;in Emek ve Özgürlük İttifakı&#8217;nın İstanbul Haliç Kongre Merkezi&#8217;inde gerçekleştirdiği halk buluşmasında yaptığı konuşma:'),('welcome','Konuşmanın açılışı','Türkiye işçi sınıfı hepinize selam olsun.')]),
 ('meeting','2022-09-25','Emek Partisi','party','party_publication','EMEP Haliç buluşması haberi',[('component','Altı ittifak bileşeni ve buluşma','Haliç Kongre Merkezi’nde düzenlediği görkemli halk buluşmasıyla yola çıktı.'),('role','Akdenizin ittifak temsilcisi olarak girişi','İttifak bileşeni partilerinden Emekçi Hareket Partisi Sözcüsü Özge Akman, Emek Partisi Genel Başkanı Ercüment Akdeniz'),('guest','Yeşil Sol temsilcilerinin salonda bulunması','Yeşil Sol Parti Eş Sözcüleri Ayşe Erdem ve İbrahim Akın da salonda yerlerini aldı.')]),
 ('program','2022-09-26','Emek Partisi','party','party_publication','EMEPte ittifak program çerçevesi yayımı',[('published','Haliçte program çerçevesi açıklanması','ittifakın yol haritası olarak da kabul edilen program çerçevesi açıklandı.')]),
 ('bianet','2022-09-24','Bianet','news','journalism','Bianet Haliç halk buluşması haberi',[('meeting','Haliçte yol haritası toplantısı',"Haliç Kongre Merkezi'nde yol haritasını açıklamak üzere toplandı."),('time','Haberin güncel sürümünde başlangıç saati',"Saat 15.30'da başlayan buluşmaya"),('declaration','Halk buluşmasında deklarasyon açıklanması','deklarasyonun </a></strong>açıklanması ile devam etti.')]),
 ('hdp','2022-09-24','Halkların Demokratik Partisi','party','party_publication','HDP Haliç buluşması ve deklarasyon yayını',[('meeting','Haliç halk buluşması','Haliç Kongre Merkezi’nde düzenlediği görkemli halk buluşmasıyla yola çıktı.'),('declaration','Deklarasyon metninin okunması','ittifakın yol haritası olarak kabul edilen deklarasyon metni okundu.')])]
def add(k,**v):entries.append({'kind':k,'values':v})
for role,day,publisher,kind,attribution,title,anchors in specs:
 row=next(x for x in reading['sources'] if x['file']==role+'.html.bin');raw=(source/row['file']).read_bytes();digest=sha256(raw).hexdigest();assert digest==row['sha256'];obj=root/'objects'/digest;obj.mkdir(parents=True,exist_ok=True);orig=obj/'original.html.bin';readable=obj/'readable.html'
 for p,blob in ((orig,raw),(readable,readable_bytes(raw,'html',legacy=False))):
  if p.exists():assert p.read_bytes()==blob
  else:p.write_bytes(blob)
 doc='0410-halic-2022-'+role;ver=doc+'-v1';url=row['url'];add('document',id=doc,party_id='emep',title=title,source_kind=kind)
 add('document_version',id=ver,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day',date_unknown_reason=None,version_label='Erişilen özgün HTML; varsa güncelleme sınırı kaynak açıklamasındadır.',accessed_at=now,verified_at=now,mime='text/html',sha256=digest,original_path=str(orig.relative_to(root)),readable_path=str(readable.relative_to(root)))
 add('source_attribution',version_id=ver,kind=attribution,publisher=publisher,author='Ruken Tuncel' if role=='bianet' else None,social_handle=None,published_at=day,date_precision='day',public_url=url,basis='Erişilen Bianet metni 24 Eylül 23.08 güncellemelidir.' if role=='bianet' else 'Erişilen EMEP program sayfasında 16 Şubat 2023 güncelleme meta verisi bulunur.' if role=='program' else 'Yayıncı, tarih ve metin özgün HTMLde incelendi.')
 view=build_view(raw,url,root,fetch_assets=False);view['version_id']=ver;validate_view(root,view);add('archive_view',**view)
 body=html_source_text(raw)
 for key,section,exact in anchors:
  assert exact in body,(role,key,exact)
  add('passage',id=doc+'-'+key+'-p',version_id=ver,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
 print(role,digest)
with (c/'halic-2022-emep-source-draft.json').open('x') as f:json.dump({'entries':entries},f,ensure_ascii=False,indent=2);f.write('\n')
print('HALIC_2022_EMEP_CAPTURE_OK',len(entries))
