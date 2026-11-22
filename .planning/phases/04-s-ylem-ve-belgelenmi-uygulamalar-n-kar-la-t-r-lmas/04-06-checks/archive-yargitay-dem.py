"""295 raporunu ve kesin isimli oylama cetvelini özgün baytlarla sakla."""
import datetime, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/dem')
checks = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
items = [("dem-tarihsiz", "/tmp/gsd-dem-yargitay-2024.pdf", "https://www.yargitaycb.gov.tr/documents/ek-1704887475.pdf", "pdf")]
records = []
for name, local, url, kind in items:
    raw = Path(local).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    folder = root/'objects'/sha
    folder.mkdir(parents=True, exist_ok=True)
    original = 'original.pdf' if kind == 'pdf' else 'original.html.bin'
    # The legacy audit-compatible derivative uses replacement decoding; the
    # passive view below preserves the HTTP charset and displays Turkish text.
    readable = readable_bytes(raw, kind, legacy=(kind == 'html'))
    for filename, data in [(original, raw), ('readable.html', readable)]:
        path = folder/filename
        if path.exists(): assert path.read_bytes() == data
        else: path.write_bytes(data)
    record = dict(id=name, original_url=url, final_url=url, publisher='Yargıtay Cumhuriyet Başsavcılığı', accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), sha256=sha, original_path='objects/'+sha+'/'+original, readable_path='objects/'+sha+'/readable.html')
    if kind == 'html':
        view = build_view(raw, url, root, fetch_assets=False, http_charset='windows-1254')
        view['version_id'] = '0406-2026-3961-vote-v1'
        validate_view(root, view)
        record['view'] = view
    records.append(record)
    print(name, sha, len(raw), flush=True)
(checks/'yargitay-dem-liste.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
