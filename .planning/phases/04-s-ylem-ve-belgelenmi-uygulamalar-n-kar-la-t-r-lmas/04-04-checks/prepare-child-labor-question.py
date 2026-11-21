import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/yeni-parti')
capture = Path('/tmp/gsd-0404-751913.html')
raw = capture.read_bytes()
digest = hashlib.sha256(raw).hexdigest()
assert digest == 'd8deccb63168c5581249b62bed77a56e23f4d7d0c5f487370d2e6f2a4c367b13'
folder = root/'objects'/digest
folder.mkdir(parents=True, exist_ok=True)
for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
    dest = folder/name
    if dest.exists():
        assert dest.read_bytes() == content
    else:
        dest.write_bytes(content)
url = 'https://www.tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/3b62f539-25e5-4155-b4f1-01a17d34c9f1'
ident = '0404-tbmm-cocuk-soru-51913'
view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
view['version_id'] = ident+'-v1'
validate_view(root, view)
text = html_source_text(raw)
exact = '&#xC7;ocuk i&#x15F;&#xE7;ili&#x11F;i ile m&#xFC;cadeleye ili&#x15F;kin'
assert exact in text and '7 / 51913' in text
accessed = datetime.fromtimestamp(capture.stat().st_mtime, timezone.utc).isoformat(timespec='seconds')
verified = datetime.now(timezone.utc).isoformat(timespec='seconds')
entries = [
    ('document', dict(id=ident, party_id='yeni-parti', title='7/51913 çocuk işçiliği yazılı soru önergesi', source_kind='official')),
    ('document_version', dict(id=ident+'-v1', document_id=ident, original_url=url, final_url=url.replace('www.tbmm.gov.tr', 'tbmm.gov.tr'), document_date=None, version_label='TBMM dinamik kayıt sayfası; yakalanan HTML', accessed_at=accessed, verified_at=verified, mime='text/html', sha256=digest, original_path='objects/'+digest+'/original.html.bin', readable_path='objects/'+digest+'/readable.html', date_precision='unknown', date_unknown_reason='Dinamik sayfanın yayın tarihi bilinmiyor; soru tarihi ayrı kaydedilir.')),
    ('archive_view', view),
    ('passage', dict(id=ident+'-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='7/51913 soru özeti', pdf_page_index=None, printed_page=None)),
    ('source_attribution', dict(version_id=ident+'-v1', kind='official', publisher='Türkiye Büyük Millet Meclisi', author=None, social_handle=None, published_at=None, date_precision='unknown', public_url=url, basis='TBMM kurumsal başlığı ve soru önergesi künyesi incelendi.')),
]
out = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/child-labor-question-records-draft.json')
out.write_text(json.dumps(dict(status='draft_unvalidated', source_root=str(root), entries=[dict(kind=k, values=v) for k, v in entries]), ensure_ascii=False, indent=2)+'\n')
print(view['view_id'], digest)
