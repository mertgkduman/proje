import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes, pdf_page_text
from arsiv_gorunum import build_view, validate_view

D = Path(__file__).parent
root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('official', 'pdf', 'https://www.resmigazete.gov.tr/eskiler/2021/07/20210715M1-2.pdf', Path('/tmp/gsd-emep-bulu-20210715.pdf'), '2021-07-15'),
    ('party', 'html', 'https://www.emep.org/emek-partisi-emep-merkez-yonetim-kurulundan-cagri', Path('/tmp/gsd-emep-4214-party.html'), '2021-08-02'),
]
entries = []
def add(table, **values):
    entries.append(dict(kind=table, values=values))
for role, typ, url, path, day in sources:
    raw = path.read_bytes(); digest = hashlib.sha256(raw).hexdigest()
    if role == 'official':
        assert digest == 'b32a832f0e68d03f027d31dc84c5524be5bf056f8ac889883906c14ec5da3d58'
    obj = root / 'objects' / digest; obj.mkdir(parents=True, exist_ok=True)
    original = 'original.pdf' if typ == 'pdf' else 'original.html.bin'
    for name, content in ((original, raw), ('readable.html', readable_bytes(raw, typ, legacy=False))):
        target = obj / name
        if target.exists(): assert target.read_bytes() == content
        else: target.write_bytes(content)
    doc = '0410-emep-bulu-2021-' + role; version = doc + '-v1'
    add('document', id=doc, party_id='emep', title='Bulu görevden alma kararı' if role == 'official' else 'EMEP MYK toplantı açıklaması', source_kind='official' if role == 'official' else 'party')
    add('document_version', id=version, document_id=doc, original_url=url, final_url=url, document_date=day, date_precision='day', date_unknown_reason=None, version_label='15 Temmuz mükerrer Resmî Gazete' if role == 'official' else '2 Ağustos EMEP MYK açıklaması', accessed_at=now, verified_at=now, mime='application/pdf' if typ == 'pdf' else 'text/html', sha256=digest, original_path='objects/'+digest+'/'+original, readable_path='objects/'+digest+'/readable.html')
    exact = ('Boğaziçi Üniversitesi Rektörü Prof. Dr. Melih BULU, 2547 sayılı Yükseköğretim Kanununun ek 1 inci maddesi ile 3 sayılı Cumhurbaşkanlığı Kararnamesinin 2 nci maddesi gereğince görevden alınmıştır.' if role == 'official' else 'Melih Bulu’nun istifasıyla sonuçlanan bu mücadele')
    pid = doc + '-p'
    if typ == 'html':
        assert exact in html_source_text(raw)
        view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8'); view['version_id'] = version; validate_view(root, view); add('archive_view', **view)
    add('passage', id=pid, version_id=version, exact=exact, prefix=None, suffix=None, article=None, section='2021/360 sayılı karar' if role == 'official' else 'Yükseköğretim ve mücadele', pdf_page_index=6 if typ == 'pdf' else None, printed_page=None)
    if typ == 'pdf' and exact not in pdf_page_text(path, 6):
        add('manual_passage', passage_id=pid, checked_at=now, method='Özgün PDF sayfa 7 Poppler/Cairo ile görüntülendi ve karar görsel okundu.', reason='Karar gövdesi çıkarılabilir metin katmanında bulunmadı.')
    add('source_attribution', version_id=version, kind='official' if role == 'official' else 'party', publisher='T.C. Resmî Gazete' if role == 'official' else 'Emek Partisi', author='Cumhurbaşkanlığı' if role == 'official' else 'Emek Partisi Merkez Yönetim Kurulu', social_handle=None, published_at=day, date_precision='day', public_url=url, basis='14 Temmuz 2021 tarihli karar 15 Temmuz mükerrer sayıda yayımlandı.' if role == 'official' else 'Parti açıklamasının özgün sayfa tarihi ve MYK imzası.')
    print(role, digest)
out = D / 'bulu-2021-source-draft.json'
with out.open('x') as f: json.dump(dict(status='source_read_package_pending', entries=entries), f, ensure_ascii=False, indent=2); f.write('\n')
