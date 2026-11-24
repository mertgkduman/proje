import datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/dem');checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/50/Tam/c825637d-a430-46a1-8932-e7ec983cfffa.html'
raw=Path('/tmp/gsd-dem-koca-jan29.html').read_bytes();text=html_source_text(raw)
assert '29 Ocak 2025 Çarşamba' in text and 'Halkların Eşitlik ve Demokrasi Partisi Grubu adına Mersin Milletvekili Sayın Perihan Koca.' in text
sha=hashlib.sha256(raw).hexdigest();folder=root/'objects'/sha;folder.mkdir(parents=True,exist_ok=True)
for name,body in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=folder/name
 if p.exists():assert p.read_bytes()==body
 else:p.write_bytes(body)
view=build_view(raw,url,root,fetch_assets=False);view['version_id']='0406-iklim-koca-jan29-v1';validate_view(root,view)
out=dict(url=url,document_date='2025-01-29',accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=sha,original_path=f'objects/{sha}/original.html.bin',readable_path=f'objects/{sha}/readable.html',view=view)
(checks/'iklim-koca-jan29-capture.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
