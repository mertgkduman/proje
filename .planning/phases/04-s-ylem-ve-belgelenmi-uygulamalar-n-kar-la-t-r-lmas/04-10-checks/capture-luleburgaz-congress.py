import datetime, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/emep')
raw = Path('/tmp/gsd0410-evrensel-416240.html').read_bytes()
sha = hashlib.sha256(raw).hexdigest()
url = 'https://www.evrensel.net/haber/416240/emep-kongrelerini-surduruyor'
archive = 'https://web.archive.org/web/20201014133834id_/https://www.evrensel.net/haber/416240/emep-kongrelerini-surduruyor'
obj = root / 'objects' / sha
obj.mkdir(parents=True, exist_ok=True)
for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
    dest = obj / name
    if dest.exists():
        assert dest.read_bytes() == content
    else:
        dest.write_bytes(content)
ident = '0410-emep-luleburgaz-2020-evrensel'
version = ident + '-v1'
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
view['version_id'] = version
validate_view(root, view)
text = html_source_text(raw)
start = text.index('Bug&uuml;n Emek Partisi L&uuml;leburgaz')
end = text.index(' Kongre sonunda', start)
exact = text[start:end]
rows = [
    dict(kind='document', values=dict(id=ident, party_id='emep', title='EMEP kongrelerini sürdürüyor', source_kind='journalism')),
    dict(kind='document_version', values=dict(id=version, document_id=ident, original_url=url, final_url=archive, document_date='2020-10-11', date_precision='day', date_unknown_reason=None, version_label='14 Ekim 2020 arşiv kopyası', accessed_at=now, verified_at=now, mime='text/html', sha256=sha, original_path='objects/'+sha+'/original.html.bin', readable_path='objects/'+sha+'/readable.html')),
    dict(kind='archive_view', values=view),
    dict(kind='source_attribution', values=dict(version_id=version, kind='journalism', publisher='Evrensel', author=None, social_handle=None, published_at='2020-10-11', date_precision='day', public_url=url, basis='Lüleburgaz/EVRENSEL imzalı haber; 14 Ekim 2020 tarihli arşiv kopyası okundu.')),
    dict(kind='passage', values=dict(id=ident+'-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section='11 Ekim ilçe kongresi', pdf_page_index=None, printed_page=None)),
]
out = Path(__file__).parent / 'luleburgaz-congress-source-draft.json'
with out.open('x') as f:
    json.dump(dict(entries=rows, status='source_read_package_pending', note='11 Ekim tarihli haberde bugün yapılan kongre ve Cengiz Atlı başkanlığı bildiriliyor; seçim yöntemi ve oy sayısı bildirilmiyor. Tek haber bağımsız gözlem sayısını artırmaz. Kapsam açık.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
print(sha, view['view_id'])
