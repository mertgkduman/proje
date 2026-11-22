from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,re,sys
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

checks,stage=map(Path,sys.argv[1:])
root=Path('data/practices/sources/yeni-yol')
origin=Path('data/practices/sources/yeni-parti')
package=json.loads(Path('data/practices/04-yeni-parti.json').read_bytes())
versions={e['values']['sha256']:e['values'] for e in package['entries'] if e['kind']=='document_version'}
now=datetime.now(timezone.utc).isoformat()
entries=[]; paths=set()
def add(table,**values): entries.append(dict(kind=table,values=values))
def put(relative,content):
   path=root/relative
   path.parent.mkdir(parents=True,exist_ok=True)
   if path.exists(): assert path.read_bytes()==content
   else: path.write_bytes(content)
   paths.add(str(path))
def archive(key,title,day,publisher,meta,raw,passages,charset=None,published=None):
   digest=sha256(raw).hexdigest()
   assert digest==meta['sha256']
   url=meta['final_url']
   doc='0408-mekke-'+key
   version=doc+'-v1'
   orig=f'objects/{digest}/original.html.bin'
   export=f'objects/{digest}/readable.html'
   put(orig,raw)
   if charset:
       put(export,(origin/export).read_bytes())
   else:
       put(export,readable_bytes(raw,'html',legacy=False))
   add('document',id=doc,party_id='yeni-yol',title=title,source_kind='official')
   add('document_version',id=version,document_id=doc,original_url=meta['original_url'],final_url=url,
       document_date=day,date_precision='day',date_unknown_reason=None,version_label='TBMM’nin erişilen özgün HTML kaydı.',
       accessed_at=meta['accessed_at'],verified_at=now,mime='text/html',sha256=digest,original_path=orig,readable_path=export)
   add('source_attribution',version_id=version,publisher=publisher,author=None,kind='official',published_at=published,
       date_precision='day' if published else 'unknown',social_handle=None,public_url=url,
       basis='TBMM sayfasında tarih veya işlem günü görüldü. Yayım tarihi yalnız açıkça verildiğinde kullanıldı.')
   view=build_view(raw,url,root,fetch_assets=False,http_charset=charset)
   view['version_id']=version
   validate_view(root,view)
   add('archive_view',**view)
   manifest=root/view['manifest_path']
   paths.add(str(manifest))
   paths.update(str(manifest.parent/n) for n in json.loads(manifest.read_bytes())['files'])
   s=raw.decode(charset) if charset else html_source_text(raw)
   for name,section,marker,row in passages:
       if row:
           choices=[m.group(1).strip() for m in re.finditer(r'<tr[^>]*>(.*?)</tr>',s,re.S|re.I)
                    if all(value in m.group(1) for value in marker)]
           assert len(choices)==1,(key,name,len(choices))
           exact=choices[0]
       else:
           assert marker in s,(key,name,marker)
           exact=marker
       add('passage',id=doc+'-'+name,version_id=version,exact=exact,prefix=None,suffix=None,
           article=None,section=section,pdf_page_index=None,printed_page=None)
def local(name, url, title, day, snippets, published=None):
   file=stage/name
   raw=file.read_bytes()
   meta=dict(original_url=url,final_url=url,sha256=sha256(raw).hexdigest(),
       accessed_at=datetime.fromtimestamp(file.stat().st_mtime,timezone.utc).isoformat())
   archive(name.removesuffix('.html'),title,day,'TBMM',meta,raw,snippets,published=published)

local('kaya-general','https://tbmm.gov.tr/Haber/Detay?Id=26c3615d-94ce-45c0-8cd0-01a1a85a7357',
      '2/3961 görüşmelerinin 4 Kasım 2026 tarihli TBMM haberi','2026-11-04',[
      ('hasan-karal','Hasan Karal’ın komisyon yetkisine ilişkin görüşü',
       "Yeni Yol Partisi İstanbul Milletvekili Hasan Karal, askeri taahhütler içeren Anlaşma'nın TBMM Milli Savunma Komisyonu'nda da görüşülmesi gerektiğini belirtti.",False),
      ('mustafa-kaya','Mustafa Kaya’nın anlaşma görüşmesindeki kimliği',
       'Teklifin tümü üzerinde konuşan Yeni Yol Partisi İstanbul Milletvekili Mustafa Kaya',False),
      ('nato','Mustafa Kaya’nın başka savunma yükümlülükleri hakkındaki sorusu',
       "NATO ile Mekke Ortak Savunma Anlaşması'nın çıkarları çatıştığında neler yapılacağının düşünülmesi gerektiğini ifade etti.",False),
      ],published='2026-11-04')
local('caliskan-group','https://tbmm.gov.tr/Milletvekili/UyeGenelKurulKonusmalariDetay?eid=149717',
      'Necmettin Çalışkan’ın 5 Kasım 2026 Yeni Yol grubu konuşması','2026-11-05',[
      ('authority','5 Kasım tarihli tutanakta grup adına konuşmacı',
       'YENİ YOL GRUBU ADINA NECMETTİN ÇALIŞKAN (Hatay)',False),
      ('quote','Anlaşmanın gündeme gelişine ilişkin grup adına açıklama',
       'Mekke isimli anlaşmanın NATO toplantısını müteakiben apar topar devreye girdiğini gördük.',False),
      ])
local('kaya-response.html','https://tbmm.gov.tr/Milletvekili/UyeGenelKurulKonusmalariDetay?eid=149716',
      'Bülent Kaya’nın 5 Kasım 2026 değişiklik önergesi konuşması','2026-11-05',[
      ('speaker','Bülent Kaya’nın değişiklik önergesi bağlamında aldığı söz',
       "BÜLENT KAYA (İstanbul) - Sayın Başkan, değerli milletvekilleri; Mekke Anlaşması'yla ilgili önergemiz hakkında söz almış bulunuyorum.",False),
      ])
local('kaya-vote-explanation','https://tbmm.gov.tr/Milletvekili/UyeGenelKurulKonusmalariDetay?eid=149734',
      'Bülent Kaya’nın anlaşma metnine ilişkin 5 Kasım 2026 açıklaması','2026-11-05',[
      ('quote','Kaya’nın anlaşma metni ve oy tercihi hakkındaki açıklaması',
       'bu belirsizlikleri içeren anlaşmaya evet dememizin mümkün olmadığını, hayır diyeceğimizi',False),
      ])
local('mekke-general-result','https://tbmm.gov.tr/Haber/mekke-anlasmasi-nin-onaylanmasinin-20261106003056',
      'Mekke Anlaşması için onay teklifinin kabulüne ilişkin TBMM haberi','2026-11-06',[
      ('result','TBMM Genel Kurulunda teklifin kabulü','TBMM Genel Kurulunda kabul edildi.',False),
      ('birol','Yeni Yol milletvekili Birol Aydın’ın 5 Kasım Genel Kurul konuşması',
       'Yeni Yol Partisi İstanbul Milletvekili Birol Aydın, milletvekillerinden',False),
      ],published='2026-11-06')
ballot='dee8048e3732d2414f3db05c106dfa60b39b8d7a92cff70bb31198527e0939da'
original=versions[ballot]
raw=(origin/original['original_path']).read_bytes()
s=raw.decode('windows-1254')
rows=[m.group(1).strip() for m in re.finditer(r'<tr[^>]*>(.*?)</tr>',s,re.S|re.I)
      if '>Yeni Yol Partisi</td>' in m.group(1)]
votes = []
from collections import Counter
from html import unescape
for i, row in enumerate(rows, 1):
   cells=[unescape(re.sub(r'<[^>]+>','',cell)).strip() for cell in re.findall(r'<td[^>]*>(.*?)</td>',row,re.I|re.S)]
   il,last,name,party,system,paper,result,date,clock=cells
   key=f'row-{i:02}'
   if (name,last)==('Bülent','KAYA'): key='bulent'
   if (name,last)==('Ertuğrul','KAYA'): key='ertugrul'
   if (name,last)==('Necmettin','ÇALIŞKAN'): key='necmettin'
   votes.append((key,il,last,name,system,paper,result,date,clock,row))
assert len(votes)==20
assert Counter(v[6] for v in votes)=={'RET':15,'KABUL':1,'KATILMADI':4}
assert Counter((v[4],v[5]) for v in votes)=={('RET','-'):12,('KABUL','-'):1,('KATILMADI','RET'):3,('KATILMADI','-'):4}
archive('ballot','TBMM 14. Birleşim 2/3961 açık oy cetveli','2026-11-05','TBMM Tutanak Hizmetleri Başkanlığı',
        original,raw,[
        ('accept','2/3961 kabul oyları',('Kabul Edenler','277'),True),
        ('reject','2/3961 ret oyları',('Reddedenler','118'),True),
        ('duplicate','2/3961 mükerrer oy sırası',('kerrer Oylar','3'),True),
        *[(key,f'{il} {name} {last} — sistem, pusula ve sonuç sütunları',(row,),True)
          for key,il,last,name,system,paper,result,date,clock,row in votes],
        ],charset='windows-1254')
bid='544abf6f551583fc66bd775a25a35dab91fd6cc8659cd10f7d314dd0e051243f'
original=versions[bid]
archive('bill','Mekke Anlaşması onayının uygun bulunmasına ilişkin 2/3961 yasama kaydı','2026-10-21','TBMM',
        original,(origin/original['original_path']).read_bytes(),[
        ('esas','TBMM kanun teklifi esas numarası','2 / 3961',False),
        ])
out=checks/'mekke-source-records.json'
with out.open('x') as f:
   f.write(json.dumps(dict(party_id='yeni-yol',entries=entries,vote_columns=['passage_id','il','soyad','ad','sistem','pusula','sonuc','tarih','saat'],
       vote_rows=[['0408-mekke-ballot-'+v[0],*v[1:-1]] for v in votes]),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0408-mekke-source-paths').write_text('\n'.join(sorted(paths))+'\n')
print(len(entries),len(paths),sha256(out.read_bytes()).hexdigest())
