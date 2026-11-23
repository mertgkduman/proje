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
    ('register', 'html', '/tmp/gsd0410-cayirhan/register.html', 'https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/0943828b-af2b-49ca-a4ba-0193bec24286'),
    ('question', 'pdf', '/tmp/gsd0410-cayirhan/question.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/f7d66c63-d98e-40aa-9490-8ed2052d06d8.pdf'),
    ('answer', 'pdf', '/tmp/gsd0410-cayirhan/reply.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/6e1c0772-3375-4b9a-8918-df35b6894a94.pdf'),
]
def add(record_kind, **values):
    entries.append(dict(kind=record_kind, values=values))

for role, typ, path, url in sources:
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    obj = root / 'objects' / sha
    obj.mkdir(parents=True, exist_ok=True)
    original = 'original.html.bin' if typ == 'html' else 'original.pdf'
    ident = '0410-emep-question-20948-' + role
    for name, content in [(original, raw), ('readable.html', readable_bytes(raw, typ, legacy=False))]:
        dest = obj / name
        if dest.exists():
            assert dest.read_bytes() == content
        else:
            dest.write_bytes(content)
    add('document', id=ident, party_id='emep', title='TBMM 7/20948 ' + {'register':'kayıt', 'question':'yazılı soru', 'answer':'bakanlık yanıtı'}[role], source_kind='official')
    date = '2024-12-12' if role == 'question' else None
    add('document_version', id=ident+'-v1', document_id=ident, original_url=url, final_url=url, document_date=date, version_label={'register':'TBMM kayıt ekranı', 'question':'TBMM yazılı soru', 'answer':'Bakanlık yanıtı, iki sayfa görsel okundu'}[role], accessed_at=now, verified_at=now, mime='text/html' if typ=='html' else 'application/pdf', sha256=sha, original_path='objects/'+sha+'/'+original, readable_path='objects/'+sha+'/readable.html', date_precision='day' if date else 'unknown', date_unknown_reason=None if date else 'Belgenin yayımlanma tarihi doğrulanmadı.')
    if typ == 'html':
        view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
        view['version_id'] = ident+'-v1'
        validate_view(root, view)
        add('archive_view', **view)
        exact = '7 / 20948'
        assert exact in html_source_text(raw)
        add('passage', id=ident+'-number-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='Soru esas numarası', pdf_page_index=None, printed_page=None)
    if role == 'question':
        exact = 'lojmanları ile birlikte satılmasında ne gibi bir kamu yararı vardır?'
        assert exact in pdf_page_text(Path(path), 1)
        add('passage', id=ident+'-sale-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='Satışa ilişkin yazılı soru', pdf_page_index=1, printed_page=None)
    add('source_attribution', version_id=ident+'-v1', kind='official', publisher='Türkiye Büyük Millet Meclisi', author=None, social_handle=None, published_at=None, date_precision='unknown', public_url=url, basis='TBMM resmî kayıt, soru ve bakanlık yanıtı ayrı belgelerdir; yayın tarihi çıkarılmadı.')
    print(role, sha)

out = Path(__file__).parent/'cayirhan-question-source-draft.json'
with out.open('x') as f:
    json.dump(dict(status='source_read_partial', entries=entries, note='7/20948 12 Aralık 2024 soru, TBMM kayıt ekranında 22 Ocak 2025 yanıt bildirimi. Bakan yanıtının iki sayfası görsel okundu; süreç ve 4 Mart 2025 teklif süresi anlatılır, nihai satış sonucu çıkarılmaz. Soru PDF OCR soyadını BAYMAN okur; resmî kayıt ve bakan yanıtı BAYHAN gösterir.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
