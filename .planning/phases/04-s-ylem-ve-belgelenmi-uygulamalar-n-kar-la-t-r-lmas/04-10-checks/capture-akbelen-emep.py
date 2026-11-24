import json,sys
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent;source=c/'akbelen-emep-sources';root=Path('data/practices/sources/emep');reading=json.loads((source/'reading.json').read_text());now=datetime.now(timezone.utc).isoformat(timespec='seconds');entries=[]
specs=[
 ('party','2023-07-29','Emek Partisi','party','party_publication','EMEP Akbelen dayanışma açıklaması',[(None,'support','İkizköylülere dayanışma','Milas’ta Akbelen ormanlarının kömür madeni için kesilmesine karşı çıkan İkizköylüler’in ve onlarla dayanışma içinde olan yöre halkının yanındayız.')]),
 ('press','2023-08-04','Başkent Gazetesi','news','journalism','Başkent Gazetesi 4 Ağustos 2023',[(1,'speaker','EMEPli Karaca ve çağrı','EMEP Dilok Milletvekili Sevda Karaca Demir, do-\nğanın'),(1,'call','Meclisi olağanüstü toplama çağrısı',"Demir, Meclis'i olağan-\nüstü toplanmaya çağırdıklarını belirterek"),(1,'quote','Akbelen forumu hakkında aktarılan söz','Bu çağrı Akbelen’de yaptığımız forumda\nkatılımcılar tarafından dile getirildi.')]),
 ('floor',None,'TBMM Tutanak Hizmetleri Başkanlığı','official','official','TBMM 8 Ağustos 2023 18. birleşim',[(None,'invitation','3 Ağustos Başkanlık daveti','8 Ağustos 2023 Salı günü 15.00’te olağanüstü toplantıya çağırıyorum.'),(None,'invitation-date','Başkanlık çağrısı tarihi','3/8/2023'),(None,'opening','8 Ağustos oturumu açılış saati','Açılma Saati: 15.01'),(None,'quorum','Açılışta toplantı yeter sayısı','Sayın milletvekilleri, toplantı yeter sayısı vardır.'),(None,'continuation','Ayrı 4/15 devam önergesi','Saadet Partisi Grubunun Türkiye Büyük Millet Meclisinin çalışmalarına devam etmesine dair İç Tüzük’ün 7’nci maddesinin son fıkrasına göre verilmiş önergesi (4/15)'),(None,'debate','Ayrı 8/14 genel görüşme önergesi','Muğla’da bulunan Akbelen Ormanı’nda maden arama faaliyeti için yapılan ağaç kesimi konusunda bir genel görüşme açılmasına ilişkin önergesi (8/14)')])]
def add(table,**values):entries.append({'kind':table,'values':values})
for role,day,publisher,skind,akind,title,anchors in specs:
 row=next(x for x in reading['sources'] if x['id']==role);path=source/row['original'];raw=path.read_bytes();digest=sha256(raw).hexdigest();assert digest==row['sha256'];fmt='pdf' if path.suffix=='.pdf' else 'html';obj=root/'objects'/digest;obj.mkdir(parents=True,exist_ok=True);original=obj/('original.pdf' if fmt=='pdf' else 'original.html.bin');readable=obj/'readable.html'
 for target,blob in ((original,raw),(readable,readable_bytes(raw,fmt,legacy=False))):
  if target.exists():assert target.read_bytes()==blob
  else:target.write_bytes(blob)
 doc='0410-akbelen-meeting-'+role;ver=doc+'-v1';add('document',id=doc,party_id='emep',title=title,source_kind=skind);add('document_version',id=ver,document_id=doc,original_url=row['url'],final_url=row['url'],document_date=day,date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'Tutanağın ilk elektronik yayın tarihi belirlenmedi; toplantı tarih ve saati tutanakta.',version_label=title,accessed_at=now,verified_at=now,mime='application/pdf' if fmt=='pdf' else 'text/html',sha256=digest,original_path=str(original.relative_to(root)),readable_path=str(readable.relative_to(root)))
 add('source_attribution',version_id=ver,kind=akind,publisher=publisher,author='Sedat Başkavak' if role=='party' else None,social_handle=None,published_at=day,date_precision='day' if day else 'unknown',public_url=row['url'],basis='Sedat Başkavak imzalı parti yayımı' if role=='party' else '4 Ağustos baskısında Karaca Demirin sözü aktarılır; konuşmanın günü açık verilmez.' if role=='press' else 'TBMM birleşim tutanağında tarih ve saatler ayrı okunur.')
 if fmt=='html':
  view=build_view(raw,row['url'],root,fetch_assets=False);view['version_id']=ver;validate_view(root,view);add('archive_view',**view)
 for page,suffix,section,exact in anchors:
  text=html_source_text(raw) if page is None else pdf_page_text(path,page);assert exact in text,(role,suffix)
  add('passage',id=doc+'-'+suffix+'-p',version_id=ver,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page='2' if page is not None else None)
 print(role,digest)
with (c/'akbelen-emep-source-draft.json').open('x') as f:json.dump({'entries':entries},f,ensure_ascii=False,indent=2);f.write('\n')
print('AKBELEN_EMEP_CAPTURE_OK',len(entries))
