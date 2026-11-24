import json, sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent; local=c/'law-7527-emep-sources'; shared=c.parent/'04-05-checks'/'law-7527-sources'; root=Path('data/practices/sources/emep'); reading=json.loads((local/'reading.json').read_text()); now=datetime.now(timezone.utc).isoformat(timespec='seconds'); entries=[]
specs=[
 ('emep-18-july.html.bin','party','2024-07-18','EMEP: Karaca hayvanların korunması teklifi hakkında',[(None,'context','EMEPli Karacanın komisyon açıklaması','Emek Partisi (EMEP) Milletvekili Sevda Karaca, sokak hayvanlarının öldürülmesinin yolunu açan yasa teklifinin görüşüldüğü Tarım, Orman ve Köyişleri Komisyonu’nda konuştu.'),(None,'withdraw','Geri alınması çağrısı','asıl siz bu kanunu geri alın')]),
 ('floor-112.pdf','floor',None,'TBMM 112. birleşim tam tutanak ve kesin oy cetveli',[(213,'adoption','2/2275 teklifinin kabulü','Teklif kabul edilmiş ve kanunlaşmıştır.'),(213,'chair','Başkanın oturumda açıkladığı sonuç','Kabul\n: 275\nRet\n: 224\nÇekimser\n: 1'),(214,'tally','Kesin cetvel sonuç ve saat','Oylama Saati : 03:46\nÜye Sayısı\n: 600\nKabul Edenler : 273\nReddedenler : 224\nÇekimserler : 1\nGeçersiz Oylar : 0\nMükerrer Oylar : 2\nToplam\n: 500'),(218,'personal','Sevda Karaca Demirin kişisel oyu','Gaziantep Karaca Demir Sevda EMEP Ret')]),
 ('floor-113-correction.pdf','correction',None,'TBMM 113. birleşim Aydoğdu düzeltme talebi',[(70,'request','Aydoğdunun oy kullanamama ve düzeltme talebi','Oyumun rengi “kabul” şeklindedir ve tutanaklara bu şekilde yansıtılması için gereğini arz ederim.\nCengiz AYDOĞDU')]),
 ('law-register.html.bin','register',None,'7527 sayılı kanunun TBMM sicili',[(None,'number','Kanun numarası','7527'),(None,'date','Kabul tarihi','30/07/2024'),(None,'publication','Resmî Gazete yayım günü','02/08/2024'),(None,'issue','Resmî Gazete sayı numarası','32620')])
]
def add(table,**values): entries.append({'kind':table,'values':values})
for filename,role,day,title,anchors in specs:
 row=next(x for x in reading['sources'] if x['path'].endswith('/'+filename) or x['path']==filename); path=local/filename if role=='party' else shared/filename; raw=path.read_bytes(); digest=sha256(raw).hexdigest(); assert digest==row['sha256']; fmt='pdf' if filename.endswith('.pdf') else 'html'; url=row['url']; obj=root/'objects'/digest; obj.mkdir(parents=True,exist_ok=True); original=obj/('original.pdf' if fmt=='pdf' else 'original.html.bin'); readable=obj/'readable.html'
 for target,blob in ((original,raw),(readable,readable_bytes(raw,fmt,legacy=False))):
  if target.exists(): assert target.read_bytes()==blob
  else: target.write_bytes(blob)
 doc='0410-law-7527-emep-'+role; ver=doc+'-v1'; party=role=='party'
 add('document',id=doc,party_id='emep',title=title,source_kind='party' if party else 'official')
 add('document_version',id=ver,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'TBMM elektronik belgesinin ilk yayım tarihi belirlenmedi; birleşim ve kabul tarihleri metinde ayrıdır.',version_label=title,accessed_at=now,verified_at=now,mime='application/pdf' if fmt=='pdf' else 'text/html',sha256=digest,original_path=str(original.relative_to(root)),readable_path=str(readable.relative_to(root)))
 add('source_attribution',version_id=ver,kind='party_publication' if party else 'official',publisher=row['publisher'],author='Sevda Karaca' if party else None,social_handle=None,published_at=day,date_precision='day' if day else 'unknown',public_url=url,basis='EMEP yayımında Sevda Karaca’nın komisyon sözleri aktarılır.' if party else 'TBMM tutanak veya kanun sicili; olayın farklı aşamaları ayrıdır.')
 if fmt=='html':
  view=build_view(raw,url,root,fetch_assets=False); view['version_id']=ver; validate_view(root,view); add('archive_view',**view)
 for page,suffix,section,exact in anchors:
  text=html_source_text(raw) if page is None else pdf_page_text(path,page); assert exact in text,(role,suffix)
  add('passage',id=doc+'-'+suffix+'-p',version_id=ver,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page={('floor',213):'388',('floor',214):'389',('floor',218):'393',('correction',70):'491'}.get((role,page)))
 print(role,digest)
with (c/'law-7527-emep-source-draft.json').open('x') as f: json.dump({'entries':entries},f,ensure_ascii=False,indent=2); f.write('\n')
print('LAW7527_EMEP_CAPTURE_OK',len(entries))
