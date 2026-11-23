import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes, pdf_page_text
from arsiv_gorunum import build_view, validate_view

D = Path(__file__).parent
root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
 ('detail-20147', 'html', 'https://www.tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/dec9e2a5-5d1d-4834-88b5-01939b90865d', None, None),
 ('question-20147', 'pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/a6de5f52-2382-4127-a713-42669caf403e.pdf', '2024-12-05', 'İskender Bayhan'),
 ('reply-20147', 'pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/c18099ea-4fc5-4e43-86a6-8b627984d882.pdf', '2025-08-25', 'Çalışma ve Sosyal Güvenlik Bakanlığı'),
 ('detail-21425', 'html', 'https://www.tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/fd2a4c7c-2986-470a-b7fa-019407004ef6', None, None),
 ('question-21425', 'pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/174390f1-730f-4eb2-836f-c19d2b272073.pdf', '2024-12-26', 'İskender Bayhan'),
 ('reply-21425', 'pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/badeae81-a349-40ba-840f-75463e530975.pdf', '2025-10-23', 'Çalışma ve Sosyal Güvenlik Bakanlığı'),
]
entries=[]
for role, typ, url, date, author in sources:
 raw=(D/'betek-20147-21425'/(role+('.html' if typ=='html' else '.pdf'))).read_bytes()
 digest=hashlib.sha256(raw).hexdigest(); obj=root/'objects'/digest; obj.mkdir(parents=True, exist_ok=True)
 original='original.html.bin' if typ=='html' else 'original.pdf'
 for name, content in [(original,raw),('readable.html',readable_bytes(raw,typ,legacy=False))]:
  path=obj/name
  if path.exists(): assert path.read_bytes()==content
  else: path.write_bytes(content)
 doc='0410-emep-betek-'+role; version=doc+'-v1'
 entries.append(dict(kind='document',values=dict(id=doc,party_id='emep',title='TBMM Betek '+role,source_kind='official')))
 entries.append(dict(kind='document_version',values=dict(id=version,document_id=doc,original_url=url,final_url=url,document_date=date,date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Yayın günü doğrulanmadı.',version_label='TBMM özgün kaydı',accessed_at=now,verified_at=now,mime='text/html' if typ=='html' else 'application/pdf',sha256=digest,original_path='objects/'+digest+'/'+original,readable_path='objects/'+digest+'/readable.html')))
 if typ=='html':
  view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8'); view['version_id']=version; validate_view(root,view); entries.append(dict(kind='archive_view',values=view))
  number=role.split('-')[1]
  for key,exact in [('number','7 / '+number),('date',{'20147':'05.12.2024','21425':'26.12.2024'}[number]),('reply',{'20147':'01.09.2025','21425':'24.10.2025'}[number])]:
   assert exact in html_source_text(raw)
   entries.append(dict(kind='passage',values=dict(id=doc+'-'+key+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Soru ve yanıt bildirim kaydı',pdf_page_index=None,printed_page=None)))
 if role.startswith('question'):
  txt=pdf_page_text(obj/original,0)
  exact={'question-20147':'çalıştığı Betek Boya fabrikasında yaşanmıştır. Petrol-İş Gebze Şubesinin çoğunluğu sağlayarak', 'question-21425':'Toplamda 88 işçinin işine son verilen fabrikada, yaklaşık 450 işçi üretimi durdurarak fabrika içinde'}[role]
  assert exact in txt
  entries.append(dict(kind='passage',values=dict(id=doc+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Yazılı soru, birinci sayfa',pdf_page_index=0,printed_page=None)))
 entries.append(dict(kind='source_attribution',values=dict(version_id=version,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=author,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM özgün kaydı; belge tarihi ile bildirim tarihi ayrı. İki taranmış yanıtın ilk sayfası görsel okundu.')))
 print(role,digest)
with (D/'betek-20147-21425-source-draft.json').open('x') as f:
 json.dump(dict(status='source_read_package_pending',entries=entries,note='5 ve 26 Aralık 2024 tarihli iki ayrı soru; 25 Ağustos ve 23 Ekim 2025 yanıtları ile 1 Eylül ve 24 Ekim bildirimleri ayrı. İkinci yanıt 16 Temmuz yetki belgesi ve 18 Temmuz 2025 sözleşmeyi bildirir; ilk genel yanıtla ayrı tutulur.'),f,ensure_ascii=False,indent=2); f.write('\n')
