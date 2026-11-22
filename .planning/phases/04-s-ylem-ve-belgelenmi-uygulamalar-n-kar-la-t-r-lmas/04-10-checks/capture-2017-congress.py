import datetime, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
root=Path('data/practices/sources/emep');raw=Path('/tmp/gsd0410-congress-2017-next.html').read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    dest=obj/name
    if dest.exists():assert dest.read_bytes()==content
    else:dest.write_bytes(content)
url='https://www.evrensel.net/haber/338968/emep-8-kongresi-tek-adam-rejimine-karsi-ortak-mucadele';archive='https://web.archive.org/web/20191118105258id_/https://www.evrensel.net/haber/338968/emep-8-kongresi-tek-adam-rejimine-karsi-ortak-mucadele';ident='0410-emep-2017-congress-report';version=ident+'-v1';now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view)
s=html_source_text(raw);start=s.find('Emek Partisi Genel başkanlığına');exact=s[start:s.find('</p>',start)];assert start>=0 and exact.endswith('se&ccedil;ildi.') and 'Selma G&uuml;rkan' in exact
entries=[{'kind':'document','values':dict(id=ident,party_id='emep',title='EMEP 8. Kongresi: Tek adam rejimine karşı ortak mücadele — Evrensel',source_kind='journalism')},{'kind':'document_version','values':dict(id=version,document_id=ident,document_date='2017-11-26',date_precision='day',date_unknown_reason=None,version_label='26 Kasım 2017 tarihli Evrensel haberi ve 18 Kasım 2019 arşiv görüntüsü',original_url=url,final_url=archive,accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')},{'kind':'archive_view','values':view},{'kind':'source_attribution','values':dict(version_id=version,publisher='Evrensel',author=None,kind='journalism',published_at='2017-11-26',date_precision='day',social_handle=None,public_url=url,basis='Evrensel kongre ve seçim haberi, 18 Kasım 2019 tarihli Wayback kopyasından okundu; haberin güncelleme zamanı ayrıca belirsiz.')},{'kind':'passage','values':dict(id=ident+'-result-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Genel başkan ve genel yönetim kurulu seçim sonucu',pdf_page_index=None,printed_page=None)}]
out=Path(__file__).parent/'congress-2017-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=entries,status='source_read_package_pending',note='Selma Gürkan genel başkan seçimi haberden; aynı dönem tüzüğü henüz bulunmadı, oy sayısı ve yöntemi haberde belirtilmedi.'),f,ensure_ascii=False,indent=2);f.write('\n')
print('CONGRESS_2017_SOURCE_OK',sha,view['view_id'])
