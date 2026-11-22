import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');raw=Path('/tmp/gsd0410-bayhan-plan-2023.html').read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);url='https://tbmm.gov.tr/milletvekili/UyeGenelKurulKonusmalariDetay?eid=118407';ident='0410-emep-bayhan-plan-2023-tbmm';version=ident+'-v1';now=datetime.now(timezone.utc).isoformat(timespec='seconds')
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);text=html_source_text(raw)
passages=[('date','31.10.2023','TBMM konuşma tarihi'),('speech','İSKENDER BAYHAN (İstanbul) - On İkinci Kalkınma Planı, yerli ve yabancı tekelleri, yandaş sermaye gruplarını daha çok kalkındırmanın planıdır. Ülkemizin emperyalizme olan bağımlılığını artırmanın; nükleer santraller, maden ocakları, kentsel dönüşüm politikalarıyla yaşam alanlarımızı ve doğamızı talan etmenin planıdır.','Bayhan’ın On İkinci Kalkınma Planı konuşmasında nükleer santraller'),('party','Emek Partisi olarak bu planı reddediyoruz...','Plan hakkında parti adına ret açıklaması')]
rows=[dict(kind='document',values=dict(id=ident,party_id='emep',title='İskender Bayhan’ın On İkinci Kalkınma Planı konuşması',source_kind='official')),dict(kind='document_version',values=dict(id=version,document_id=ident,original_url=url,final_url=url,document_date='2023-10-31',date_precision='day',date_unknown_reason=None,version_label='TBMM üye konuşması; toplantı günü, yayım günü olarak varsayılmaz',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')),dict(kind='archive_view',values=view),dict(kind='source_attribution',values=dict(version_id=version,kind='official',publisher='Türkiye Büyük Millet Meclisi',author='İskender Bayhan',social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM üye konuşması kaydı, 28. dönem 2. yıl 15. birleşim; konuşma tarihi yayımlanma tarihi değildir.'))]
for suffix,exact,section in passages:
 assert exact in text;rows.append(dict(kind='passage',values=dict(id=ident+'-'+suffix+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)))
out=Path(__file__).parent/'bayhan-development-plan-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=rows,status='source_read_package_pending',note='31 Ekim 2023 Bayhan, On İkinci Kalkınma Planı bağlamında nükleer santralleri eleştiriyor ve EMEP adına planı reddettiğini söylüyor. Bu söz bir oy kaydı, santralın durması veya tek başına tüm plana ilişkin ayrı oylama sonucu değildir.'),f,ensure_ascii=False,indent=2);f.write('\n')
print(sha,view['view_id'])
