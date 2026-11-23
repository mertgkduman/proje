"""7 Eylül 2026 PM toplantısı için ayrı haber sürümleri ve pasajlar."""
from datetime import datetime,timezone
from pathlib import Path
from hashlib import sha256
from arsiv import html_source_text
import json
c=Path(__file__).resolve().parent
root=c.parents[3]
source=root/'data/practices/sources/dem'
rows=[];now=datetime.now(timezone.utc).isoformat()
def add(table,**values):rows.append(dict(kind=table,values=values))
for label,item in zip(('mezopotamya','independent'),json.loads((c/'2026-pm-myk-capture.json').read_text())):
 raw=(root/item['object']/'original.html.bin').read_bytes();assert sha256(raw).hexdigest()==item['sha256']
 doc='0406-2026-pm-myk-'+label;vid=doc+'-v1';url=item['url'];pub='Mezopotamya Ajansı' if label=='mezopotamya' else 'Independent Türkçe'
 add('document',id=doc,party_id='dem',title=pub+' 7 Eylül Parti Meclisi toplantısı haberi',source_kind='news')
 add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date='2026-09-07',date_precision='day',date_unknown_reason=None,version_label='23 Kasım 2026 tarihinde yakalanan haber.',accessed_at=now,verified_at=now,mime='text/html',sha256=item['sha256'],original_path=str((root/item['object']/'original.html.bin').relative_to(source)),readable_path=str((root/item['object']/'readable.html').relative_to(source)))
 add('source_attribution',version_id=vid,publisher=pub,author=None,kind='journalism',published_at='2026-09-07',date_precision='day',social_handle=None,public_url=url,basis='Haber parti açıklamasına dayanır; toplantı tutanağı sunulmadı.')
 v=dict(item['view']);v['version_id']=vid;add('archive_view',**v)
 if label=='mezopotamya':
  s=html_source_text(raw)
  for key,section,exact in [('meeting','Parti Meclisi toplantısı','Olağan Büyük Kongresi sonrası Eş Genel Başkanlar Tülay Hatimoğulları ve Tuncer Bakırhan başkanlığında gerçekleştirilen Parti Meclisi (PM) toplantısı sona erdi.'),('announcement','Basın komisyonunun bildirdiği belirleme','DEM Parti Basın Komisyonu partinin yeni Merkez Yürütme Kurulu (MYK) üyelerinin belirlendiği bilgisini paylaştı.'),('women','Ayrı kadın meclisi toplantısı',"Aynı zamanda Kadın Meclisi de toplandı. Toplantıda Kadın Meclisi Sözcü olarak Halide Türkoğlu seçilirken, yeni dönem Kadın Koordinasyonu'nda yer alacak isimler de belirlendi.")]:
   assert exact in s
   add('passage',id='0406-2026-pm-myk-'+key,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
(c/'2026-pm-myk-records.json').write_text(json.dumps(dict(party_id='dem',entries=rows),ensure_ascii=False,indent=2)+'\n')
print('PM_MYK_PASS',len(rows))
