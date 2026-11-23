"""Önceden yakalanmış 2026 kongre kaynaklarını geçici DEM kayıtlarına dönüştürür."""
from datetime import datetime,timezone
from pathlib import Path
from arsiv import html_source_text
import hashlib,json

c=Path(__file__).resolve().parent
root=c.parents[3]
source=root/'data/practices/sources/dem'
rows=[]
now=datetime.now(timezone.utc).isoformat()
def add(table,**values): rows.append(dict(kind=table,values=values))
for item in json.loads((c/'2026-congress-source-capture.json').read_text()):
 label=item['label']
 if label=='euronews': continue  # Çözülemeyen PM sayısı araştırma notunda korunur.
 raw=(root/item['original']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==item['sha256']
 doc='0406-2026-congress-'+label;vid=doc+'-v1';url=item['url']
 add('document',id=doc,party_id='dem',title={'party':'DEM Parti eş genel başkanlar biyografisi','dw':'DW Türkçe 5. olağan kongre haberi','jin':'JINNEWS kongrede yönetim haberi'}[label],source_kind='party' if label=='party' else 'news')
 add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date='2026-09-06' if label!='party' else None,date_precision='day' if label!='party' else 'unknown',date_unknown_reason=None if label!='party' else 'Güncel biyografi sayfasının yayın tarihi belirtilmedi.',version_label='23 Kasım 2026 tarihinde yakalanan sayfa.',accessed_at=now,verified_at=now,mime='text/html',sha256=item['sha256'],original_path=str((root/Path(item['original'])).relative_to(source)),readable_path=str((root/Path(item['readable'])).relative_to(source)))
 add('source_attribution',version_id=vid,publisher={'party':'DEM Parti','dw':'DW Türkçe','jin':'JINNEWS'}[label],author=None,kind='party_publication' if label=='party' else 'journalism',published_at='2026-09-06' if label!='party' else None,date_precision='day' if label!='party' else 'unknown',social_handle=None,public_url=url,basis='Parti biyografisi veya kongre haberi; seçim tutanağı değildir.')
 view=dict(item['view']);view['version_id']=vid;add('archive_view',**view)
 passages={'party':[('party-result','Parti biyografisinde 2026 seçimi',"6 Eylül 2026'da gerçekleştirilen 5. Olağan Büyük Kongrede DEM Parti Eş Genel Başkanlığına yeniden seçildi.")],
 'dw':[('dw-result','DW haberinde iki başkan ve geçerli oylar','Kongrede yapılan Eş Genel Başkanlık seçiminde Tuncer Bakırhan ve Tülay Hatimoğulları, geçerli 535 oyun tamamını aldı.')],
 'jin':[('jin-result','JINNEWS haberinde kapalı oylama','Yapılan kapalı oylama sonucunda Eş Genel Başkanlar Tülay Hatimoğulları ve Tuncer Bakırhan oy birliği ile tekrar partinin eş genel başkanlığına seçildi.'),('jin-count','JINNEWS haberinde kullanılan ve geçerli oylar','Tek liste ile gidilen seçimlerde 538 kişi oy kullanırken, 535 geçerli 3 geçersiz oy olduğu belirtildi.')]}[label]
 text=html_source_text(raw)
 for key,section,exact in passages:
  assert exact in text,(label,key)
  add('passage',id='0406-2026-congress-'+key,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
(c/'2026-congress-records.json').write_text(json.dumps(dict(party_id='dem',entries=rows),ensure_ascii=False,indent=2)+'\n')
print('KONGRE_KAYNAK',len(rows),'PASS')
