import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json'); q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "Balıkesir" "ön seçim" 18 Ekim 2026 il başkanı sonuç','"Yeni Parti" "Balıkesir" "il kongresi" 25 Ekim 2026 başkan','"Yeni Parti" "Balıkesir" "önseçim" 2026 "oy" itiraz','"Erden Köybaşı" "25 Ekim 2026" "kongresi" seçildi','"Yeni Parti" "Balıkesir" "25 Ekim" "Köybaşı" kongre 2026']]
items=[
 ('https://gazetemerhaba.com/siyaset/balikesir-yeni-parti-il-baskanligi-on-seciminde-sonuclar-belli-oldu-124633','603f01c670e7672f9df2e90be1bf4bea7f0512d7f7cbad910e690de4b872ac2e','2026-11-21T20:56:15.528584+00:00','Semra Aman Akyürek, 18 Ekim 18:47/19:25: üyelerin katıldığı ön seçimi, Köybaşı ve Ak adaylığını ve 25 Ekimde yapılacak kongreyi ayrı aktarıyor. Oy sayılarına ilişkin kaynaklar arasındaki fark çözülmedi.'),
 ('https://gazetemerhaba.com/siyaset/yeni-parti-balikesir-on-seciminde-erden-koybasi-ve-ozan-can-akin-20-ilcedeki-oylari-belli-oldu-124679','d0532530f59db369418dbc5c6e5ce935338eb0e65acdd937be466bbecaec41d5','2026-11-21T20:56:15.887662+00:00','Macit Ermiş, 19 Ekim: il başkanının açıkladığı 20 ilçe oy listesini aktarıyor. Haber parti açıklamasını kaydeder; özgün sandık tutanağı değildir, sayısal farkın tek başına çözümü sayılmadı.'),
]
for url,digest,when,note in items:
 q['initial_readings'].append(dict(read_at='2026-11-21',url=url,section='Ön seçim haber gövdesi',note=note));q['captures'].append(dict(url=url,sha256=digest,accessed_at=when,state='source_records_draft'))
q['candidate_leads'] += [dict(url='https://www.balikesir24saat.com/yeni-partide-yeni-donem.html',state='read_search_index_capture_blocked',note='Arama indeksi 25 Ekim kongresi ve Köybaşı seçimini bildiriyor; doğrudan sayfa 403 verdi. Kongre ve ön seçim ayrı, gerçek kongre kaynağı izlenecek.'),dict(url='https://www.onturk.tv/erden-koybasi-yeni-parti039nin-balikesir-il-baskani-secildi/80633/',state='read_search_index_capture_blocked',note='25 Ekim 14:07 kongre haberini arama indeksi gösterdi; capture 403. Tam erişim izlenecek.')]
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
