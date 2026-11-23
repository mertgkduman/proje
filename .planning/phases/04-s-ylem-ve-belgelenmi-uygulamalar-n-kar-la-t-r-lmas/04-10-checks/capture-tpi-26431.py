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
    ('register', 'html', '/tmp/gsd0410-tpi26431/detail.html', 'https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/6c9f49e7-ed8f-4f7a-ab38-0196196e63e0'),
    ('question', 'pdf', '/tmp/gsd0410-tpi26431/question.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/439a6332-cbb1-46da-81a2-8403e5a72e74.pdf'),
    ('answer', 'pdf', '/tmp/gsd0410-tpi26431/answer.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/4c9294f1-67e1-416c-9917-226854b6d94a.pdf'),
]
def add(record_kind, **values):
    entries.append(dict(kind=record_kind, values=values))

for role, typ, path, url in sources:
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    obj = root / 'objects' / sha
    obj.mkdir(parents=True, exist_ok=True)
    original = 'original.html.bin' if typ == 'html' else 'original.pdf'
    ident = '0410-emep-question-26431-' + role
    for name, content in [(original, raw), ('readable.html', readable_bytes(raw, typ, legacy=False))]:
        dest = obj / name
        if dest.exists():
            assert dest.read_bytes() == content
        else:
            dest.write_bytes(content)
    add('document', id=ident, party_id='emep', title='TBMM 7/26431 ' + {'register':'kayıt', 'question':'yazılı soru', 'answer':'bakanlık yanıtı'}[role], source_kind='official')
    date = {'question': '2025-04-08', 'answer': '2025-09-22'}.get(role)
    add('document_version', id=ident+'-v1', document_id=ident, original_url=url, final_url=url, document_date=date, version_label={'register':'TBMM kayıt ekranı', 'question':'TBMM yazılı soru', 'answer':'Bakanlık yanıtı, bir sayfa görsel okundu'}[role], accessed_at=now, verified_at=now, mime='text/html' if typ=='html' else 'application/pdf', sha256=sha, original_path='objects/'+sha+'/'+original, readable_path='objects/'+sha+'/readable.html', date_precision='day' if date else 'unknown', date_unknown_reason=None if date else 'Belgenin yayımlanma tarihi doğrulanmadı.')
    if typ == 'html':
        view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
        view['version_id'] = ident+'-v1'
        validate_view(root, view)
        add('archive_view', **view)
        exact = '7 / 26431'
        assert exact in html_source_text(raw)
        add('passage', id=ident+'-number-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='Soru esas numarası', pdf_page_index=None, printed_page=None)
    if role == 'question':
        exact = 'TPI fabrikasında yürütülen toplu iş sözleşmesi süreci Bakanlığınızca izlenmekte'
        assert exact in pdf_page_text(Path(path), 1)
        add('passage', id=ident+'-sale-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='TPI toplu iş sözleşmesine ilişkin soru', pdf_page_index=1, printed_page=None)
    add('source_attribution', version_id=ident+'-v1', kind='official', publisher='Türkiye Büyük Millet Meclisi', author='Çalışma ve Sosyal Güvenlik Bakanlığı' if role == 'answer' else None, social_handle=None, published_at=None, date_precision='unknown', public_url=url, basis=('22.09.2025 tarihli Bakanlık yanıtı; TBMM bildirilişi 23.09.2025; yayım tarihi çıkarılmadı.' if role == 'answer' else 'TBMM resmî kayıt, soru ve bakanlık yanıtı ayrı belgelerdir; yayın tarihi çıkarılmadı.'))
    print(role, sha)

out = Path(__file__).parent / "tpi-26431-source-draft.json"
with out.open("x") as f:
    json.dump(dict(status="source_read_partial", entries=entries, note="8 Nisan 2025 soru, 22 Eylül Bakanlık yanıtı, 23 Eylül bildirim. Bir sayfa yanıt görsel okundu; iddialar ve Bakanlık beyanları ayrı."), f, ensure_ascii=False, indent=2)
    f.write("\n")
