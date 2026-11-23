import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('party', '/tmp/gsd0410-earthquake2025/party.html', 'https://www.emep.org/emek-partisi-hatayda-2-yil-deprem-raporunu-acikladi', '2025-02-05', 'party_publication', 'Emek Partisi', 'Emep', 'İkinci yıl deprem raporu parti yayını', 'Emek Partisi (EMEP) 2. yıl deprem raporunu Hatay’da açıkladı.'),
    ('pirha', '/tmp/gsd0410-earthquake2025/pirha.html', 'https://pirha.org/emep-deprem-raporunu-acikladi-halk-butun-kisi-sogukta-gecirdi-sorunlar-suruyor-462445.html/05/02/2025/', '2025-02-05', 'journalism', 'PİRHA', 'Eren Güven', 'Hatay deprem raporu açıklaması haberi', 'EMEP Hatay İl binasında gerçekleşen açıklamada'),
]
entries = []
for role, path, url, date, kind, publisher, author, title, exact in sources:
    raw = Path(path).read_bytes(); sha = hashlib.sha256(raw).hexdigest()
    obj = root/'objects'/sha; obj.mkdir(parents=True, exist_ok=True)
    for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        dest = obj/name
        if dest.exists(): assert dest.read_bytes() == content
        else: dest.write_bytes(content)
    ident = '0410-emep-earthquake2025-'+role; version = ident+'-v1'
    view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
    view['version_id'] = version; validate_view(root, view)
    assert exact in html_source_text(raw)
    entries.extend([
        dict(kind='document', values=dict(id=ident, party_id='emep', title=title, source_kind='party' if kind=='party_publication' else kind)),
        dict(kind='document_version', values=dict(id=version, document_id=ident, original_url=url, final_url=url, document_date=date, date_precision='day', date_unknown_reason=None, version_label=title, accessed_at=now, verified_at=now, mime='text/html', sha256=sha, original_path='objects/'+sha+'/original.html.bin', readable_path='objects/'+sha+'/readable.html')),
        dict(kind='archive_view', values=view),
        dict(kind='source_attribution', values=dict(version_id=version, kind=kind, publisher=publisher, author=author, social_handle=None, published_at=date, date_precision='day', public_url=url, basis='Tarihli özgün yayın; parti açıklaması ve bağımsız haber ayrı belgelerdir.')),
        dict(kind='passage', values=dict(id=ident+'-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section=title, pdf_page_index=None, printed_page=None)),
    ])
    print(role, sha, view['view_id'])
out = Path(__file__).parent/'earthquake2025-source-draft.json'
with out.open('x') as f:
    json.dump(dict(entries=entries, status='source_read_package_pending', note='EMEP ve PİRHA 5 Şubat 2025 yayınlarını ayrı okudum. PİRHA il binasındaki açıklamayı haberleştirir; rapordaki tüm savlar bağımsız doğrulanmış olgu sayılmaz. 6 Şubat Evrensel Bayhan aktarımında sunum önceki gün olarak tarihlenir.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
