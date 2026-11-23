"""10/2882 esas belgesi ve DEM grup konuşması için yerel pasajlar."""
import datetime, hashlib, json
from pathlib import Path
from arsiv import html_source_text, pdf_page_text
c=Path(__file__).resolve().parent
source=c.parents[3]/'data/practices/sources/dem'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
q=lambda s:'0406-sap-2882-'+s
entries=[]
def add(kind,**values): entries.append(dict(kind=kind,values=values))
def passage(name,version,exact,section,index=None): add('passage',id=q(name),version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=index,printed_page=None)
specs=[('register','d4479239f56a8d3dfb95f9a8ec2546c11e5cbefe3ad4c25c47f6c51403249844','https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/c5be7c5a-af9d-4d9f-bb19-0197d0d18e59','text/html','original.html.bin'),('signed','6184e8293ee649541fcff7792ba5e159a920d4eb5101403f64fab03e456c89cb','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T10/WebOnergeMetni/bb1abb59-4233-4141-9ced-6769f9b2fe72.pdf','application/pdf','original.pdf')]
for suffix,digest,url,mime,filename in specs:
 doc=q(suffix);v=doc+'-v1';p=source/'objects'/digest/filename
 assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
 add('document',id=doc,party_id='dem',title='TBMM 10/2882 '+('esas kaydı' if suffix=='register' else 'imzalı önerge'),source_kind='official')
 add('document_version',id=v,document_id=doc,original_url=url,final_url=url,document_date='2025-07-02',date_precision='day',date_unknown_reason=None,version_label='2 Temmuz 2025 tarihli TBMM işlemi',accessed_at=now,verified_at=now,mime=mime,sha256=digest,original_path='objects/'+digest+'/'+filename,readable_path='objects/'+digest+'/readable.html')
 if suffix=='register':
  view=json.loads((c/'sap-2882-detail-capture.json').read_text())[0]['view'];view['version_id']=v;add('archive_view',**view)
  raw=html_source_text(p.read_bytes())
  for name,exact in [('number','10 / 2882'),('date','02/07/2025'),('status','G&#xFC;ndemde'),('count','Edirne Milletvekili Mehmet Akal&#x131;n ve 20 Milletvekili')]:
   assert exact in raw;passage('register-'+name,v,exact,'TBMM esas kaydı '+name)
 else:
  assert '10/2882' in pdf_page_text(p,0);passage('signed-number',v,'10/2882','İmzalı dosya esas numarası',0)
floor=html_source_text((source/'objects'/'84c36043d410905c0227bc2ed17339ecd2fbc94fe0a58c6d0f40ea5afe57a679'/'original.html.bin').read_bytes())
for name,exact,section in [('floor-call','Edirne Milletvekili Mehmet Akalın ve 19 milletvekili','Grup gündem talebinin imzacı sayısı'),('floor-role','DEM PARTİ GRUBU ADINA BERİTAN GÜNEŞ ALTIN (Mardin)','DEM grup konuşmacısı'),('floor-speech','çözüm için atılacak ilk adımın yaygın ve ücretsiz aşılamaların bir sistematiğe oturtulması','DEM grup konuşmasındaki aşılama çağrısı'),('floor-vote','BAŞKAN - Öneriyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Kabul edilmemiştir.','Ön görüşme gündem talebinin reddi')]:
 assert exact in floor;passage(name,'0406-iklim-final-floor-v1',exact,section)
(c/'sap-2882-source-records.json').write_text(json.dumps({'party_id':'dem','entries':entries},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('SAP_SOURCE_RECORDS_OK',len(entries))
