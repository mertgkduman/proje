import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "Bursa" 18 Ekim 2026 "ön seçim" il başkanı sonuç','"Yeni Parti" "Diyarbakır" 18 Ekim 2026 "ön seçim" il başkanı sonuç','"Yeni Parti" "Sakarya" 18 Ekim 2026 "ön seçim" il başkanı sonuç','"Yeni Parti" "İzmir" 18 Ekim 2026 ön seçim il kongresi']]
items=[
 ('https://www.baskagazete.com/haber/yeni-parti-bursa-da-il-baskanligini-nihat-yesiltas-kazandi-255672.html','e8c6f9187223bb189cc9182e9028239b55ee24adedcf3c19902bb203a89ee7bb','2026-11-21T21:07:15.725972+00:00','Kardelen Cancı, 18 Ekim Bursa ön seçiminin 17 ilçede yapıldığını bildiriyor. Güncellenen haber ve arama önbelleği farklı zamanlardaki sayıları gösterebilir; yakalanan baytın güncellemesi ve sandık kayıtları ayrıca izlenir, rakamlar birleştirilmez.'),
 ('https://www.haberlisin.com/partililer-degisim-dedi-on-secimde-zafer-selda-sezginin','3b13857212fa9f8f3c59b599bb489bd89d9b48d9023a99d45c3b885711dc9625','2026-11-21T21:07:16.541629+00:00','Nazile Akarsu, 18 Ekim 19:59/20:13: Sakarya 16 ilçeli ön seçim, iki adayın 3.886 ve 3.359 oyu ile toplam 7.245 aday oyu; sonraki il kongresi ayrı. Toplamı kullanılan veya geçerli tüm oy sayısına otomatik eşitleme yok.'),
 ('https://www.halk54.com/engin-ozkoctan-sakaryadaki-il-baskanligi-secimine-iliskin-aciklama','6f86aeff11a1031b6b62180caab448d87a5ed3fd2015cc5eb823f49be420b1db','2026-11-21T21:07:17.483854+00:00','Halk54 18 Ekim 20:23/20:40: kesin olmayan sonuçta 7.266 kişinin oy kullandığını ve iki aday için 3.886/3.359 oyu bildiriyor. İki aday toplamı 7.245 ile bildirilen katılımın 21 farkı gerekçesiz uzlaştırılmadı; sandık tutanakları görülmedi.'),
]
for url,digest,when,note in items:
 q['initial_readings'].append(dict(read_at='2026-11-21',url=url,section='18 Ekim il ön seçimi haberi',note=note));q['captures'].append(dict(url=url,sha256=digest,accessed_at=when,state='source_records_draft'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
