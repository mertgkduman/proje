import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('party', 'https://www.emep.org/emep-nato-zirvesi-icin-alinan-eylem-yasagi-kararini-mahkemeye-tasidi', 'party', 'party_publication', 'Emek Partisi', 'Emek Partisi', 'EMEP adına Av. Sevil Aracı ve Av. Tugay Bek tarafından Ankara Nöbetçi İdare Mahkemesi Başkanlığına sunulan dilekçede'),
    ('anka', 'https://www.haberler.com/guncel/emep-nato-zirvesi-oncesi-ankara-daki-yasaklama-kararina-dava-acti-19933419-haberi/', 'journalism', 'journalism', 'Haberler.com', 'ANKA', 'Sevil Aracı ve Tugay Bek tarafından Ankara Nöbetçi İdare Mahkemesi'),
]
entries = []
for key, url, source_kind, attribution, publisher, author, exact in sources:
    raw = Path('/tmp/gsd0410-nato-case-' + key + '.html').read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    assert exact in html_source_text(raw)
    obj = root / 'objects' / sha
    obj.mkdir(parents=True, exist_ok=True)
    for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        dest = obj / name
        if dest.exists():
            assert dest.read_bytes() == content
        else:
            dest.write_bytes(content)
    doc = '0410-emep-nato-case-' + key
    version = doc + '-v1'
    view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
    view['version_id'] = version
    validate_view(root, view)
    entries.extend([
        dict(kind='document', values=dict(id=doc, party_id='emep', title='NATO zirvesi öncesi Ankara yasak kararına EMEP davası', source_kind=source_kind)),
        dict(kind='document_version', values=dict(id=version, document_id=doc, original_url=url, final_url=url, document_date='2026-06-10', date_precision='day', date_unknown_reason=None, version_label='10 Haziran 2026 yayını', accessed_at=now, verified_at=now, mime='text/html', sha256=sha, original_path='objects/'+sha+'/original.html.bin', readable_path='objects/'+sha+'/readable.html')),
        dict(kind='archive_view', values=view),
        dict(kind='source_attribution', values=dict(version_id=version, kind=attribution, publisher=publisher, author=author, social_handle=None, published_at='2026-06-10', date_precision='day', public_url=url, basis='Dava açıldığına ilişkin yayın; mahkeme dosyası ve sonucu ayrıca açık. İki metin ortak dilekçe aktarımına dayanabilir.')),
        dict(kind='passage', values=dict(id=doc+'-filing-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section='Davanın açılması', pdf_page_index=None, printed_page=None)),
    ])
    print(key, sha, view['view_id'])
out = Path(__file__).parent / 'nato-case-source-draft.json'
with out.open('x') as f:
    json.dump(dict(entries=entries, status='source_read_package_pending', note='İki yayın dava açılması ve yürütmenin durdurulması talebini aktarır; talep mahkeme kararı değildir. KESK ve TKP davaları ile daha sonraki valilik kararı ayrıdır.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
