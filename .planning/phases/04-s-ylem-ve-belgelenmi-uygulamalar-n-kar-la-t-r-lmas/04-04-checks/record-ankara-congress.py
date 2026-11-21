import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "İstanbul" "ön seçim" 18 ekim 2026 il başkanı kongresi','"Yeni Parti" "Ankara" "ön seçim" 18 ekim 2026 il başkanı 25 kongre','"Yeni Parti" "Afyonkarahisar" 18 ekim 2026 ön seçim kongre itiraz','"Yeni Parti" "Aydın" 18 ekim 2026 ön seçim 25 ekim kongre','"Dilaver Demir" "26 Ekim 2026" "kongre" seçildi Yeni Parti','"İbrahim Karaca" "25 Ekim 2026" il kongresi Yeni Parti']]
items=[
 ('https://www.vtv.net.tr/haber/yeni-parti-ankara-il-orgutunde-ibrahim-karaca-donemi-il-baskani-ve-yonetim-kurulu-belirlendi','96601cffe14d2bcd0bd7c9c74b2c50d305701e302db3239df07a0bc8b1fe12e1','2026-11-21T21:26:18.726048+00:00','Atasavun Yiğit / VTV 25 Ekim 16:44: Ankara il kongresinde 372 oy kullanan delege ve Karaca için 357 oy bildiriliyor; blok listeye tepki ayrı bir haber iddiası. Saat ve rakam diğer haberden farklı; tutanak görülmedi.'),
 ('https://baskenthaber.org/yeni-parti-ankara-il-baskani-av-ibrahim-karaca-oldu/','fe01ac50d584465b62d71157fc07c26cdd1a68300906199e4c5b0f81d8981422','2026-11-21T21:26:21.606201+00:00','Başkent Haber 25 Ekim 18:42/18:52: 405 imza, 349 oy kullanan ve 349 geçerli oyun tümü Karacaya atfediliyor; sandığın 17:00de kapandığı aktarılıyor. VTVnin 357/372 rakamları ve erken yayın saati ile farklılık açıklanmadan korunur.'),
 ('https://www.yeniankara.com.tr/yeni-parti/yeni-parti-ankarada-yeni-donem-ilk-olagan-il-kongresi-duzenlendi-187535','158da3e85da346e5274c4b14efd7566408a0952f2a047fbf9549cca6395760ea','2026-11-21T21:26:22.038944+00:00','Yeni Ankara 25 Ekim 11:54/13:38: 18 Ekim ön seçimi ve ardından il kongresini anlatıyor. Erken yayınlanan haberin süreç anlatımı son oylama tutanağı yerine geçirilmez.'),
]
for url,digest,when,note in items:
 q['initial_readings'].append(dict(read_at='2026-11-21',url=url,section='Ankara il kongresi haberi',note=note));q['captures'].append(dict(url=url,sha256=digest,accessed_at=when,state='source_records_draft'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
