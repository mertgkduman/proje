import datetime, hashlib, json, subprocess
from pathlib import Path

url = 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y4/T10/DosyaKomisyonRaporunuVerdi/502ba724-5f63-48a3-935e-3caca0c33b83.pdf'
raw = subprocess.run(['curl', '--http1.1', '-fsSL', '--connect-timeout', '10', '--max-time', '180', '--retry', '1', '--retry-delay', '1', url], check=True, stdout=subprocess.PIPE).stdout
at = datetime.datetime.now(datetime.timezone.utc).isoformat()
assert raw.startswith(b'%PDF-')
digest = hashlib.sha256(raw).hexdigest()
dest = Path('data/practices/sources/tip/objects') / digest / 'original.pdf'
dest.parent.mkdir(parents=True, exist_ok=True)
if dest.exists():
    assert dest.read_bytes() == raw
else:
    dest.write_bytes(raw)
out = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/deprem-rapor-capture.json')
out.write_text(json.dumps(dict(url=url, accessed_at=at, sha256=digest, bytes=len(raw)), ensure_ascii=False, indent=2) + '\n')
print('OK', digest, at, len(raw))
