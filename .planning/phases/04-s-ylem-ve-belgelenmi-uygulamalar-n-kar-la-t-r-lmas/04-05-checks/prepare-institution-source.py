import json, sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text

checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
sources=[
 dict(capture='institution-nisan-capture.json',id='0405-tip-pm-nisan',kind='party_publication',publisher='Türkiye İşçi Partisi',title='6-7 Nisan 2024 Tarihli Parti Meclisi Değerlendirmesi',date=None,passages=[('self-evaluation','parti içi iletişim, katılım ve tartışma kanallarının istenildiği gibi çalışmaması','Örgütsel öz değerlendirme'),('thirtyfive','Çalışma Süresi Haftalık 35 Saate Düşürülsün','Öncelikli somut hedefler')]),
 dict(capture='institution-istifa-capture.json',id='0405-tip-istifa-cumhuriyet',kind='journalism',publisher='Cumhuriyet',title="TİP’in üç il yönetimi istifa etti",date='2024-07-20',author='Haber Merkezi',passages=[('announcement','Bu sebeplerle Türkiye İşçi Partisi\'ndeki görevlerimizden ve parti üyeliğimizden istifa ediyoruz.','Ortak açıklamadaki istifa beyanı'),('criticism','parti merkezi ve yerel örgütler arasındaki diyaloğun kopukluğu','İstifa açıklamasındaki eleştiriler'),('rebuttal','Türkiye İşçi Partisi’nin Amasya İl Örgütü bulunmamaktadır.','Parti basın bürosunun cevabı'),('rebuttal-mdk','TİP Merkez Disiplin Kurulu (MDK) tarafından kesin ihraç kararı verilmiş','Parti basın bürosunun ihraç iddiası')]),
 dict(capture='institution-gazeteci-capture.json',id='0405-tip-gazeteci-yanit',kind='journalism',publisher='Çağdaş Samsun',title='Ümit Özçelik, TİP’nin seni 26 Haziran’da ihraç etmediğini ispatla!',date='2024-07-24',author='Mehmet Rebii Özdemir',passages=[('denial','Parti bizi kesinlikle ihraç etmedi. Partinin bizim hakkımızda almış olduğu ihraç kararı yok','Özçelik’in gazeteciye aktarılan yanıtı'),('self-criticism','Burada kendime bir özeleştiri veriyorum.','Gazetecinin kendi haberiyle ilgili değerlendirmesi')])]
entries=[]
for s in sources:
 r=json.loads((checks/s['capture']).read_text()); digest=r['sha256']; text=html_source_text((Path('data/practices/sources/tip/objects')/digest/'original.html.bin').read_bytes()); vid=s['id']+'-v1'
 def add(kind,values): entries.append(dict(kind=kind,values=values))
 add('document',dict(id=s['id'],party_id='tip',title=s['title'],source_kind=s['kind']))
 add('document_version',dict(id=vid,document_id=s['id'],original_url=r['url'],final_url=r['final_url'],document_date=s['date'],version_label='Yayımlanan sayfanın HTML yakalaması',accessed_at=r['accessed_at'],verified_at=r['accessed_at'],mime='text/html',sha256=digest,original_path=f'objects/{digest}/original.html.bin',readable_path=f'objects/{digest}/readable.html',date_precision='day' if s['date'] else 'unknown',date_unknown_reason=None if s['date'] else 'Toplantı tarihi başlıktadır; sayfanın kesin yayın günü ayrıca doğrulanmalı.'))
 add('archive_view',r['view'])
 add('source_attribution',dict(version_id=vid,kind=s['kind'],publisher=s['publisher'],author=s.get('author'),social_handle=None,published_at=s['date'],date_precision='day' if s['date'] else 'unknown',public_url=r['url'],basis='Kaynağın künye, başlık, yayıncı ve metin bağlamı okundu; taraflara atfedilen ifadeler ayrı korunur.'))
 for pid,exact,section in s['passages']:
  assert exact in text,(s['id'],pid)
  add('passage',dict(id=s['id']+'-'+pid+'-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None))
(checks/'institution-sources-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries),ensure_ascii=False,indent=2)+'\n')
print('DRAFT ONLY',len(entries))
