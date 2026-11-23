import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('party', '/tmp/gsd0410-gaziantep2026/party.html', 'https://www.emep.org/baspinar-iscilerinden-dogasini-savunan-koylulere-emep-gaziantep-kongresinde-emekciler-konustu', '2026-11-10', 'party_publication', 'Emek Partisi', 'Emep', 'Gaziantep 11. il kongresi parti yayını', 'Mecit Bozkurt il başkanlığına seçildi.'),
    ('news', '/tmp/gsd0410-gaziantep2026/news.html', 'https://www.yenicizgihaber.com/gundem/emep-gaziantepte-mecit-bozkurt-donemi-382615', '2026-11-08', 'journalism', 'Yeni Çizgi Haber', 'Anıl Şahin', 'Gaziantep 11. il kongresi haberi', 'Mecit Bozkurt, EMEP Gaziantep İl Başkanlığına seçildi.'),
]
entries = []
for role, path, url, date, kind, publisher, author, title, exact in sources:
    raw = Path(path).read_bytes(); sha = hashlib.sha256(raw).hexdigest()
    obj = root/'objects'/sha; obj.mkdir(parents=True, exist_ok=True)
    for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        dest = obj/name
        if dest.exists(): assert dest.read_bytes() == content
        else: dest.write_bytes(content)
    ident = '0410-emep-gaziantep2026-'+role; version = ident+'-v1'
    view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
    view['version_id'] = version; validate_view(root, view)
    assert exact in html_source_text(raw)
    entries.extend([
        dict(kind='document', values=dict(id=ident, party_id='emep', title=title, source_kind='party' if kind=='party_publication' else kind)),
        dict(kind='document_version', values=dict(id=version, document_id=ident, original_url=url, final_url=url, document_date=date, date_precision='day', date_unknown_reason=None, version_label=title, accessed_at=now, verified_at=now, mime='text/html', sha256=sha, original_path='objects/'+sha+'/original.html.bin', readable_path='objects/'+sha+'/readable.html')),
        dict(kind='archive_view', values=view),
        dict(kind='source_attribution', values=dict(version_id=version, kind=kind, publisher=publisher, author=author, social_handle=None, published_at=date, date_precision='day', public_url=url, basis='Farklı tarihli parti ve haber yayını; haber sayfası Anıl Şahin ve Haber Merkezi atıflarını birlikte gösterir; metinsel benzerlik bağımsız tanıklığı tek başına kanıtlamaz.')),
        dict(kind='passage', values=dict(id=ident+'-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section=title, pdf_page_index=None, printed_page=None)),
    ])
    print(role, sha, view['view_id'])
out = Path(__file__).parent/'gaziantep2026-source-draft.json'
with out.open('x') as f:
    json.dump(dict(entries=entries, status='source_read_package_pending', note='Gaziantep 11. il kongresinde Mecit Bozkurt seçimi iki yayında bildirilir. 8 Kasım yayını olayın en geç tarihidir; kesin olay günü ve oy sayısı bu belgelerle sabit değil.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
