import json,sys
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent; root=Path('data/practices/sources/emep'); source=c/'bakirkoy-2019-sources'; capture=json.loads((source/'capture.json').read_text());now=datetime.now(timezone.utc).isoformat(); entries=[]
def add(k,**v):entries.append({'kind':k,'values':v})
specs=[('hkmo','HKMO İstanbul Şubesi 25. dönem çalışma raporu','official','official','TMMOB Harita ve Kadastro Mühendisleri Odası İstanbul Şubesi',None,'application/pdf','hkmo-istanbul-2018-2020.pdf'),('evrensel','Evrensel: 8 Aralık mitingine çağrı','news','journalism','Evrensel','2019-12-07','text/html','evrensel-392639.html.bin'),('ozgur','Özgür Gelecek: Bakırköy mitingi','news','journalism','Özgür Gelecek','2019-12-08','text/html','ozgurgelecek.html.bin'),('anf','ANF: İstanbulda insanca yaşam mitingi','news','journalism','ANF','2019-12-08','text/html','anf-134433.html.bin')]
for key,title,kind,attribution,publisher,day,mime,filename in specs:
 meta=next(x for x in capture if x.get('file')==filename);raw=(source/filename).read_bytes();digest=sha256(raw).hexdigest();assert digest==meta['sha256'];url=meta['final_url'];obj=root/'objects'/digest;obj.mkdir(parents=True,exist_ok=True);orig=obj/('original.pdf' if mime=='application/pdf' else 'original.html.bin');readable=obj/'readable.html'
 for path,data in ((orig,raw),(readable,readable_bytes(raw,'pdf' if mime=='application/pdf' else 'html',legacy=False))):
  if path.exists():assert path.read_bytes()==data
  else:path.write_bytes(data)
 doc='0410-bakirkoy-2019-'+key;vid=doc+'-v1';unknown=day is None
 add('document',id=doc,party_id='emep',title=title,source_kind=kind)
 add('document_version',id=vid,document_id=doc,original_url=meta['requested_url'],final_url=url,document_date=day,date_precision='unknown' if unknown else 'day',date_unknown_reason='25. dönem raporunun tam yayım günü bilinmiyor; raporda Şubat 2020 yazıyor.' if unknown else None,version_label='Erişilen özgün nüsha; rapor Şubat 2020.' if unknown else 'Erişilen özgün haber.',accessed_at=meta['retrieved_at_utc'],verified_at=now,mime=mime,sha256=digest,original_path=str(orig.relative_to(root)),readable_path=str(readable.relative_to(root)))
 add('source_attribution',version_id=vid,kind=attribution,publisher=publisher,author='Mezopotamya Ajansı' if key=='evrensel' else None,social_handle=None,published_at=day,date_precision='unknown' if unknown else 'day',public_url=url,basis='Şubenin kendi dönemi çalışma raporu ve olay güncesi.' if unknown else ('7 Aralık Evrensel sayfası İstanbul/MA kaynak atfı taşır.' if key=='evrensel' else 'Yayıncının tarihli miting haberi.'))
 if mime=='text/html':
  view=build_view(raw,url,root,fetch_assets=False);view['version_id']=vid;validate_view(root,view);add('archive_view',**view);body=html_source_text(raw)
 else:body=pdf_page_text(orig,99)
 anchors={'hkmo':[('date','Miting tarihi','8 Aralık 2019 tarihinde İstanbul Emek, Demokrasi ve Barış Koordinasyonu'),('place','Bakırköy Halk Pazarı','Bakırköy Halk Pazarında')], 'evrensel':[('identity','Önceki dönem il başkanlığı','Emek Partisi (EMEP) &ouml;nceki d&ouml;nem İstanbul İl Başkanı G&uuml;ven Ger&ccedil;ek'),('invitation','Önceki gün çağrı','halkımızı mitinge davet ediyoruz'),('agency','MA haber atfı','(İstanbul/MA)')], 'ozgur':[('attendance','Mitinge katılan kurumlar','Mitinge DİSK, KESK, TMMOB, TTB, Kaldıraç, HDP ve HDK ile Devrimci Parti, EMEP, BDSP, DİP, ESP, SYKP, SODAP, TÖP, UİD-DER pankart ve bayraklarıyla katıldı.')], 'anf':[('attendance','Mitinge katılanlar','Emek Partisi (EMEP)')]}
 for suffix,section,exact in anchors[key]:
  assert exact in body,(key,suffix,exact)
  add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=99 if key=='hkmo' else None,printed_page='99' if key=='hkmo' else None)
with (c/'bakirkoy-2019-emep-source-records.json').open('x') as f:json.dump({'party_id':'emep','entries':entries},f,ensure_ascii=False,indent=2);f.write('\n')
print('BAKIRKOY_EMEP_CAPTURE_OK',len(entries))
