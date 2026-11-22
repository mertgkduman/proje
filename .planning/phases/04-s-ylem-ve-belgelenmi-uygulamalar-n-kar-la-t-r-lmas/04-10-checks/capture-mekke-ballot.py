import hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv_gorunum import build_view, validate_view

sha = 'dee8048e3732d2414f3db05c106dfa60b39b8d7a92cff70bb31198527e0939da'
url = 'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/14/AcikOylamaSonuc/cbfb34cb-f290-4c39-a3b3-b902717425ea.html'
old = Path('data/practices/sources/yeni-parti/objects') / sha
root = Path('data/practices/sources/emep')
obj = root / 'objects' / sha
raw = (old / 'original.html.bin').read_bytes()
assert hashlib.sha256(raw).hexdigest() == sha
obj.mkdir(parents=True, exist_ok=True)
for name in ('original.html.bin', 'readable.html'):
    content = (old / name).read_bytes()
    dest = obj / name
    if dest.exists():
        assert dest.read_bytes() == content
    else:
        dest.write_bytes(content)
ident = '0410-emep-mekke-ballot'
version = ident + '-v1'
view = build_view(raw, url, root, fetch_assets=False, http_charset='windows-1254')
view['version_id'] = version
validate_view(root, view)
text = raw.decode('windows-1254')
rows = []
def add(k, **values): rows.append({'kind': k, 'values': values})
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
add('document', id=ident, party_id='emep', title='TBMM 5 Kasım 2026 Mekke anlaşması açık oylama cetveli', source_kind='official')
add('document_version', id=version, document_id=ident, document_date='2026-11-05', date_precision='day', date_unknown_reason=None, version_label='5 Kasım 2026 tarihli açık oylamanın kesin cetveli; yayın zamanı ayrıca bilinmiyor.', original_url=url, final_url=url, accessed_at=now, verified_at=now, mime='text/html', sha256=sha, original_path=f'objects/{sha}/original.html.bin', readable_path=f'objects/{sha}/readable.html')
add('archive_view', **view)
add('source_attribution', version_id=version, publisher='TBMM Tutanak Hizmetleri Başkanlığı', author=None, kind='official', published_at=None, date_precision='unknown', social_handle=None, public_url=url, basis='TBMM kesin açık oylama cetveli; olay tarihi 5 Kasım, yayın zamanı ayrı doğrulanmadı.')
for key, needle, section in [('bayhan', '<td>BAYHAN</td>', 'İskender Bayhan oylama satırı'), ('karaca', '<td>KARACA DEM&#x130;R</td>', 'Sevda Karaca Demir oylama satırı')]:
    found = [row for row in re.findall(r'<tr[^>]*>.*?</tr>', text, re.S | re.I) if needle in row]
    assert len(found) == 1 and 'Emek Partisi' in found[0]
    exact = found[0][4:-5].strip()
    add('passage', id=ident + '-' + key + '-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=None, printed_page=None)
assert 'RET' in next(x['values']['exact'] for x in rows if x['kind'] == 'passage' and 'bayhan' in x['values']['id'])
assert 'KATILMADI' in next(x['values']['exact'] for x in rows if x['kind'] == 'passage' and 'karaca' in x['values']['id'])
out = Path(__file__).parent / 'mekke-ballot-source-draft.json'
with out.open('x') as f:
    json.dump({'status': 'draft_unvalidated', 'entries': rows, 'note': 'Bayhan RET; Karaca Demir KATILMADI, nedeni çıkarılmaz. 24 Ağustos sorusu ayrı olaydır.'}, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('MEKKE_BALLOT_SOURCE_OK', sha, view['view_id'])
