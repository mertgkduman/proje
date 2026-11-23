import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import readable_bytes
from arsiv_gorunum import build_view, validate_view

path = Path('/tmp/gsd-tip-iklim-104.html')
url = 'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/104/Tam/1252814c-e8f1-40c6-ae66-f1d33b9950b8.html'
raw = path.read_bytes()
digest = hashlib.sha256(raw).hexdigest()
assert digest == '84c36043d410905c0227bc2ed17339ecd2fbc94fe0a58c6d0f40ea5afe57a679'
root = Path('data/practices/sources/tip')
obj = root / 'objects' / digest
obj.mkdir(parents=True, exist_ok=True)
for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=True))]:
    dest = obj / name
    if dest.exists():
        assert dest.read_bytes() == content
    else:
        dest.write_bytes(content)
view = build_view(raw, url, root, fetch_assets=False, http_charset='windows-1254')
view['version_id'] = '0405-tip-iklim-104-tutanak-v1'
validate_view(root, view)
receipt = {'url': url, 'sha256': digest, 'bytes': len(raw), 'accessed_at': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(), 'view': view, 'limitations': 'Erişim zamanı indirilen dosyanın son yazım zamanıdır; belge henüz tam okunmadı ve paket kapılarına alınmadı.'}
here = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
(here / 'iklim-2927-104-capture.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(digest, view['view_id'])
