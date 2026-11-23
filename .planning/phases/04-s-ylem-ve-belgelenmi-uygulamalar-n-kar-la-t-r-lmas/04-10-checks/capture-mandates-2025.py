import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

D = Path(__file__).parent
root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('speech', 'html', 'https://tbmm.gov.tr/milletvekili/UyeGenelKurulKonusmalariDetay?eid=138119'),
    ('transcript', 'pdf', 'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/9/Tam/52b66e2b-6fdc-4d12-aa41-703b4fc2c246.pdf'),
]
entries = []
for role, typ, url in sources:
    path = D / 'mandates-2025' / (role + ('.html' if typ == 'html' else '.pdf'))
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    obj = root / 'objects' / sha
    obj.mkdir(parents=True, exist_ok=True)
    original = 'original.html.bin' if typ == 'html' else 'original.pdf'
    for name, content in [(original, raw), ('readable.html', readable_bytes(raw, typ, legacy=False))]:
        dst = obj / name
        if dst.exists(): assert dst.read_bytes() == content
        else: dst.write_bytes(content)
    doc = '0410-emep-mandates-2025-' + role
    version = doc + '-v1'
    entries.extend([
        dict(kind='document', values=dict(id=doc, party_id='emep', title='TBMM 21 Ekim 2025 '+('Karaca açıklaması' if role == 'speech' else '9. birleşim tutanağı'), source_kind='official')),
        dict(kind='document_version', values=dict(id=version, document_id=doc, original_url=url, final_url=url, document_date='2025-10-21', date_precision='day', date_unknown_reason=None, version_label='TBMM 28. dönem 4. yasama yılı 9. birleşim', accessed_at=now, verified_at=now, mime='text/html' if typ == 'html' else 'application/pdf', sha256=sha, original_path='objects/'+sha+'/'+original, readable_path='objects/'+sha+'/readable.html')),
        dict(kind='source_attribution', values=dict(version_id=version, kind='official', publisher='Türkiye Büyük Millet Meclisi', author='Sevda Karaca Demir' if role == 'speech' else None, social_handle=None, published_at=None, date_precision='unknown', public_url=url, basis='Birleşim ve konuşma tarihi 21 Ekim 2025; yayın tarihi ayrı. İki tezkere ve beyan/oylama ayrıdır.')),
    ])
    if typ == 'html':
        view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
        view['version_id'] = version
        validate_view(root, view)
        entries.append(dict(kind='archive_view', values=view))
        exact = 'Bugün Mecliste Lübnan, Irak-Suriye tezkereleri oylanacak, biz Emek Partisi olarak "hayır" diyoruz.'
        assert exact in html_source_text(raw)
        entries.append(dict(kind='passage', values=dict(id=doc+'-position-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section='Genel Kurul açıklaması', pdf_page_index=None, printed_page=None)))
    else:
        for num, page in [('1199', 40), ('1200', 58)]:
            exact = 'BAŞKAN - Sayın milletvekilleri, (3/'+num+') esas numaralı Cumhurbaşkanlığı Tezkeresi üzerindeki görüşmeler\ntamamlanmıştır.\nTezkereyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Kabul edilmiştir.'
            assert exact in pdf_page_text(path, page)
            entries.append(dict(kind='passage', values=dict(id=doc+'-'+num+'-vote-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section='Tezkere oylaması', pdf_page_index=page, printed_page=None)))
    print(role, sha)
with (D/'mandates-2025-source-draft.json').open('x') as f:
    json.dump(dict(entries=entries, status='source_read_package_pending', note='Karaca iki tezkereye karşı tutumu açıkladı; iki ayrı işaret oylaması kabul edildi, kişisel kesin oy gösterilmedi.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
