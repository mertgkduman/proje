import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('statement', '/tmp/gsd0410-anadil/statement.html', 'https://www.emep.org/tek-adam-yonetiminin-savas-ve-somuru-politikalarina-karsi-butun-demokrasi-guclerini-emek-baris-ozgurluk-icin-mucadeleye-cagiriyoruz', '2024-11-15', 'party_publication', 'Emek Partisi', 'Merkez Yürütme Kurulu', 'MYK anadilde eğitim açıklaması', 'Kürt ulusal varlığının ve eşitliğinin kabulü; anadilinde eğitim hakkı, Kürtçenin ikinci resmi dil olması gibi anayasal düzenlemelerin güvenceye alınması bunun için gerekli ilk adımlardır.'),
    ('event', '/tmp/gsd0410-anadil/event.html', 'https://pirha.org/dersimde-21-subat-soylesisi-dil-yasaklari-insan-varolusuna-yoneliktir-video-504954.html/21/02/2026/', '2026-02-21', 'journalism', 'PİRHA', 'PİRHA/Dersim', 'Dersim anadilde eğitim söyleşisi', 'Emek Partisi(EMEP) Dersim İl Örgütü, 21 Şubat Dünya Anadil Günü vesilesiyle, “Anadilde Eğitim ve Sosyal, Kültürel, Yaşamsal Boyutları” konulu söyleşi gerçekleştirdi.'),
]
entries = []
for role, path, url, date, kind, publisher, author, title, exact in sources:
    raw = Path(path).read_bytes(); sha = hashlib.sha256(raw).hexdigest()
    obj = root/'objects'/sha; obj.mkdir(parents=True, exist_ok=True)
    for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        dest = obj/name
        if dest.exists(): assert dest.read_bytes() == content
        else: dest.write_bytes(content)
    ident = '0410-emep-anadil-'+role; version = ident+'-v1'
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
out = Path(__file__).parent/'anadil-sources-draft.json'
with out.open('x') as f:
    json.dump(dict(entries=entries, status='source_read_package_pending', note='15 Kasım 2024 MYK yayını eğitim hakkını ister. PİRHA 21 Şubat 2026 yayını EMEP Dersim İl Örgütünün söyleşisini bildirir. Haber konuşmacılarının görüşleri parti kararı veya eğitim alanında yasal sonuç sayılmaz.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
