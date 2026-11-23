import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('party', '/tmp/gsd0410-monetary2021/party.html', 'https://www.emep.org/ucretler-eriyor-halkin-ekmegi-kuculuyor-sessiz-kalmayalim-haklarimiz-icin-birlikte-mucadele-edelim', '2021-11-24', 'party_publication', 'Emek Partisi', 'Sedat Başkavak', 'Ücretler ve döviz üzerine açıklama', 'Döviz ve faiz kıskacında'),
]
entries = []
for role, path, url, date, kind, publisher, author, title, exact in sources:
    raw = Path(path).read_bytes(); sha = hashlib.sha256(raw).hexdigest()
    obj = root/'objects'/sha; obj.mkdir(parents=True, exist_ok=True)
    for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        dest = obj/name
        if dest.exists(): assert dest.read_bytes() == content
        else: dest.write_bytes(content)
    ident = '0410-emep-monetary2021-'+role; version = ident+'-v1'
    view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
    view['version_id'] = version; validate_view(root, view)
    assert exact in html_source_text(raw)
    entries.extend([
        dict(kind='document', values=dict(id=ident, party_id='emep', title=title, source_kind='party' if kind=='party_publication' else kind)),
        dict(kind='document_version', values=dict(id=version, document_id=ident, original_url=url, final_url=url, document_date=date, date_precision='day', date_unknown_reason=None, version_label=title, accessed_at=now, verified_at=now, mime='text/html', sha256=sha, original_path='objects/'+sha+'/original.html.bin', readable_path='objects/'+sha+'/readable.html')),
        dict(kind='archive_view', values=view),
        dict(kind='source_attribution', values=dict(version_id=version, kind=kind, publisher=publisher, author=author, social_handle=None, published_at=date, date_precision='day', public_url=url, basis='Tarihli parti yayını, metin sonundaki Sedat Başkavak ve genel başkan yardımcısı imzasıyla atfedilir.')),
        dict(kind='passage', values=dict(id=ident+'-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section=title, pdf_page_index=None, printed_page=None)),
    ])
    print(role, sha, view['view_id'])
out = Path(__file__).parent/'monetary2021-source-draft.json'
with out.open('x') as f:
    json.dump(dict(entries=entries, status='source_read_package_pending', note='24 Kasım 2021 parti yayını döviz/faiz, alım gücü ve küçük esnaf durumunu ele alır. Açıklama somut faiz oranı önerisi veya doğrulanmış ekonomik veri olarak sunulmaz.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
