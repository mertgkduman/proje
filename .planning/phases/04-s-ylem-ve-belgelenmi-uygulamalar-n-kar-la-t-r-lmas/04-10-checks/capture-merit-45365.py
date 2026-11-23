import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
entries = []
sources = [
    ('register', 'html', '/tmp/gsd0410-merit45365/detail.html', 'https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/6e5279e0-3efd-4c0d-9cd4-019e96bf0f92'),
    ('question', 'pdf', '/tmp/gsd0410-merit45365/question.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T7/WebOnergeMetni/e9f9e613-c7b0-4046-821d-40bc1e43d92d.pdf'),
    ('answer', 'pdf', '/tmp/gsd0410-merit45365/answer.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T7/WebOnergeMetni/019b095e-a10b-4dbb-ac70-7ded7a7c71ea.pdf'),
]
def add(record_kind, **values):
    entries.append(dict(kind=record_kind, values=values))

for role, typ, path, url in sources:
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    obj = root / 'objects' / sha
    obj.mkdir(parents=True, exist_ok=True)
    original = 'original.html.bin' if typ == 'html' else 'original.pdf'
    ident = '0410-emep-question-45365-' + role
    for name, content in [(original, raw), ('readable.html', readable_bytes(raw, typ, legacy=False))]:
        dest = obj / name
        if dest.exists():
            assert dest.read_bytes() == content
        else:
            dest.write_bytes(content)
    add('document', id=ident, party_id='emep', title='TBMM 7/45365 ' + {'register':'kayıt', 'question':'yazılı soru', 'answer':'bakanlık yanıtı'}[role], source_kind='official')
    date = {'question': '2026-06-04', 'answer': '2026-07-16'}.get(role)
    add('document_version', id=ident+'-v1', document_id=ident, original_url=url, final_url=url, document_date=date, version_label={'register':'TBMM kayıt ekranı', 'question':'TBMM yazılı soru', 'answer':'Bakanlık, YÖK ve üniversite yanıtı, altı sayfa görsel okundu'}[role], accessed_at=now, verified_at=now, mime='text/html' if typ=='html' else 'application/pdf', sha256=sha, original_path='objects/'+sha+'/'+original, readable_path='objects/'+sha+'/readable.html', date_precision='day' if date else 'unknown', date_unknown_reason=None if date else 'Belgenin yayımlanma tarihi doğrulanmadı.')
    if typ == 'html':
        view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
        view['version_id'] = ident+'-v1'
        validate_view(root, view)
        add('archive_view', **view)
        exact = '7 / 45365'
        assert exact in html_source_text(raw)
        add('passage', id=ident+'-number-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='Soru esas numarası', pdf_page_index=None, printed_page=None)
    if role == 'question':
        exact = 'şartlarından biri, kamu görevlerine yapılacak atamalarda liyakat ve kariyer ilkelerinin'
        assert exact in pdf_page_text(Path(path), 0)
        add('passage', id=ident+'-sale-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='Kamu görevinde liyakat ilkesine ilişkin soru', pdf_page_index=0, printed_page=None)
    add('source_attribution', version_id=ident+'-v1', kind='official', publisher='Türkiye Büyük Millet Meclisi', author='Millî Eğitim Bakanlığı' if role == 'answer' else None, social_handle=None, published_at=None, date_precision='unknown', public_url=url, basis=('16.07.2026 tarihli MEB üst yazısı ve aynı gün TBMM bildirimi; YÖK ve İstanbul Üniversitesi yanıtları ektedir.' if role == 'answer' else 'TBMM resmî kayıt, soru ve bakanlık yanıtı ayrı belgelerdir; yayın tarihi çıkarılmadı.'))
    print(role, sha)

out = Path(__file__).parent / "merit-45365-source-draft.json"
with out.open("x") as f:
    json.dump(dict(status="source_read_partial", entries=entries, note="4 Haziran 2026 soru; 16 Temmuz MEB bildirimi, 22 Haziran İstanbul Üniversitesi yanıtı. İddialar ve kurum cevabı ayrı atfedilir."), f, ensure_ascii=False, indent=2)
    f.write("\n")
