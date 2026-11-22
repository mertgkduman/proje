import json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); root=Path('data/practices/sources/tip')
sources=[
 dict(name='sevk',date='2024-03-05',publisher='HaberTire',author='Ercan Çelik',title='TİP İlçe Başkanlığı, Ali Haydar Öztürk’ü disipline sevk etti',fragments=[('request','“Kesin ihraç talebiyle” Parti Merkez Disiplin Kurulu’na sevk etmiş','İlçe yönetiminin açıklaması'),('suspension','nihai karar alınıncaya kadar Ali Haydar Öztürk’ün örgütsel faaliyetlerinin askıya alınmasına karar vermiştir.','Tedbir ve nihai karar sınırı')]),
 dict(name='yanit',date='2024-03-07',publisher='HaberTire',author='Ercan Çelik',title='TİP Tire İlçe Başkanlığı, Öztürk’ün iddialarına yanıt verdi',fragments=[('reply','kendisinin istifa ettiğini söylese de istifa ettim dediği tarihin disiplin kuruluna sevk edildiği tarih olduğu','İlçe açıklamasında zamanlama itirazı')]),
 dict(name='ozturk',date='2024-03-12',publisher="Ege'ye Bakış",author=None,title="TİP'in vekil adayından TİP'e ağır eleştiri",fragments=[('resignation','Ve istifa ettim.','Öztürk’ün açıklaması')])]
entries=[]
for s in sources:
 r=json.loads((p/('tire-'+s['name']+'-capture.json')).read_text()); digest=r['sha256']; vid='0405-tip-tire-'+s['name']+'-v1'; doc='0405-tip-tire-'+s['name']; raw=(root/'objects'/digest/'original.html.bin').read_bytes(); text=html_source_text(raw)
 def add(kind,values): entries.append(dict(kind=kind,values=values))
 add('document',dict(id=doc,party_id='tip',title=s['title'],source_kind='journalism'))
 add('document_version',dict(id=vid,document_id=doc,original_url=r['url'],final_url=r['final_url'],document_date=s['date'],version_label='Yayım tarihli haberin yakalanan sürümü; güncellemeler ayrıca korunur',accessed_at=r['accessed_at'],verified_at=r['accessed_at'],mime='text/html',sha256=digest,original_path=f'objects/{digest}/original.html.bin',readable_path=f'objects/{digest}/readable.html',date_precision='day',date_unknown_reason=None))
 add('archive_view',r['view'])
 add('source_attribution',dict(version_id=vid,kind='journalism',publisher=s['publisher'],author=s['author'],social_handle=None,published_at=s['date'],date_precision='day',public_url=r['url'],basis='Haber künyesi ve tarafların açıklamaları incelendi.'))
 for key,exact,section in s['fragments']:
  assert exact in text,(s['name'],key)
  add('passage',dict(id=doc+'-'+key+'-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None))
(p/'tire-sources-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries),ensure_ascii=False,indent=2)+'\n');print('DRAFT ONLY',len(entries))
