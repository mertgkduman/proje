import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json')
q=json.loads(p.read_text())
q['candidate_leads'].append(dict(url='https://www.sozcu.com.tr/yeni-parti-istanbul-on-seciminde-kazanan-belli-oldu-p370398',state='source_records_draft',note='18 Ekim Sözcü/ANKA haberinde İstanbul il başkanlığı ön seçimini tek aday Özgür Çelik’in resmî olmayan sonuca göre kazandığı bildiriliyor. Pasaj 0404-istanbul-onsecim-sozcu-p, özgün bayt SHA256 c3710e8f0388a2a8927423891387d6bcde8a53dc1a806f3459c872eca2a0cd1c; sonraki kongreyle özdeşlenmez. Diğer ANKA yayınları ayrı bağımsız ajans sayılmaz.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
