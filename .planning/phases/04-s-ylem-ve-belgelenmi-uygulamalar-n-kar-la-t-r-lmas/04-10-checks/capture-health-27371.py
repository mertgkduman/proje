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
    ('register', 'html', '/tmp/gsd0410-health27371/detail.html', 'https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/dd30aad9-f3e4-4761-8434-01963dc213f4'),
    ('question', 'pdf', '/tmp/gsd0410-health27371/question.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/1bc7c191-6680-4a02-9a1e-65f5fd64a1de.pdf'),
    ('notice', 'html', '/tmp/gsd0410-health27371/gelen.html', 'https://www.tbmm.gov.tr/Gundem/GelenKagitDetay/a4473e5c-75f5-42e5-bf83-0196f7260e97'),
]
def add(record_kind, **values):
    entries.append(dict(kind=record_kind, values=values))

for role, typ, path, url in sources:
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    obj = root / 'objects' / sha
    obj.mkdir(parents=True, exist_ok=True)
    original = 'original.html.bin' if typ == 'html' else 'original.pdf'
    ident = '0410-emep-question-27371-' + role
    for name, content in [(original, raw), ('readable.html', readable_bytes(raw, typ, legacy=False))]:
        dest = obj / name
        if dest.exists():
            assert dest.read_bytes() == content
        else:
            dest.write_bytes(content)
    add('document', id=ident, party_id='emep', title='TBMM 7/27371 ' + {'register':'kayıt', 'question':'yazılı soru', 'notice':'gelen kağıt ilanı'}[role], source_kind='official')
    date = {'question': '2025-04-15', 'notice': '2025-05-22'}.get(role)
    add('document_version', id=ident+'-v1', document_id=ident, original_url=url, final_url=url, document_date=date, version_label={'register':'TBMM kayıt ekranı', 'question':'TBMM yazılı soru', 'notice':'22 Mayıs 2025 gelen kağıt ilanı'}[role], accessed_at=now, verified_at=now, mime='text/html' if typ=='html' else 'application/pdf', sha256=sha, original_path='objects/'+sha+'/'+original, readable_path='objects/'+sha+'/readable.html', date_precision='day' if date else 'unknown', date_unknown_reason=None if date else 'Belgenin yayımlanma tarihi doğrulanmadı.')
    if typ == 'html':
        view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
        view['version_id'] = ident+'-v1'
        validate_view(root, view)
        add('archive_view', **view)
        exact = '7 / 27371' if role == 'register' else '7/27371'
        assert exact in html_source_text(raw)
        add('passage', id=ident+'-number-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='Soru esas numarası', pdf_page_index=None, printed_page=None)
    if role == 'question':
        exact = 'Sağlık hizmetlerinin özelleştirilmesi ve ticarileştirilmesinin , halkın sağlık hizmetlerine'
        assert exact in pdf_page_text(Path(path), 1)
        add('passage', id=ident+'-sale-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='İş sağlığı ve hastalıklarına ilişkin yazılı soru', pdf_page_index=1, printed_page=None)
    add('source_attribution', version_id=ident+'-v1', kind='official', publisher='Türkiye Büyük Millet Meclisi', author='Türkiye Büyük Millet Meclisi' if role == 'notice' else None, social_handle=None, published_at=None, date_precision='unknown', public_url=url, basis=('22 Mayıs 2025 gelen kağıtlar, süresinde cevaplanmayan soru ilanı.' if role == 'notice' else 'TBMM resmî kayıt ve soru ayrı belgelerdir; yayın tarihi çıkarılmadı.'))
    print(role, sha)

out = Path(__file__).parent / "health-27371-source-draft.json"
with out.open("x") as f:
    json.dump(dict(status="source_read_partial", entries=entries, note="15 Nisan 2025 soru, 22 Mayıs 2025 süre içi yanıtsızlık ilanı; iddialar atıflı, sonraki durum çıkarılmaz."), f, ensure_ascii=False, indent=2)
    f.write("\n")
