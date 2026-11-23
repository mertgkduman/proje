import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

D = Path(__file__).parent
root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
specs = [
    ('report', 'pdf', 'emep-second-year-earthquake-2025.pdf', 'https://www.emep.org/wp-content/uploads/2025/02/2.-Yil-Deprem-Raporu-EMEP.pdf', '2025-02-05', 'party', 'party_publication', 'Emek Partisi', 'Emek Partisi', 'İkinci yıl deprem raporu'),
    ('news', 'html', 'earthquake-workshop-2025-ekspres.html', 'https://www.gazeteekspres.com/hesaplasilmamis-her-suc-yeni-suclari-doguruyor', '2025-02-02', 'journalism', 'journalism', 'Gaziantep Ekspres', 'Samet Koçum', 'Gaziantep deprem çalıştayı haberi'),
]
entries = []
for role, typ, filename, url, date, source_kind, attribution_kind, publisher, author, title in specs:
    raw = (D / filename).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    obj = root / 'objects' / sha
    obj.mkdir(parents=True, exist_ok=True)
    original = 'original.pdf' if typ == 'pdf' else 'original.html.bin'
    for name, content in [(original, raw), ('readable.html', readable_bytes(raw, typ, legacy=False))]:
        path = obj / name
        if path.exists():
            assert path.read_bytes() == content
        else:
            path.write_bytes(content)
    doc = '0410-emep-earthquake-workshop-2025-' + role
    version = doc + '-v1'
    entries.append(dict(kind='document', values=dict(id=doc, party_id='emep', title=title, source_kind=source_kind)))
    entries.append(dict(kind='document_version', values=dict(id=version, document_id=doc, original_url=url, final_url=url, document_date=date, date_precision='day', date_unknown_reason=None, version_label=title, accessed_at=now, verified_at=now, mime='application/pdf' if typ == 'pdf' else 'text/html', sha256=sha, original_path='objects/'+sha+'/'+original, readable_path='objects/'+sha+'/readable.html')))
    if typ == 'html':
        view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
        view['version_id'] = version
        validate_view(root, view)
        entries.append(dict(kind='archive_view', values=view))
        exact = 'Emek Partisi, 6 Şubat 2023 tarihinde meydana gelen ve büyük yıkıma yol açan depremlerin 2. yıldönümü dolayısıyla Gaziantep’te bir çalıştay düzenledi.'
        assert exact in html_source_text(raw)
        page = None
    else:
        exact = 'Emek Partisi olarak, 6 Şubat depreminin 2. yıldönümü öncesi Gaziantep’te bir buluşma'
        assert exact in pdf_page_text(obj / original, 15)
        page = 15
    entries.append(dict(kind='passage', values=dict(id=doc+'-p', version_id=version, exact=exact, prefix=None, suffix=None, article=None, section=title, pdf_page_index=page, printed_page=None)))
    entries.append(dict(kind='source_attribution', values=dict(version_id=version, kind=attribution_kind, publisher=publisher, author=author, social_handle=None, published_at=date, date_precision='day', public_url=url, basis='Özgün parti raporu ve ayrı gazeteci haberi; duyuru tarihi, toplantının gerçekleşmesi ve önerilerin sonraki sonucu ayrı değerlendirilir.')))
    print(role, sha)

out = D / 'earthquake-workshop-2025-source-draft.json'
with out.open('x') as f:
    json.dump(dict(status='source_read_package_pending', entries=entries, note='Raporun Hatay sunumu mevcut ayrı olaydır; Gaziantep çalıştayı için haberde kesin gün açık değil. Toplantıdaki öneriler gerçekleşmiş sonuç değildir.'), f, ensure_ascii=False, indent=2)
    f.write('\n')
