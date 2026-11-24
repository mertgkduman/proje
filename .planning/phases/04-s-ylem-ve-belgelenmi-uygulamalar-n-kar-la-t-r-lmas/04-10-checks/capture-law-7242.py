import json, sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
checks=Path(__file__).resolve().parent; sources=checks/'law-7242-sources'; root=Path('data/practices/sources/emep')
reading=json.loads((sources/'reading.json').read_text()); now=datetime.now(timezone.utc).isoformat(timespec='seconds'); entries=[]
specs=[
 ('emep-3527.html.bin','joint','2020-04-06','İnfaz teklifi hakkında çok partili açıklama',[(None,'sign','Ortak açıklamadaki EMEP imzası','EMEK PARTİSİ')]),
 ('emep-3531.html.bin','prior','2020-04-08','Selma Gürkan infaz teklifi açıklaması',[(None,'request','Geri çekme çağrısı','infaz düzenlemesi geri çekilmeli'),(None,'author','Açıklamanın imzası','SELMA GÜRKAN')]),
 ('emep-3562.html.bin','after','2020-04-14','EMEP Genel Merkezi kabul sonrası değerlendirmesi',[(None,'accepted','Kabul sonrası parti açıklaması','Meclis’te kabul edilen İnfaz Yasası')]),
 ('tbmm-2-2762-sicil.html.bin','proposal',None,'2/2762 teklif sicili',[(None,'number','Teklif esas numarası','2 / 2762'),(None,'sequence','Sicilde sıra sayısı','207</a>'),(None,'law','Sicilde kanun numarası','7242')]),
 ('tbmm-27-3-84-tutanak.pdf','floor',None,'13 Nisanda açılan TBMM 84. birleşim tutanağı',[(0,'opening','13 Nisan birleşim tarihi','13 Nisan 2020 Pazartesi'),(68,'request','207 sıra sayısında açık oylama isteği','207 sıra sayılı Kanun Teklifi’nin tümü üzerindeki oylamanın'),(68,'vote','Oylama sayımı','Oy sayısı :330\nKabul\n:279\nRet\n:51'),(69,'accepted','Teklifin kabulü','Teklif kabul edilmiş ve kanunlaşmıştır.')]),
 ('tbmm-27-3-84-basilmis.pdf','printed',None,'13 Nisanda açılan TBMM birleşiminin basılı oylama cetveli',[(158,'header','Kesin cetvelin basılı sayfa başlığı','IX.- OYLAMALAR')]),
 ('tbmm-7242-kabul.html.bin','law','2020-04-14','7242 kabul edilen kanun metni',[(None,'m48','48. madde koşullu salıverilme genel oran değişikliği','“üçte ikisini” ibaresi\r\n“yarısını” şeklinde değiştirilmiş'),(None,'m48-exceptions','48. madde belirli kategorilerin oranı','cezalarının üçte\r\nikisini infaz kurumunda çektikleri takdirde'),(None,'m52-date','52. madde geçici denetimli serbestlik tarih eşiği','30/3/2020 tarihine kadar işlenen suçlar bakımından'),(None,'m52-exclusions','52. madde belirli istisnalar','Terörle Mücadele Kanunu kapsamına giren suçlar hariç olmak üzere, 105/A'),(None,'m53-leave','53. madde salgın izni','31/5/2020 tarihine kadar izinli sayılır.'),(None,'m53-discipline','53. madde disiplin düzeni','verilen disiplin cezası ve tedbirleri,'),(None,'m68','68. madde yürürlük','Bu Kanun yayımı\r\ntarihinde yürürlüğe girer.')]),
 ('tbmm-7242-kanun-sicili.html.bin','registry',None,'7242 kanun sicili',[(None,'adoption','Kabul tarihi','14/04/2020'),(None,'publication','Resmî Gazete tarihi','15/04/2020'),(None,'issue','Resmî Gazete sayısı','31100')]),
]
def add(table,**values): entries.append({'kind':table,'values':values})
for filename,role,day,title,anchors in specs:
 row=next(x for x in reading['sources'] if x['original_path']==filename); raw=(sources/filename).read_bytes(); digest=sha256(raw).hexdigest(); assert digest==row['sha256']; fmt='pdf' if filename.endswith('.pdf') else 'html'; url=row['url']; final=row.get('retrieved_url',url); obj=root/'objects'/digest; obj.mkdir(parents=True,exist_ok=True); original=obj/('original.pdf' if fmt=='pdf' else 'original.html.bin'); readable=obj/'readable.html'
 for path,blob in ((original,raw),(readable,readable_bytes(raw,fmt,legacy=False))):
  if path.exists(): assert path.read_bytes()==blob
  else: path.write_bytes(blob)
 doc='0410-law-7242-'+role; ver=doc+'-v1'; isparty=role in ('joint','prior','after')
 add('document',id=doc,party_id='emep',title=title,source_kind='party' if isparty else 'official')
 add('document_version',id=ver,document_id=doc,original_url=url,final_url=final,document_date=day,date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'Belgenin ilk yayımlanma günü belirlenmedi; tutanağın 13 Nisan başlığı birleşimin açılış günüdür.' if role in ('floor','printed') else 'Sicilin ilk yayımlanma günü belirlenmedi.',version_label=title,accessed_at=row['retrieved_at_utc'],verified_at=now,mime='application/pdf' if fmt=='pdf' else 'text/html',sha256=digest,original_path=str(original.relative_to(root)),readable_path=str(readable.relative_to(root)))
 add('source_attribution',version_id=ver,kind='party_publication' if isparty else 'official',publisher=row['publisher'],author=('Selma Gürkan' if role=='prior' else 'Çok partili ortak açıklama' if role=='joint' else 'EMEP Genel Merkezi' if role=='after' else None),social_handle=None,published_at=day,date_precision='day' if day else 'unknown',public_url=url,basis=row['reading'])
 if fmt=='html':
  view=build_view(raw,final,root,fetch_assets=False); view['version_id']=ver; validate_view(root,view); add('archive_view',**view)
 for page,suffix,section,exact in anchors:
  content=html_source_text(raw) if page is None else pdf_page_text(sources/filename,page); assert exact in content,(role,suffix)
  add('passage',id=doc+'-'+suffix+'-p',version_id=ver,exact=exact,prefix=None,suffix=None,article={'m48':'48','m48-exceptions':'48','m52-date':'52','m52-exclusions':'52','m53-leave':'53','m53-discipline':'53','m68':'68'}.get(suffix),section=section,pdf_page_index=page,printed_page='383' if role=='printed' else None)
 print(role,digest)
out=checks/'law-7242-source-draft.json'
with out.open('x') as f: json.dump({'entries':entries,'visual_limit':'Basılı s.383 metin katmanı yalnız başlığı içerir; 00.09 ve 279/51/330 özgün görüntüden okundu, tutanak sayımı ve sicil ile karşılaştırıldı. Gültekin Uysal satırı Katılmadı; ilk okuma makbuzundaki Kabul ifadesi hatalıdır.','signed_scan':'İmzalı teklif bu taslağa alınmadı; 31 Mart sevki kaynak okuma makbuzunda açık.'},f,ensure_ascii=False,indent=2); f.write('\n')
print('LAW7242_SOURCE_CAPTURE_OK',len(entries))
