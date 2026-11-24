import json, sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

c = Path(__file__).resolve().parent
sources = c / 'tezkere-1231-sources'
root = Path('data/practices/sources/emep')
reading = json.loads((sources / 'reading.json').read_text())
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
entries = []
specs = [
    ('emep-3379.html.bin', 'party', '2019-10-08', 'EMEP sınır ötesi tezkere açıklaması', [(None, 'call', 'Milletvekillerine ret çağrısı', 'meclisteki milletvekillerine tezkerede hayır oyu vermeleri çağrısında\nbulunuyoruz.'), (None, 'east', 'Fıratın doğusu', 'Fırat’ın doğusu')]),
    ('tbmm-27-3-3-printed.pdf', 'floor', None, 'TBMM 8 Ekim 2019 tam birleşim tutanağı', [(95, 'request', '3/878 ve iznin 30 Ekimden uzatılması', '30/10/2019\ntarihinden itibaren bir yıl uzatılmasına dair tezkeresi (3/878)'), (122, 'accepted', '3/878 tezkere kabulü', 'Anayasa’nın 92’nci maddesine göre verilen (3/878) esas numaralı Cumhurbaşkanlığı Tezkeresi kabul\nedilmiştir.'), (122, 'closing', 'İkinci oturum kapanış saati', 'Kapanma Saati: 19.36'), (95, 'opening', 'İkinci oturum açılış saati', 'Açılma Saati: 17.23')]),
    ('tbmm-2020-3-1324-context.html.bin', 'later', None, '2020 TBMM tutanağında 1231 sayılı karara atıf', [(None, 'registry', 'Sonraki görüşmede 2019 tarihli 1231e atıf', '08.10.2019\r\nTarihli ve 1231')]),
]
def add(table, **values): entries.append({'kind': table, 'values': values})
for filename, role, day, title, anchors in specs:
    row = next(x for x in reading['sources'] if x['original'] == filename)
    raw = (sources / filename).read_bytes(); digest = sha256(raw).hexdigest(); assert digest == row['sha256']
    fmt = 'pdf' if filename.endswith('.pdf') else 'html'; url = row['url']
    obj = root / 'objects' / digest; obj.mkdir(parents=True, exist_ok=True)
    original = obj / ('original.pdf' if fmt == 'pdf' else 'original.html.bin'); readable = obj / 'readable.html'
    for path, blob in ((original, raw), (readable, readable_bytes(raw, fmt, legacy=False))):
        if path.exists(): assert path.read_bytes() == blob
        else: path.write_bytes(blob)
    doc = '0410-tezkere-1231-' + role; ver = doc + '-v1'; party = role == 'party'
    add('document', id=doc, party_id='emep', title=title, source_kind='party' if party else 'official')
    add('document_version', id=ver, document_id=doc, original_url=url, final_url=url, document_date=day, date_precision='day' if day else 'unknown', date_unknown_reason=None if day else 'Tutanağın ilk elektronik yayımlanma tarihi belirlenmedi; birleşim tarihi metinde yer alır.', version_label=title, accessed_at=now, verified_at=now, mime='application/pdf' if fmt == 'pdf' else 'text/html', sha256=digest, original_path=str(original.relative_to(root)), readable_path=str(readable.relative_to(root)))
    add('source_attribution', version_id=ver, kind='party_publication' if party else 'official', publisher='Emek Partisi' if party else row['publisher'], author='EMEP Genel Merkezi' if party else None, social_handle=None, published_at=day, date_precision='day' if day else 'unknown', public_url=url, basis='Özgün parti açıklaması' if party else 'TBMM birleşim tutanağı; sonraki tutanakta geçmiş karara atıf ayrı tutulur.')
    if fmt == 'html':
        view = build_view(raw, url, root, fetch_assets=False); view['version_id'] = ver; validate_view(root, view); add('archive_view', **view)
    for page, suffix, section, exact in anchors:
        text = html_source_text(raw) if page is None else pdf_page_text(sources / filename, page)
        assert exact in text, (role, suffix)
        add('passage', id=doc+'-'+suffix+'-p', version_id=ver, exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=page, printed_page=str(page+203) if page is not None else None)
    print(role, digest)
with (c/'tezkere-1231-source-draft-v2.json').open('x') as f:
    json.dump({'entries': entries}, f, ensure_ascii=False, indent=2); f.write('\n')
print('TEZKERE1231_CAPTURE_OK', len(entries))
