import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "Çağatay Güç" "25 Ekim 2026" il kongresi İzmir seçildi','"Yeni Parti" "İzmir" "il kongresi" "25 Ekim" "Güç" 2026','"Yeni Parti" "Aziz Kocaoğlu" "ön seçim" "itiraz" 18 Ekim 2026','"Yeni Parti" "Diyarbakır" "18 Ekim" "ön seçim" 2026 il başkanlığı']]
items=[
 ('https://www.sozcu.com.tr/yeni-parti-izmir-il-baskanligi-on-secimi-18-ekim-2026-p370418','e7a390db201b9671d08c2da46bbf22e7b30f1d146fb6a739d87e360d31f049b5','2026-11-21T21:15:31.680934+00:00','Sözcü, 18 Ekim 22:08/22:29: İzmir il başkanlığı ön seçiminde kesin olmayan sonuç; kongre için 25 Ekim planı ayrı. Ön seçim sonucu kongre oylaması değildir.'),
 ('https://www.habertire.com/ersin-gungor-kurultay-delegesi-secildi','c04c56b14530f9c983bb8218035af7bc3bb75fcc3f355335cb817ffabcad64fe','2026-11-21T21:15:32.257051+00:00','Ercan Çelik, 26 Ekim: 25 Ekim kongresinde Güçün 408 oyla il başkanı, Tire ilçe başkanının kurultay delegesi seçildiğini bildiriyor. Kongre ve üyelerin bir hafta önceki ön seçimi ayrı.'),
 ('https://www.habererk.com/haber/yeni-parti-izmir-il-kongresi-nde-cagatay-guc-yeniden-secildi_357889/','074dec9ba1ec7ec38367a2177d8d8c7848458a177f6d600e0e583cf41ab81187','2026-11-21T21:15:33.002828+00:00','Habererk / ANKA 25 Ekim 20:41 divan başkan yardımcısına 465 oy kullanan delege ve 408 geçerli oyu atfediyor. Özgün kongre tutanağı görülmedi; kaynak atfı korunuyor.'),
]
for url,digest,when,note in items:
 q['initial_readings'].append(dict(read_at='2026-11-21',url=url,section='İzmir ön seçim veya sonraki kongre haberi',note=note));q['captures'].append(dict(url=url,sha256=digest,accessed_at=when,state='source_records_draft'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
