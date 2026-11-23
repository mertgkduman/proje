import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('statement', '/tmp/gsd0410-media/party.html', 'https://www.emep.org/iskender-bayhan-saray-oligarsisinin-baskisindan-genel-direnis-hattiyla-kurtulabiliriz', '2026-10-16', 'party_publication', 'Emek Partisi', 'Haber merkezi', 'Bayhan basın özgürlüğü açıklaması', 'Halkın haber alma hakkı, basın özgürlüğü, Halk TV hedefe konuyor.'),
    ('event', '/tmp/gsd0410-media/anka.html', 'https://ankahaber.net/haber/emep-li-bayhan-371-televizyon-kanalinin-hepsine-el-koysaniz-da-gercekleri-karartamayacaksiniz-be4252fc', '2026-10-15', 'journalism', 'ANKA Haber Ajansı', 'ANKA Haber', 'Bayhan Halk TV açıklaması', 'Halk TV’ye kayyum atanmasına ilişkin'),
]
entries = []
for role, path, url, date, kind, publisher, author, title, exact in sources:
    raw = Path(path).read_bytes(); sha = hashlib.sha256(raw).hexdigest()
    obj = root/'objects'/sha; obj.mkdir(parents=True, exist_ok=True)
    for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        dest = obj/name
        if dest.exists(): assert dest.read_bytes() == content
        else: dest.write_bytes(content)
    ident = '0410-emep-media-'+role; version = ident+'-v1'
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
out = Path(__file__).parent/'media-sources-draft.json'
with out.open('x') as f:
    json.dump(dict(entries=entries, status='source_read_package_pending', note='ANKA haberi 15 Ekim, parti yayını 16 Ekim tarihlidir; aynı konuşmaya ilişkin tarih ve yayın tarihi ayrılır. Görüşler Bayhan’a atfedilir, iddialar doğrulanmış olgu yapılmaz.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
