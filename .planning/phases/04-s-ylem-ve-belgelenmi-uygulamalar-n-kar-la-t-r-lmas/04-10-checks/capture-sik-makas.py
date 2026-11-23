import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path(__file__).parent
root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('party', 'sik-makas-party-original.html', 'https://www.emep.org/sik-makas-iscileri-mecliste-anayasal-haklarimiz-icin-neden-direnmek-zorundayiz', 'party', 'party_publication', 'Emek Partisi', 'Emek Partisi', '2026-03-06', 'TİP Genel Başkanı Erkan Baş, DEM Parti Milletvekili Özgül Saki’nin de katıldığı basın toplantısında'),
    ('anka', 'sik-makas-anka-original.html', 'https://ankahaber.net/haber/detay/sik_makas_iscileri_tbmmde_kidem_ve_ihbar_tazminatlarimiz_yasal_guvence_altinda_olmasina_ragmen_neden_150_gundur_savasmak_zorunda_birakiliyoruz_296548', 'journalism', 'journalism', 'ANKA Haber', 'ANKA Haber', '2026-03-04', 'Basın toplantısına TİP Genel Başkanı Erkan Baş ve DEM Milletvekili'),
]
entries = []
for key, filename, url, source_kind, attribution, publisher, author, day, exact in sources:
    raw = (checks / filename).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    assert exact in html_source_text(raw), (key, exact)
    obj = root / 'objects' / sha
    obj.mkdir(parents=True, exist_ok=True)
    for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        dest = obj / name
        if dest.exists():
            assert dest.read_bytes() == content
        else:
            dest.write_bytes(content)
    doc = '0410-emep-sik-makas-' + key
    version = doc + '-v1'
    view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
    view['version_id'] = version
    validate_view(root, view)
    entries.extend([
        dict(kind='document', values=dict(id=doc, party_id='emep', title='Şık Makas işçileriyle TBMM basın toplantısı', source_kind=source_kind)),
        dict(kind='document_version', values=dict(id=version, document_id=doc, original_url=url, final_url=url, document_date=day, date_precision='day', date_unknown_reason=None, version_label=day+' tarihli yayın', accessed_at=now, verified_at=now, mime='text/html', sha256=sha, original_path='objects/'+sha+'/original.html.bin', readable_path='objects/'+sha+'/readable.html')),
        dict(kind='archive_view', values=view),
        dict(kind='source_attribution', values=dict(version_id=version, kind=attribution, publisher=publisher, author=author, social_handle=None, published_at=day, date_precision='day', public_url=url, basis='Yayın tarihi toplantı tarihi olarak kesinleştirilmedi. ANKA sayfası 3 Haziran güncellemesi de gösterir; haberlerin ortak kaynak kullanımı olasıdır.')),
        dict(kind='passage', values=dict(id=doc+'-meeting-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section='TBMM basın toplantısı', pdf_page_index=None, printed_page=None)),
    ])
    print(key, sha, view['view_id'])
out = checks / 'sik-makas-source-draft.json'
with out.open('x') as f:
    json.dump(dict(entries=entries, status='source_read_package_pending', note='Yayın tarihleri ayrıdır; toplantı tarihi ve TBMM asıl kaydı açık. İşçilerin beyanları kendilerine atıflı; süreç sonucu çıkarılmaz.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
