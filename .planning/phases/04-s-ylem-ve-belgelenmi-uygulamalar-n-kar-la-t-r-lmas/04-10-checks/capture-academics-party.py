import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

D = Path(__file__).parent
root = Path('data/practices/sources/emep')
raw = (D / 'academics-37207/party.html').read_bytes()
url = 'https://www.emep.org/iskender-bayhan-mevsimlik-akademisyenlik-dayatiliyor'
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sha = hashlib.sha256(raw).hexdigest()
obj = root / 'objects' / sha
obj.mkdir(parents=True, exist_ok=True)
for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
    path = obj / name
    if path.exists(): assert path.read_bytes() == content
    else: path.write_bytes(content)
doc = '0410-emep-academics-37207-party'
version = doc + '-v1'
view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
view['version_id'] = version
validate_view(root, view)
exact = 'Sendikal hak ve özgürlüklerin fiilen yok sayılmasının'
assert exact in html_source_text(raw)
entries = [
    dict(kind='document', values=dict(id=doc, party_id='emep', title='Bayhan’ın vakıf üniversitelerinde akademisyenler hakkındaki sorusu', source_kind='party')),
    dict(kind='document_version', values=dict(id=version, document_id=doc, original_url=url, final_url=url, document_date='2025-12-02', date_precision='day', date_unknown_reason=None, version_label='2 Aralık 2025 parti yayını', accessed_at=now, verified_at=now, mime='text/html', sha256=sha, original_path='objects/'+sha+'/original.html.bin', readable_path='objects/'+sha+'/readable.html')),
    dict(kind='archive_view', values=view),
    dict(kind='source_attribution', values=dict(version_id=version, kind='party_publication', publisher='Emek Partisi', author='Emek Partisi', social_handle=None, published_at='2025-12-02', date_precision='day', public_url=url, basis='Parti yayını soru ve iddiaları aktarır; yanıt ve fiilî sonuç ayrıca değerlendirilir.')),
    dict(kind='passage', values=dict(id=doc+'-union-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section='Bayhan yazılı soru içeriği', pdf_page_index=None, printed_page=None)),
]
with (D / 'academics-37207-party-source-draft.json').open('x') as f:
    json.dump(dict(entries=entries, status='source_read_package_pending'), f, ensure_ascii=False, indent=2)
    f.write('\n')
print(sha, view['view_id'])
