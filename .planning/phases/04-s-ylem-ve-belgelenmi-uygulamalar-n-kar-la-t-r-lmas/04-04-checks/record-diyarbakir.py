import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "Diyarbakır" "18 Ekim" "il başkanlığı" ön seçimi 2026','"Yeni Parti" Diyarbakır il başkanlığı ön seçim kazandı 2026 18 ekim','"Yeni Parti" "Diyarbakır" "ön seçim" "2026" il başkanı seçildi','"Yeni Parti" "Diyarbakır" "25 Ekim" il kongresi 2026']]
items=[
 ('https://www.toplumsal.com.tr/haber/yeni-parti-diyarbakir-il-baskanligi-on-seciminde-mehmet-berk-one-cikti_30208/','dab98f5ca87d7c3583dcd2ae30df1fb3206eff24ef7373707c4c737c0bcbe27d','2026-11-21T21:19:30.277536+00:00','Toplumsal / ANKA 18 Ekim 18:28: 17 ilçedeki il başkanlığı ön seçiminin tamamlandığı ve Mehmet Berkin en fazla oy aldığı aktarılıyor; sonraki kongre ve özgün sandık kayıtları ayrı incelenmeli.'),
 ('https://www.habererk.com/haber/yeni-parti-diyarbakir-da-on-secimle-il-baskanini-belirliyor_356595/','a231f4a3a6bb80a7ad0eeb3bde1d7c740da82ae2a3d9ca4f03f884215ad0997b','2026-11-21T21:19:30.608213+00:00','Habererk / ANKA 18 Ekim 14:22: ön seçimin işleyişi ve Sezgin Tanrıkulunun beyanı aktarılıyor; haber sonuç açıklamasından önce. Her iki yayın aynı ajansa atıf yapar, birbirinden bağımsız iki haber kaynağı sayılmadı.'),
]
for url,digest,when,note in items:
 q['initial_readings'].append(dict(read_at='2026-11-21',url=url,section='Diyarbakır ön seçim haber gövdesi',note=note));q['captures'].append(dict(url=url,sha256=digest,accessed_at=when,state='source_records_draft'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
