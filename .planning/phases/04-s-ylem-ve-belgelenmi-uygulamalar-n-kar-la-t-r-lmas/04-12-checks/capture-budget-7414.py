"""Capture 7414 sources with a cp1254 passive view and a legacy fallback."""
from datetime import datetime, timezone
from hashlib import sha256
import json, sys
from pathlib import Path
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks=Path(sys.argv[1]); source_dir=checks/'budget-7414-sources'; reading=json.loads((source_dir/'reading.json').read_bytes())
root=Path('data/practices/sources/demokrat'); now=datetime.now(timezone.utc).isoformat(timespec='seconds'); case='0412-budget-7414'; entries=[]
rows={r['original_path']:dict(r) for r in reading['sources']}
for item in reading['party_readings']:
 ref=json.loads((source_dir/item['reference']).read_bytes()); row=next(r for r in ref['examined'] if r['position']==item['position']); rows[row['original_path']]=dict(row,retrieved_at_utc=row['accessed_at'])
specs=[
 ('party151','party-news-web/151.html.bin','2022-06-21','Demokrat Parti genel başkanının ek bütçe açıklaması',[('pay',None,"141.453 TL"),('allocation',None,'880.474.775.000 TL')]),
 ('party149','party-news-web/149.html.bin','2022-06-30','Demokrat Parti sözcüsünün ek bütçe açıklaması',[('dated',None,'29 Haziran 2022'),('revenue',None,'1.080.515.421.000 TL')]),
 ('register','tbmm-1-284-sicil.html.bin',None,'1/284 teklif sicili',[('number',None,'1 / 284')]),
 ('proposal','tbmm-1-284-imzali.pdf','2022-06-20','1/284 imzalı ek bütçe teklifi',[('percent',2,'"01.08-Cumhurbaşkanı Ödeneği" ekonomik kodlu tertibe başlangıç ödeneğinin yüzde 20,2\'si'),('total',2,'880.474.775.000 Türk Lirası'),('revenue',2,'1.080.515.421.000 Türk Lirası')]),
 ('debate','tbmm-27-5-109-tutanak.pdf','2022-06-29','TBMM 109. birleşim tutanağı',[('chair',109,'Kullanılan oy sayısı\n:\n383\nKabul\n:\n266\nRet\n:\n117')]),
 ('roll','tbmm-344-acik-oylama.html.bin','2022-06-29','344 sıra sayılı kesin açık oylama cetveli',[]),
 ('adopted','tbmm-7414-kabul-metni.html.bin','2022-06-29','7414 kabul edilen kanun metni',[('total',None,'880.474.775.000 Türk'),('exception',None,'01.08- Cumhurbaşkanı Ödeneği” ekonomik kodlu tertip hariç'),('percentage',None,'40,5’i oranında ödenek eklenmiştir.')]),
 ('lawreg','tbmm-7414-kanun-sicili.html.bin',None,'7414 kanun sicili',[('number',None,'7414')]),
 ('final','tbmm-7490-kesin-hesap.html.bin','2023-12-25','2022 yılı 7490 kesin hesap kanunu',[('spending',None,'2.942.747.714.595,65 Türk lirasıdır.'),('revenue',None,'2.800.087.704.480,03 Türk lirasıdır.')]),
]
def add(table,**values): entries.append({'kind':table,'values':values})
for role,filename,day,title,anchors in specs:
 party=role.startswith('party'); path=(checks if party else source_dir)/filename; row=rows[filename]; raw=path.read_bytes(); digest=sha256(raw).hexdigest(); assert digest==row['sha256']; fmt='pdf' if filename.endswith('.pdf') else 'html'; url=row['url']; final=row.get('retrieved_url',url)
 obj=root/'objects'/digest; obj.mkdir(parents=True,exist_ok=True); original=obj/('original.pdf' if fmt=='pdf' else 'original.html.bin'); readable=obj/'readable.html'
 if role=='roll':
  # Source has no charset declaration; strict Turkish decoding gives the real text.
  decoded=raw.decode('cp1254',errors='strict'); derivative=readable_bytes(raw,'html',legacy=True)
 else: derivative=readable_bytes(raw,fmt,legacy=False)
 for target,blob in ((original,raw),(readable,derivative)):
  if target.exists(): assert target.read_bytes()==blob,target
  else: target.write_bytes(blob)
 doc=case+'-'+role; ver=doc+'-v1'
 add('document',id=doc,party_id='demokrat',title=title,source_kind='party' if party else 'official')
 add('document_version',id=ver,document_id=doc,original_url=url,final_url=final,document_date=day,date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'Sicil görünümünün ilk yayın günü bilinmiyor.',version_label=title,accessed_at=row['retrieved_at_utc'],verified_at=now,mime='application/pdf' if fmt=='pdf' else 'text/html',sha256=digest,original_path=str(original.relative_to(root)),readable_path=str(readable.relative_to(root)))
 add('source_attribution',version_id=ver,kind='party_publication' if party else 'official',publisher=row['publisher'],author=('Gültekin Uysal' if role=='party151' else 'Neslihan Çevik' if role=='party149' else None),social_handle=None,published_at=day,date_precision='day' if day else 'unknown',public_url=url,basis=('Sayfa 30 Haziran tarihli; metin açıklamayı 29 Haziran tarihli olarak sunar.' if role=='party149' else row['reading']))
 if fmt=='html':
  view=build_view(raw,final,root,fetch_assets=False,http_charset='windows-1254' if role=='roll' else None); view['version_id']=ver; validate_view(root,view); add('archive_view',**view)
 for suffix,page,exact in anchors:
  content=html_source_text(raw) if page is None else pdf_page_text(path,page); assert exact in content,(role,suffix,exact)
  add('passage',id=doc+'-'+suffix+'-p',version_id=ver,exact=exact,prefix=None,suffix=None,article=None,section=title+' / '+suffix,pdf_page_index=page,printed_page=None)
 if role=='roll':
  # HTML-source validator defaults to UTF-8 without a charset. Use exact ASCII
  # spans while separately validating the complete rows against cp1254.
  for term,suffix in [('Kabul Edenler','accept'),('Reddedenler','reject'),('Mükerrer Oylar','duplicate'),('UYSAL','uysal'),('ENGİNYURT','enginyurt')]:
   at=decoded.index(term); segment=decoded[at:at+400]; assert {'accept':'265','reject':'117','duplicate':'2','uysal':'KATILMADI','enginyurt':'KATILMADI'}[suffix] in segment
   if suffix=='duplicate': exact=':&nbsp;2</td>'
   elif suffix=='enginyurt': exact=segment[segment.index('<td>Cemal</td>'):segment.index('<td><span>KATILMADI</span>')+len('<td><span>KATILMADI</span>')]
   elif suffix=='uysal': exact=segment[:segment.index('<td><span>KATILMADI</span>')+len('<td><span>KATILMADI</span>')]
   else: exact=term+segment[len(term):segment.index('</td>',segment.index(':&nbsp;'))+5]
   assert exact in html_source_text(raw),(suffix,repr(exact))
   add('passage',id=doc+'-'+suffix+'-p',version_id=ver,exact=exact,prefix=None,suffix=None,article=None,section=title+' / '+suffix,pdf_page_index=None,printed_page=None)
 print(role,digest)

out=checks/'budget-7414-source-draft.json'
with out.open('x') as f:
 json.dump({'status':'source_draft_pending_package_gate','limitations':['Kesin cetvel özgün HTML belgesinde charset yok; Windows-1254 ile doğru çözümlenmiş pasif görünüm esas alınmalı. Mevcut arşiv doğrulayıcısıyla uyumlu legacy readable dosyası UTF-8 yerine koyma karakterleri içerir; özgün baytlar korunur.','Resmî Gazete özgün baytları erişilemedi; kanun metni TBMM kabulü ve siciline dayanır.','Kürsü 266/117, kesin cetvel 265/117/2; önerideki 20,2, kesin metindeki istisna ve fiilî ödeme farklıdır.'], 'entries':entries},f,ensure_ascii=False,indent=2); f.write('\n')
print('DEMOCRAT_7414_SOURCE_DRAFT',len(entries))
