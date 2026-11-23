import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root=Path('data/practices/sources/emep')
url='https://www.emep.org/emek-partisi-akcadag-ilce-orgutu-11-olagan-genel-kurulu-yapildi-koylu-isci-uretici-cozum-icin-emepte-bulusmali'
raw=Path('/tmp/gsd0410-akcadag2026/party.html').read_bytes(); sha=hashlib.sha256(raw).hexdigest()
obj=root/'objects'/sha; obj.mkdir(parents=True, exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 dest=obj/name
 if dest.exists(): assert dest.read_bytes()==content
 else: dest.write_bytes(content)
version='0410-emep-akcadag2026-party-v1'; doc='0410-emep-akcadag2026-party'; now=datetime.now(timezone.utc).isoformat(timespec='seconds')
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view)
exacts=[('financial','Konuşmaların ardından faaliyet raporu ve mali rapor okunarak ibra edildi.'),('leader','kongrede söz alan İl Başkanı Şerif Demirel'),('election','Yapılan seçim sonucunda İlçe Başkanlığına Karaca Karakuzu yeniden seçilirken')]
entries=[dict(kind='document',values=dict(id=doc,party_id='emep',title='Akçadağ 11. ilçe genel kurulu parti yayını',source_kind='party')),dict(kind='document_version',values=dict(id=version,document_id=doc,original_url=url,final_url=url,document_date='2026-10-12',date_precision='day',date_unknown_reason=None,version_label='12 Ekim 2026 parti yayını',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')),dict(kind='archive_view',values=view),dict(kind='source_attribution',values=dict(version_id=version,kind='party_publication',publisher='Emek Partisi',author='Emek Partisi',social_handle=None,published_at='2026-10-12',date_precision='day',public_url=url,basis='Parti yayını; mali raporun içeriği ve kamusal erişimi gösterilmemiştir. Kongrenin günü yayın tarihi değildir.'))]
for key,exact in exacts:
 assert exact in html_source_text(raw),key
 entries.append(dict(kind='passage',values=dict(id=doc+'-'+key+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Akçadağ genel kurulu',pdf_page_index=None,printed_page=None)))
out=Path(__file__).parent/'akcadag2026-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=entries,status='source_read_package_pending',note='İlçe genel kurulunda mali raporun okunduğu ve ibra edildiği parti kaynağına göre; hesap metni ve kamuya açıklanması gösterilmiyor. Şerif Demirel 2026 Malatya il kongresi haberinden önce il başkanı olarak anılıyor.'),f,ensure_ascii=False,indent=2);f.write('\n')
print(sha,view['view_id'])
