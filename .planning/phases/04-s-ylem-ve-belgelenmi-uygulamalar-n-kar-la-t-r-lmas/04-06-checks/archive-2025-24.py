"""TBMM 24. birleşiminin özgün bayt ve pasif görünümünü arşivle."""
import datetime, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/dem')
checks = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
url = 'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/24/Tam/2842bd28-bf72-4455-bc86-4efae804ab3f.html'
raw = Path('/tmp/gsd-dem-2025-24.html').read_bytes()
sha = hashlib.sha256(raw).hexdigest()
folder = root / 'objects' / sha
folder.mkdir(parents=True, exist_ok=True)
for name, body in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
    path = folder / name
    if path.exists(): assert path.read_bytes() == body
    else: path.write_bytes(body)
view = build_view(raw, url, root, fetch_assets=False)
view['version_id'] = '0406-tbmm-2025-24-v1'
validate_view(root, view)
record = dict(original_url=url, final_url=url, document_date='2025-12-03', publisher='TBMM', accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), sha256=sha, original_path='objects/'+sha+'/original.html.bin', readable_path='objects/'+sha+'/readable.html', view=view)
(checks/'tbmm-2025-24-capture.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
print(sha, len(raw), view['view_id'])
