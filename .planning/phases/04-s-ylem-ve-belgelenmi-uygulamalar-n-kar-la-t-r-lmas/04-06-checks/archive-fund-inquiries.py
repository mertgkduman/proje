"""İki TBMM önergesi için yerel okunabilir ve pasif kaynak varlıkları."""
import json
import hashlib
from pathlib import Path
from arsiv import readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
root = Path('data/practices/sources/dem')
capture = json.loads((checks / '2026-fon-4830-4918-capture.json').read_text())
for item in capture['records']:
    original = Path(item['path'])
    raw = original.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['sha256']
    kind = 'pdf' if item['id'].endswith('pdf') else 'html'
    readable = original.parent / 'readable.html'
    content = readable_bytes(raw, kind, legacy=False)
    if readable.exists():
        assert readable.read_bytes() == content
    else:
        readable.write_bytes(content)
    item['readable_path'] = str(readable.relative_to(root))
    if kind == 'html':
        view = build_view(raw, item['url'], root, fetch_assets=False)
        view['version_id'] = '0406-fund-'+item['id']+'-v1'
        validate_view(root, view)
        item['view'] = view
        print(item['id'], 'VIEW', view['view_id'])
    else:
        print(item['id'], 'PDF')
(checks / '2026-fon-4830-4918-views.json').write_text(json.dumps(capture, ensure_ascii=False, indent=2)+'\n')
