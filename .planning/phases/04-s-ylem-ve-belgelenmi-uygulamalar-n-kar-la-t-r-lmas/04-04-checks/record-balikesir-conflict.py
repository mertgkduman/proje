import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json'); q=json.loads(p.read_text())
q['initial_readings'].append(dict(read_at='2026-11-21',url='https://gazetemerhaba.com/siyaset/balikesir-yeni-parti-il-baskanligi-on-seciminde-sonuclar-belli-oldu-124633',section='Ön seçim sonucu, haber metni ve sonuç tablosu',note='Aynı özgün haber gövdesinde Ozan Can Ak için düzyazıda 4.696, tabloda 4.697 yazılıdır; toplam 10.975 ve 1.583 fark da ayrıca verilir. Bunlar otomatik düzeltilmedi veya tek doğru sayı seçilmedi. 19 Ekim ilçe listesi il başkanına atfediliyor; sandık tutanakları görülmedi.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
