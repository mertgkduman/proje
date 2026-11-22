import datetime, hashlib, json, subprocess
from pathlib import Path
import requests

root = Path('data/practices/sources/tip')
out = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
urls = {
 'tbmm-2-4390': 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y5/T2/WebOnergeMetni/9c60b46f-6665-479a-aa0f-9025c059f4e9.pdf',
 'tbmm-2-2121': 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y2/T2/WebOnergeMetni/8774d96e-ebce-4f0b-8ecf-6172f44e5c40.pdf',
}
results = []
for name, url in urls.items():
    try:
        r = requests.get(url, timeout=45, headers={'User-Agent':'Mozilla/5.0 research archive'})
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        r.raise_for_status()
        if not r.content.startswith(b'%PDF-'): raise ValueError('Response is not PDF')
        digest = hashlib.sha256(r.content).hexdigest()
        dest = root / 'objects' / digest
        dest.mkdir(parents=True, exist_ok=True)
        file = dest / 'original.pdf'
        if file.exists() and file.read_bytes() != r.content: raise ValueError('Hash collision or altered object')
        if not file.exists(): file.write_bytes(r.content)
        receipt = dict(name=name,url=url,final_url=r.url,status=r.status_code,accessed_at=timestamp,sha256=digest,bytes=len(r.content))
        try:
            text = out / (name + '.txt')
            subprocess.run(['pdftotext','-layout',str(file),str(text)],check=True,timeout=30)
            receipt['text_chars'] = len(text.read_text())
        except (OSError, subprocess.SubprocessError) as exc:
            receipt['extraction_error'] = str(exc)
        results.append(receipt)
    except Exception as exc:
        results.append(dict(name=name,url=url,attempted_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),error=str(exc)))
(out/'policy-capture.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(results)
