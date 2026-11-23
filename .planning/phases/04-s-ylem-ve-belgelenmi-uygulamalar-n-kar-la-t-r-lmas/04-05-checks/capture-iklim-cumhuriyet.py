import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import readable_bytes
from arsiv_gorunum import build_view, validate_view

path = Path('/tmp/gsd-tip-iklim-cumhuriyet.html')
url = 'https://www.cumhuriyet.com.tr/turkiye/muhalefet-karbon-piyasasi-diye-elestirmisti-iklim-kanunu-teklifi-nin-birinci-bolumu-tbmm-genel-kurulu-nda-kabul-edildi-2413005'
raw = path.read_bytes()
digest = hashlib.sha256(raw).hexdigest()
assert digest == 'aafa748fe4ffd56bffbc3c30310c3fa6f8a633187e8cbd97cb3f71d50a1b8399'
root = Path('data/practices/sources/tip')
obj = root / 'objects' / digest
obj.mkdir(parents=True, exist_ok=True)
for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=True))]:
    dest = obj / name
    if dest.exists():
        assert dest.read_bytes() == content
    else:
        dest.write_bytes(content)
view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
view['version_id'] = '0405-tip-iklim-cumhuriyet-v1'
validate_view(root, view)
receipt = {'url': url, 'sha256': digest, 'bytes': len(raw), 'accessed_at': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(), 'view': view, 'limitations': 'Erişim zamanı indirilen dosyanın son yazım zamanıdır; belge henüz tam okunmadı ve paket kapılarına alınmadı.'}
here = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
(here / 'iklim-2927-cumhuriyet-capture.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(digest, view['view_id'])
