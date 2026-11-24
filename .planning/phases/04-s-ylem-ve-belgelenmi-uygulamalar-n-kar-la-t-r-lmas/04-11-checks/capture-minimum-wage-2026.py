from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

here=Path(__file__).resolve().parent
root=Path('data/practices/sources/saadet')
now=datetime.now(timezone.utc).isoformat()
raw=Path('/tmp/saadet-wage-press.html').read_bytes()
digest=sha256(raw).hexdigest()
url='https://www.kayserihaber.com/mahmut-arikan-asgari-ucret-en-az-33-bin-tl-olmali'
original=f'objects/{digest}/original.html.bin'
readable=f'objects/{digest}/readable.html'
paths=set()
def put(path,contents):
 p=root/path; p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists(): assert p.read_bytes()==contents
 else: p.write_bytes(contents)
 paths.add(str(p))
put(original,raw); put(readable,readable_bytes(raw,'html',legacy=False))
view=build_view(raw,url,root,fetch_assets=False); view['version_id']='0411-wage-2026-press-v1'; validate_view(root,view)
manifest=root/view['manifest_path']; paths.add(str(manifest)); paths.update(str(manifest.parent/n) for n in json.loads(manifest.read_bytes())['files'])
quote='En az yüzde 50 zamla 33 bin lira olmalıdır. Bunun altı kabul edilemez.'
assert quote in html_source_text(raw)
entries=[
 {'kind':'document','values':dict(id='0411-wage-2026-press',party_id='saadet',title='Arıkanın 2026 asgari ücret talebi',source_kind='news')},
 {'kind':'document_version','values':dict(id='0411-wage-2026-press-v1',document_id='0411-wage-2026-press',original_url=url,final_url=url,document_date='2025-10-23',date_precision='day',date_unknown_reason=None,version_label='Kayseri Haber yayını; parti API konuşması ayrıca okundu.',accessed_at=now,verified_at=now,mime='text/html',sha256=digest,original_path=original,readable_path=readable)},
 {'kind':'source_attribution','values':dict(version_id='0411-wage-2026-press-v1',publisher='Kayseri Haber',author='Nadire Nur Temur',kind='journalism',published_at='2025-10-23',date_precision='day',social_handle=None,public_url=url,basis='Yayıncı ve imza haberin özgün sayfasından.')},
 {'kind':'archive_view','values':view},
 {'kind':'passage','values':dict(id='0411-wage-2026-demand',version_id='0411-wage-2026-press-v1',exact=quote,prefix=None,suffix=None,article=None,section='Arıkanın asgari ücret talebi',pdf_page_index=None,printed_page=None)},
 {'kind':'passage','values':dict(id='0411-wage-2026-official-net-brut',version_id='0411-july-pension-wage-announcement-v1',exact='net asgari ücret 28 bin 75 lira 50 kuruş, brüt asgari ücret tutarı ise 33 bin 30 lira olarak belirlenmiştir.',prefix=None,suffix=None,article=None,section='2026 için net ve brüt ücret duyurusu',pdf_page_index=None,printed_page=None)},
]
(here/'minimum-wage-2026-source-records.json').write_text(json.dumps(dict(party_id='saadet',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0411-wage2026-paths').write_text('\n'.join(sorted(paths))+'\n')
print('source entries',len(entries),'paths',len(paths))
