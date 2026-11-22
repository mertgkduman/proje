import datetime, hashlib, json, subprocess
from pathlib import Path

url = 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y5/T2/WebOnergeMetni/a0435151-e9fd-4e39-aa5c-1a5be7b5c03a.pdf'
raw = subprocess.run(['curl', '-fsSL', '--connect-timeout', '10', '--max-time', '60', '--retry', '1', '--retry-delay', '1', url], check=True, stdout=subprocess.PIPE).stdout
at = datetime.datetime.now(datetime.timezone.utc).isoformat()
assert raw.startswith(b'%PDF-')
digest = hashlib.sha256(raw).hexdigest()
dest = Path('data/practices/sources/tip/objects') / digest / 'original.pdf'
dest.parent.mkdir(parents=True, exist_ok=True)
if dest.exists():
    assert dest.read_bytes() == raw
else:
    dest.write_bytes(raw)
out = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/barinma-capture.json')
out.write_text(json.dumps(dict(url=url, accessed_at=at, sha256=digest, bytes=len(raw)), ensure_ascii=False, indent=2) + '\n')
print('OK', digest, at, len(raw))
