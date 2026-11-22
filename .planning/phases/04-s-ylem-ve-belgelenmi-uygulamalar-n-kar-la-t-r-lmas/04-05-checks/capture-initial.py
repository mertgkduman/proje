import datetime, hashlib, json, sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path.cwd() / 'src'))
from arsiv import html_source_text
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/tip')
items = [
 ('parti-pm-myk-20240804', 'https://tip.org.tr/myk-ve-parti-meclisi/turkiye-isci-partisi-pm-ve-myk-toplantilari-sonuc-metni'),
 ('kongre-dokuz-eylul-20240107', 'https://dokuzeylul.com/turkiye-isci-partisi-2-buyuk-kongresini-gerceklestirdi'),
 ('tbmm-bas-20240605', 'https://www.tbmm.gov.tr/Haber/Detay?Id=311fd7c2-f439-4e0e-8dce-018fe856f92b'),
 ('tip-program', 'https://tip.org.tr/parti-programi'),
]
receipts = []
for name, url in items:
    try:
        response = requests.get(url, timeout=45, headers={'User-Agent': 'Mozilla/5.0 research archive'})
        at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        response.raise_for_status()
        raw = response.content
        digest = hashlib.sha256(raw).hexdigest()
        target = root / 'objects' / digest
        target.mkdir(parents=True, exist_ok=True)
        for path, content in [(target/'original.html.bin', raw), (target/'readable.html', raw)]:
            if path.exists() and path.read_bytes() != content:
                raise ValueError('Hash path contains different bytes')
            if not path.exists(): path.write_bytes(content)
        view = build_view(raw, response.url, root, fetch_assets=False, http_charset=response.encoding or 'utf-8')
        view['version_id'] = f'0405-{name}-v1'
        validate_view(root, view)
        txt = html_source_text(raw)
        (Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks') / f'{name}.txt').write_text(txt)
        receipts.append(dict(name=name, url=url, final_url=response.url, accessed_at=at, status=response.status_code, sha256=digest, bytes=len(raw), content_type=response.headers.get('Content-Type'), archive_view=view, text_chars=len(txt)))
    except Exception as exc:
        receipts.append(dict(name=name,url=url,attempted_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),error=str(exc)))
Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/initial-capture.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2)+'\n')
print([(r['name'],r.get('status'),r.get('bytes'),r.get('error')) for r in receipts])
