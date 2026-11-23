import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('party', '/tmp/gsd0410-kirsehir2026/party.html', 'https://www.emep.org/kirsehir-il-baskanimiz-pelin-atarbay-ortak-ve-birlesik-mucadeleyi-birlikte-buyutecegiz', '2026-09-09', 'party_publication', 'Emek Partisi', 'Emep', 'Kırşehir 4. il kongresi parti yayını', 'Kongrede il başkanı Pelin Atarbay oldu.'),
    ('news', '/tmp/gsd0410-kirsehir2026/news.html', 'https://www.kirsehircigdem.com/emep-kirsehirde-yeni-donem-il-baskani-pelin-atarbay-oldu', '2026-09-07', 'journalism', 'Kırşehir Çiğdem', 'Nurten Ceylan ve Damla Yeşilli', 'Kırşehir 4. il kongresi haberi', 'Kongrede yapılan seçimin ardından EMEP Kırşehir İl Başkanı seçilen Pelin Atarbay, kadınların toplumsal yaşamdan siyasete kadar her alanda daha görünür ve etkin olması gerektiğini vurguladı.'),
]
entries = []
for role, path, url, date, kind, publisher, author, title, exact in sources:
    raw = Path(path).read_bytes(); sha = hashlib.sha256(raw).hexdigest()
    obj = root/'objects'/sha; obj.mkdir(parents=True, exist_ok=True)
    for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        dest = obj/name
        if dest.exists(): assert dest.read_bytes() == content
        else: dest.write_bytes(content)
    ident = '0410-emep-kirsehir2026-'+role; version = ident+'-v1'
    view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
    view['version_id'] = version; validate_view(root, view)
    assert exact in html_source_text(raw)
    entries.extend([
        dict(kind='document', values=dict(id=ident, party_id='emep', title=title, source_kind='party' if kind=='party_publication' else kind)),
        dict(kind='document_version', values=dict(id=version, document_id=ident, original_url=url, final_url=url, document_date=date, date_precision='day', date_unknown_reason=None, version_label=title, accessed_at=now, verified_at=now, mime='text/html', sha256=sha, original_path='objects/'+sha+'/original.html.bin', readable_path='objects/'+sha+'/readable.html')),
        dict(kind='archive_view', values=view),
        dict(kind='source_attribution', values=dict(version_id=version, kind=kind, publisher=publisher, author=author, social_handle=None, published_at=date, date_precision='day', public_url=url, basis='Farklı tarihli parti yayını ve yerel haber; haberde Nurten Ceylan ve Damla Yeşilli muhabir olarak yer alıyor. Oy sayısı ve seçim tutanağı görülmedi.')),
        dict(kind='passage', values=dict(id=ident+'-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section=title, pdf_page_index=None, printed_page=None)),
    ])
    print(role, sha, view['view_id'])
out = Path(__file__).parent/'kirsehir2026-source-draft.json'
with out.open('x') as f:
    json.dump(dict(entries=entries, status='source_read_package_pending', note='Kırşehir 4. il kongresinde Pelin Atarbay seçimi iki yayında bildirilir. Parti yayını ve yerel haber 6 Eylül 2026 gününü bildirir; oy sayısı ve seçim tutanağı görülmedi.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
