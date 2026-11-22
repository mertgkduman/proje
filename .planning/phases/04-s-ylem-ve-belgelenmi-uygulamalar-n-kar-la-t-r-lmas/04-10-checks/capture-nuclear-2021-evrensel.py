import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');raw=Path('/tmp/gsd0410-nuclear-2021-evrensel.html').read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);url='https://www.evrensel.net/haber/424002/emep-yol-yakinken-nukleer-santral-felaketinden-vazgecilmelidir';archive='https://web.archive.org/web/20210120110831id_/https://www.evrensel.net/haber/424002/emep-yol-yakinken-nukleer-santral-felaketinden-vazgecilmelidir';ident='0410-emep-nuclear-2021-evrensel';version=ident+'-v1';now=datetime.now(timezone.utc).isoformat(timespec='seconds')
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);text=html_source_text(raw)
exact='Mersin Akkuyu N&uuml;kleer Santral inşatındaki patlamaların &ccedil;evreye ve y&ouml;re halkına verdiği zarar ile ilgili a&ccedil;ıklama yapan Emek Partisi (EMEP) Genel başkan Yardımcısı Sedat Başkavak n&uuml;kleer santral sevdasından vazge&ccedil;me &ccedil;ağrısı yaptı.';assert exact in text
rows=[dict(kind='document',values=dict(id=ident,party_id='emep',title='EMEP: Yol yakınken nükleer santral felaketinden vazgeçilmelidir',source_kind='journalism')),dict(kind='document_version',values=dict(id=version,document_id=ident,original_url=url,final_url=archive,document_date='2021-01-20',date_precision='day',date_unknown_reason=None,version_label='20 Ocak 2021 Evrensel haberi, aynı gün arşiv kopyası',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')),dict(kind='archive_view',values=view),dict(kind='source_attribution',values=dict(version_id=version,kind='journalism',publisher='Evrensel',author='Haber Merkezi',social_handle=None,published_at='2021-01-20',date_precision='day',public_url=url,basis='Evrensel’in tarihli haberinin aynı gün arşivlenen özgün baytları; açıklamayı haberleştirir.')),dict(kind='passage',values=dict(id=ident+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Başkavak’ın nükleer santral çağrısı',pdf_page_index=None,printed_page=None))]
out=Path(__file__).parent/'nuclear-2021-evrensel-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=rows,status='source_read_package_pending',note='20 Ocak 2021 tarihli haber, EMEP genel başkan yardımcısı Sedat Başkavak’ın nükleer santralden vazgeçme çağrısını bildirir. Açıklamanın kesin günü belirtilmedi; kaza, zarar ve ölüm sayıları ilgili aktör iddiası olarak kalır. 2026 Mersin açıklaması ve Kasım 2021 Yusuf Kaya haberi ayrı olaylardır.'),f,ensure_ascii=False,indent=2);f.write('\n')
print(sha,view['view_id'])
