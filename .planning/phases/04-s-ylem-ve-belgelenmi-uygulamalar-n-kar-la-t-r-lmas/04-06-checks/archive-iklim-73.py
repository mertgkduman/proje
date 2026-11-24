import datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/dem');checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/73/Tam/fa17fb98-1132-42b3-a186-5c92c667847d.html'
raw=Path('/tmp/gsd-dem-iklim-73.html').read_bytes();text=html_source_text(raw)
assert '8 Nisan 2025 Salı' in text and 'İklim Kanunu Teklifi (2/2927)' in text
assert "Halkların Eşitlik ve Demokrasi Partisi Grubu adına İzmir Milletvekili İbrahim Akın'a ait." in text
assert "Halkların Eşitlik ve Demokrasi Partisi Grubu adına diğer söz talebi Mersin Milletvekili Perihan Koca'ya ait." in text
sha=hashlib.sha256(raw).hexdigest();folder=root/'objects'/sha;folder.mkdir(parents=True,exist_ok=True)
for name,body in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=folder/name
 if p.exists():assert p.read_bytes()==body
 else:p.write_bytes(body)
view=build_view(raw,url,root,fetch_assets=False);view['version_id']='0406-iklim-73-floor-v1';validate_view(root,view)
out=dict(url=url,document_date='2025-04-08',accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=sha,original_path=f'objects/{sha}/original.html.bin',readable_path=f'objects/{sha}/readable.html',view=view)
(checks/'iklim-73-source-capture.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
