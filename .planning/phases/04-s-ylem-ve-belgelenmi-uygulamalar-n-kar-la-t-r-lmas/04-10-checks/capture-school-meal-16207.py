import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes, pdf_page_text
from arsiv_gorunum import build_view, validate_view

D = Path(__file__).parent
root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('detail', 'html', 'school-meal-16207-detail.html', 'https://www.tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/31be0532-5567-4db3-bdce-0191f9fa0f2c', None, None),
    ('question', 'pdf', 'school-meal-16207-question.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y2/T7/WebOnergeMetni/ee012f2b-7611-45cc-a53a-d23e4b56c245.pdf', '2024-09-13', 'Sevda Karaca Demir'),
    ('answer', 'pdf', 'school-meal-16207-answer.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y2/T7/WebOnergeMetni/2fc7e4bd-959f-43ef-9a79-37fd409ae5cb.pdf', None, 'Millî Eğitim Bakanlığı'),
    ('commission', 'pdf', 'school-meal-20231114-tbmm-commission.pdf', 'https://www.tbmm.gov.tr/Tutanaklar/TutanakGoster/3190', '2023-11-14', 'TBMM Plan ve Bütçe Komisyonu'),
]
entries = []
for role, typ, filename, url, date, author in sources:
    raw = (D / filename).read_bytes()
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
    doc = '0410-emep-school-meal-16207-' + role
    version = doc + '-v1'
    entries.append(dict(kind='document', values=dict(id=doc, party_id='emep', title='TBMM okul yemeği ' + role, source_kind='official')))
    entries.append(dict(kind='document_version', values=dict(id=version, document_id=doc, original_url=url, final_url=url, document_date=date, date_precision='day' if date else 'unknown', date_unknown_reason=None if date else 'Belgenin kendi düzenleme günü doğrulanmadı.', version_label='TBMM özgün kaydı', accessed_at=now, verified_at=now, mime='text/html' if typ == 'html' else 'application/pdf', sha256=digest, original_path='objects/' + digest + '/' + original, readable_path='objects/' + digest + '/readable.html')))
    if typ == 'html':
        view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
        view['version_id'] = version
        validate_view(root, view)
        entries.append(dict(kind='archive_view', values=view))
        for key, exact in [('number', '7 / 16207'), ('date', '13.09.2024'), ('reply', '25.10.2024')]:
            assert exact in html_source_text(raw)
            entries.append(dict(kind='passage', values=dict(id=doc+'-'+key+'-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section='Soru ve cevap bildirimi', pdf_page_index=None, printed_page=None)))
    if role == 'question':
        exact = '14 Kasım 2024 tarihinde'
        assert exact in pdf_page_text(obj/original, 1)
        entries.append(dict(kind='passage', values=dict(id=doc+'-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section='İmzalı soru, metindeki tarih', pdf_page_index=1, printed_page=None)))
    if role == 'commission':
        exact = 'Bu 10 bin imza ücretsiz yemek için toplandı.'
        assert exact in pdf_page_text(obj/original, 103)
        entries.append(dict(kind='passage', values=dict(id=doc+'-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section='18. toplantı, 4. oturum', pdf_page_index=103, printed_page='104')))
    entries.append(dict(kind='source_attribution', values=dict(version_id=version, kind='official', publisher='Türkiye Büyük Millet Meclisi', author=author, social_handle=None, published_at=None, date_precision='unknown', public_url=url, basis='TBMM özgün kaydı. Cevabın iki taranmış sayfası görsel okundu; soru tarihi ile teslim tarihi ayrı.')))
    print(role, digest)
with (D/'school-meal-16207-source-draft.json').open('x') as f:
    json.dump(dict(status='source_read_package_pending', entries=entries, note='2023 komisyonundaki 10 bin imza, 13 Eylül 2024 soru ve 25 Ekim bildirimli yanıt ayrı. Sorudaki 14 Kasım 2024 tarihi gelecekte kalır; asıl komisyon tutanağı 14 Kasım 2023tür. Yanıtta belirli öğrenci gruplarına yemek anlatılır, dilekçelerin akıbeti açıklanmaz.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
