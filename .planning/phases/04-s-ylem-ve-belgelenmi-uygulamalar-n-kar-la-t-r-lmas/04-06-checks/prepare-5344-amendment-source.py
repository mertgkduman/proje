"""DEM'in emeklilikte yeni madde önerisi ve komisyon kararını çıkar."""
import hashlib,json
from pathlib import Path
from arsiv import pdf_page_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
rows=json.loads((p/'2026-5344-direct-source-records.json').read_text())['entries']; entries=[e for e in rows if e['kind'] in ('document','document_version','source_attribution')]
v=next(e['values'] for e in entries if e['kind']=='document_version');f=Path('data/practices/sources/dem')/v['original_path'];assert hashlib.sha256(f.read_bytes()).hexdigest()==v['sha256']
t=pdf_page_text(f,69);a=t.index('Görüşülmekte olan (2/3464) esas numaralı');b=t.index('Önerge kabul\nedilmemiştir.',a)+len('Önerge kabul\nedilmemiştir.');exact=t[a:b]
entries.append(dict(kind='passage',values=dict(id='0406-7573-commission-pension-amendment',version_id=v['id'],exact=exact,prefix=None,suffix=None,article=None,section='DEM milletvekilleri imzalı yeni madde önerisi ve komisyon reddi',pdf_page_index=69,printed_page='70')))
out=p/'2026-5344-amendment-source-records.json';out.write_text(json.dumps(dict(party_id='dem',entries=entries),ensure_ascii=False,indent=2)+'\n');print(hashlib.sha256(out.read_bytes()).hexdigest())
