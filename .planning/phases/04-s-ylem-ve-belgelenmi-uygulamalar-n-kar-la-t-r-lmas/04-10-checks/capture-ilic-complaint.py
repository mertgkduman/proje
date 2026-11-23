import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

D = Path(__file__).parent
root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('party', 'ilic-complaint-20240315-emep-retry.html', 'https://www.emep.org/erzincan-ilicte-sorumlular-yargilansin-kaza-degil-cinayet', 'Emek Partisi', 'party_publication', 'Emek Partisi olarak Erzincan İliç’te yaşanan felaketin bütün sorumluları hakkında suç duyurusunda bulunmak için toplanmış bulunuyoruz.'),
    ('news', 'ilic-complaint-20240315-cumhuriyet.html', 'https://www.cumhuriyet.com.tr/siyaset/emepten-ilic-icin-suc-duyurusu-sorumlulugu-olanlar-yargilansin-2186092', 'Cumhuriyet', 'journalism', 'Emek Partisi (EMEP) Genel Başkanı Seyit Aslan, bugün İstanbul Çağlayan Adliyesi’ne giderek söz konusu madenin işletilmesinde sorumluluğu bulunan kamu görevlileri hakkında suç duyurusunda bulundu.'),
]
entries = []
for role, filename, url, publisher, kind, exact in sources:
    raw = (D / filename).read_bytes()
    assert exact in html_source_text(raw)
    digest = hashlib.sha256(raw).hexdigest()
    obj = root / 'objects' / digest
    obj.mkdir(parents=True, exist_ok=True)
    for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        path = obj / name
        if path.exists(): assert path.read_bytes() == content
        else: path.write_bytes(content)
    doc = '0410-emep-ilic-complaint-' + role
    version = doc + '-v1'
    entries.append(dict(kind='document', values=dict(id=doc, party_id='emep', title='İliç için suç duyurusu: ' + publisher, source_kind='party' if role == 'party' else 'journalism')))
    entries.append(dict(kind='document_version', values=dict(id=version, document_id=doc, original_url=url, final_url=url, document_date='2024-03-15', date_precision='day', date_unknown_reason=None, version_label='Özgün yayın', accessed_at=now, verified_at=now, mime='text/html', sha256=digest, original_path='objects/'+digest+'/original.html.bin', readable_path='objects/'+digest+'/readable.html')))
    view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
    view['version_id'] = version
    validate_view(root, view)
    entries.append(dict(kind='archive_view', values=view))
    entries.append(dict(kind='passage', values=dict(id=doc+'-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section='Suç duyurusu', pdf_page_index=None, printed_page=None)))
    entries.append(dict(kind='source_attribution', values=dict(version_id=version, kind=kind, publisher=publisher, author=None, social_handle=None, published_at='2024-03-15', date_precision='day', public_url=url, basis='Parti açıklaması ve 15 Mart tarihli haber; duyuru başvurusu yargılama sonucu değildir.')))
    print(role, digest, view['view_id'])
with (D / 'ilic-complaint-20240315-source-draft.json').open('x') as f:
    json.dump(dict(status='source_read_package_pending', entries=entries, note='Parti metnindeki dilekçede olay yılı bir yerde 2023, diğer yerlerde 2024; 15 Mart 2024 başvuru ve karar ayrı tutulur. Cumhuriyet o gün dokuz işçiye ulaşılamadığını bildirir.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
