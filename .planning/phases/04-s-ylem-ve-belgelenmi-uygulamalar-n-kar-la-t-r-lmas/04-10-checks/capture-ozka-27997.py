import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

D = Path(__file__).parent
root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('detail', 'html', 'https://www.tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/b12ae3c7-59fa-4a40-be3e-0196901bb502', None, None),
    ('question', 'pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/89df1cc2-afd2-4390-af13-1f8746869a8a.pdf', '2025-04-30', 'İskender Bayhan'),
    ('reply', 'pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/351daf4f-9a5c-4b9c-9fbf-3d86b6621e00.pdf', '2026-09-17', 'Çalışma ve Sosyal Güvenlik Bakanlığı'),
]
entries = []
for role, typ, url, date, author in sources:
    raw = (D / 'ozka-27997' / (role + ('.html' if typ == 'html' else '.pdf'))).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    obj = root / 'objects' / digest
    obj.mkdir(parents=True, exist_ok=True)
    original = 'original.html.bin' if typ == 'html' else 'original.pdf'
    for name, content in [(original, raw), ('readable.html', readable_bytes(raw, typ, legacy=False))]:
        path = obj / name
        if path.exists():
            assert path.read_bytes() == content
        else:
            path.write_bytes(content)
    doc = '0410-emep-ozka-27997-' + role
    version = doc + '-v1'
    entries.append(dict(kind='document', values=dict(id=doc, party_id='emep', title='TBMM 7/27997 ' + {'detail': 'kayıt', 'question': 'soru', 'reply': 'bakanlık yanıtı'}[role], source_kind='official')))
    entries.append(dict(kind='document_version', values=dict(id=version, document_id=doc, original_url=url, final_url=url, document_date=date, date_precision='day' if date else 'unknown', date_unknown_reason=None if date else 'Yayın günü doğrulanmadı.', version_label='TBMM özgün kaydı; PDF sayfaları okundu', accessed_at=now, verified_at=now, mime='text/html' if typ == 'html' else 'application/pdf', sha256=digest, original_path='objects/' + digest + '/' + original, readable_path='objects/' + digest + '/readable.html')))
    if typ == 'html':
        view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
        view['version_id'] = version
        validate_view(root, view)
        entries.append(dict(kind='archive_view', values=view))
        for key, exact in [('number', '7 / 27997'), ('date', '30.04.2025'), ('reply', '18.09.2026')]:
            assert exact in html_source_text(raw)
            entries.append(dict(kind='passage', values=dict(id=doc + '-' + key + '-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section='Soru ve yanıt bildirim kaydı', pdf_page_index=None, printed_page=None)))
    entries.append(dict(kind='source_attribution', values=dict(version_id=version, kind='official', publisher='Türkiye Büyük Millet Meclisi', author=author, social_handle=None, published_at=None, date_precision='unknown', public_url=url, basis='TBMM özgün kaydı; belge tarihi ve yayın tarihi ayrıdır. Taranmış bakanlık yanıtı sayfa sayfa görsel okundu.')))
    print(role, digest)
with (D / 'ozka-27997-source-draft.json').open('x') as f:
    json.dump(dict(status='source_read_package_pending', entries=entries, note='Soru 30 Nisan 2025; yanıt 17 Eylül 2026 ve bildirim 18 Eylül 2026. Yanıt genel hükümleri anlatır; somut işyeri denetim sonucu gösterilmez.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
