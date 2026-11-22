import datetime, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
root = Path('data/practices/sources/emep')
raw = Path('/tmp/gsd0410-kocaeli-discipline-original.html').read_bytes()
sha = hashlib.sha256(raw).hexdigest()
url = 'https://www.ozgunkocaeli.com.tr/ilhami-sahbaz-yeniden-il-baskani-secildi'
obj = root/'objects'/sha
obj.mkdir(parents=True,exist_ok=True)
for name, content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    dest = obj/name
    if dest.exists(): assert dest.read_bytes()==content
    else: dest.write_bytes(content)
ident = '0410-emep-kocaeli-2026-congress-ozgun'
version = ident+'-v1'
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
view = build_view(raw,url,root,fetch_assets=False,http_charset='utf-8')
view['version_id'] = version
validate_view(root,view)
exact = 'İl disiplin kurulu üyeleri ise Osman Nuri Şenol, Ahmet Orhan Tüzmen ve Nizam Umur olarak belirlendi.'
assert exact in html_source_text(raw)
rows = [
 dict(kind='document',values=dict(id=ident,party_id='emep',title='İlhami Şahbaz yeniden il başkanı seçildi!',source_kind='journalism')),
 dict(kind='document_version',values=dict(id=version,document_id=ident,original_url=url,final_url=url,document_date='2026-11-01',date_precision='day',date_unknown_reason=None,version_label='1 Kasım 2026 kongre haberi',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')),
 dict(kind='archive_view',values=view),
 dict(kind='source_attribution',values=dict(version_id=version,kind='journalism',publisher='Özgün Kocaeli',author='Bahar Özdemir',social_handle=None,published_at='2026-11-01',date_precision='day',public_url=url,basis='Haberde gazeteci adı, 1 Kasım yayın ve aynı gün güncelleme zamanı yer alıyor.')),
 dict(kind='passage',values=dict(id=ident+'-discipline-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='İl disiplin kurulu üyeleri',pdf_page_index=None,printed_page=None))
]
out=Path(__file__).parent/'kocaeli-discipline-source-draft.json'
with out.open('x') as f:
    json.dump(dict(entries=rows,status='source_read_package_pending',note='1 Kasım 2026 Kocaeli kongresinde üç isim bildiriliyor; kurul seçiminde gizli oy ve oy sayısı haberden çıkarılamaz. İl başkanlığı adayıyla aynı kongre ve tek olay kimliği kullanılmalı; 2023 tüzüğünün 2026da kesintisiz yürürlükte olduğu varsayılmaz.'),f,ensure_ascii=False,indent=2)
    f.write('\n')
print(sha,view['view_id'])
