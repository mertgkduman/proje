"""5367 tutanağının partiye özgü kayıtları; bağımsız taslak için, canlı terfi değil."""
import datetime, hashlib, json
from pathlib import Path
from arsiv import pdf_page_text

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
capture = json.loads((p.parent / '04-05-checks/mdkd-5367-capture.json').read_text())
sha = '64125de3b7a7d716711595ea16dc8a68c618976ba514de0e840ba065cc0ae04d'
rel = f'objects/{sha}'
path = Path('data/practices/sources/dem') / rel / 'original.pdf'
assert hashlib.sha256(path.read_bytes()).hexdigest() == capture['sha256'] == sha
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
doc = '0406-2026-mdkd-5367'
version = doc + '-v1'
url = capture['url']
entries = [
    {'kind': 'document', 'values': {'id': doc, 'party_id': 'dem', 'title': '18 Şubat 2026 Millî Dayanışma, Kardeşlik ve Demokrasi Komisyonu 21. toplantı tutanağı', 'source_kind': 'official'}},
    {'kind': 'document_version', 'values': {'id': version, 'document_id': doc, 'original_url': url, 'final_url': url, 'document_date': '2026-02-18', 'date_precision': 'day', 'date_unknown_reason': None, 'version_label': 'TBMM özgün toplantı tutanağı.', 'accessed_at': capture['accessed_at'], 'verified_at': now, 'mime': 'application/pdf', 'sha256': sha, 'original_path': rel + '/original.pdf', 'readable_path': rel + '/readable.html'}},
    {'kind': 'source_attribution', 'values': {'version_id': version, 'publisher': 'TBMM', 'author': None, 'kind': 'official', 'published_at': None, 'date_precision': 'unknown', 'social_handle': None, 'public_url': url, 'basis': 'Kurumun özgün toplantı tutanağı. Grup görüşü, üyelerin tekil oyları ve sonuçlar ayrıdır.'}},
]
for i, section in [(19, 'DEM adına Koçyiğit konuşmasının başlangıcı'), (20, 'Koçyiğit ve Çiçek: taslak ve çekince'), (21, 'Çiçek: taslağın dili hakkında itiraz'), (22, 'Çiçek: farklı görüşün gerekçesi'), (23, 'Çiçek: ana dili hakkı ve konuşmanın sonu'), (60, 'Başkanın komisyon sonucu duyurusu')]:
    exact = pdf_page_text(path, i)
    assert exact.strip()
    entries.append({'kind': 'passage', 'values': {'id': f'{doc}-p{i}', 'version_id': version, 'exact': exact, 'prefix': None, 'suffix': None, 'article': None, 'section': section, 'pdf_page_index': i, 'printed_page': str(i + 1)}})
out = p / '2026-5367-dem-source-records.json'
out.write_text(json.dumps({'party_id': 'dem', 'entries': entries}, ensure_ascii=False, indent=2) + '\n')
print('SOURCE_RECORDS', hashlib.sha256(out.read_bytes()).hexdigest(), len(entries))
