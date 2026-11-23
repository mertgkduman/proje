"""10/2881 esas belgesi ve DEM grup konuşması için yerel pasajlar."""
import datetime, hashlib, json
from pathlib import Path
from arsiv import html_source_text, pdf_page_text
c=Path(__file__).resolve().parent
source=c.parents[3]/'data/practices/sources/dem'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
q=lambda s:'0406-textile-2881-'+s
entries=[]
def add(kind,**values): entries.append(dict(kind=kind,values=values))
def passage(name,version,exact,section,index=None): add('passage',id=q(name),version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=index,printed_page=None)
specs=[('register','9fd3ae5c18b74d7a1872328143a01f74b6abbbba18efabc94393ce5814065266','https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/3851a66e-d9a0-4163-86d9-0197d0cb34ae','text/html','original.html.bin'),('signed','906c068f1b94f067387ffcb74a0639cec9b76d52a9180a59f49cd9ddad7505de','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T10/WebOnergeMetni/98284e17-4110-42df-846c-cb35430b1dc9.pdf','application/pdf','original.pdf')]
for suffix,digest,url,mime,filename in specs:
 doc=q(suffix);v=doc+'-v1';p=source/'objects'/digest/filename
 assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
 add('document',id=doc,party_id='dem',title='TBMM 10/2881 '+('esas kaydı' if suffix=='register' else 'imzalı önerge'),source_kind='official')
 add('document_version',id=v,document_id=doc,original_url=url,final_url=url,document_date='2025-07-02',date_precision='day',date_unknown_reason=None,version_label='2 Temmuz 2025 tarihli TBMM işlemi',accessed_at=now,verified_at=now,mime=mime,sha256=digest,original_path='objects/'+digest+'/'+filename,readable_path='objects/'+digest+'/readable.html')
 if suffix=='register':
  view=json.loads((c/'textile-2881-detail-capture.json').read_text())[0]['view'];view['version_id']=v;add('archive_view',**view)
  raw=html_source_text(p.read_bytes())
  for name,exact in [('number','10 / 2881'),('date','02/07/2025'),('status','G&#xFC;ndemde'),('count','Mersin Milletvekili Mehmet Emin Ekmen ve 21 Milletvekili')]:
   assert exact in raw;passage('register-'+name,v,exact,'TBMM esas kaydı '+name)
 else:
  assert '10/2881' in pdf_page_text(p,0);passage('signed-number',v,'10/2881','İmzalı dosya esas numarası',0)
floor=html_source_text((source/'objects'/'84c36043d410905c0227bc2ed17339ecd2fbc94fe0a58c6d0f40ea5afe57a679'/'original.html.bin').read_bytes())
for name,exact,section in [('floor-call','Mehmet Emin Ekmen ve 21 milletvekili','Grup gündem talebinin imzacı sayısı'),('floor-role','DEM PARTİ GRUBU ADINA PERİHAN KOCA (Mersin)','DEM grup konuşmacısı'),('floor-speech','ben bu önergede diğer hatiplerin yaptığı gibi ihracatçıların sorunlarını konuşmayacağım','DEM grup konuşmasında işçi koşullarına odaklanma'),('floor-vote','BAŞKAN - Öneriyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Kabul edilmemiştir.','Ön görüşme gündem talebinin reddi')]:
 assert exact in floor;passage(name,'0406-iklim-final-floor-v1',exact,section)
(c/'textile-2881-source-records.json').write_text(json.dumps({'party_id':'dem','entries':entries},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('TEXTILE_SOURCE_RECORDS_OK',len(entries))
