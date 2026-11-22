import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

capture = Path('/tmp/gsd-0407-research/bianet.html')
raw = capture.read_bytes()
digest = hashlib.sha256(raw).hexdigest()
assert digest == 'ba292e3091f3e64f55b34197b4387f5276da353d35982f8a9ba0ccbd8679bab0'
exact = "Tek aday olan Akşener, 1151 delegenin 1127'sinin geçerli oyunu aldı."
assert html_source_text(raw).count(exact) == 1
root = Path('data/practices/sources/iyi')
folder = root / 'objects' / digest
folder.mkdir(parents=True, exist_ok=True)
for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
    dest = folder / name
    if dest.exists():
        assert dest.read_bytes() == content
    else:
        dest.write_bytes(content)
url = 'https://bianet.org/haber/iyi-parti-de-3-olagan-kurultay-aksener-yeniden-genel-baskan-280801'
ident = '0407-iyi-2023-kurultay-bianet'
view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
view['version_id'] = ident + '-v1'
validate_view(root, view)
access = datetime.fromtimestamp(capture.stat().st_mtime, timezone.utc).isoformat(timespec='seconds')
checked = datetime.now(timezone.utc).isoformat(timespec='seconds')
rows = [
    ('document', dict(id=ident, party_id='iyi', title='İYİ Parti 3. Olağan Kurultayında genel başkan seçimi', source_kind='journalism')),
    ('document_version', dict(id=ident+'-v1', document_id=ident, original_url=url, final_url=url, document_date='2023-06-24', version_label='24 Haziran 2023 yayınlanan ve aynı gün güncellenen haber', accessed_at=access, verified_at=checked, mime='text/html', sha256=digest, original_path='objects/'+digest+'/original.html.bin', readable_path='objects/'+digest+'/readable.html', date_precision='day', date_unknown_reason=None)),
    ('archive_view', view),
    ('passage', dict(id=ident+'-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='Genel başkan seçimi sonucu', pdf_page_index=None, printed_page=None)),
    ('source_attribution', dict(version_id=ident+'-v1', kind='journalism', publisher='bianet', author=None, social_handle=None, published_at='2023-06-24', date_precision='day', public_url=url, basis='Yayıncı ve sayfa yayın/güncelleme tarihi okundu; imzasız haber.')),
]
out = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-07-checks/bianet-2023-source-draft.json')
out.write_text(json.dumps(dict(status='draft_unvalidated', entries=[dict(kind=k, values=v) for k,v in rows]), ensure_ascii=False, indent=2)+'\n')
print('view', view['view_id'], 'sha256', digest)
