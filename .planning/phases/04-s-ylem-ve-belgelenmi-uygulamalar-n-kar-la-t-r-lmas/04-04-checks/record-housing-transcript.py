import json
from pathlib import Path

p=Path('data/practices/04-yeni-parti-tranches.json'); q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in [
 'site:cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/122 "barınma" "kabul edilmemiştir"',
 'site:tbmm.gov.tr "Ayça Taşkent" "barınma" "önerisi kabul edilmemiştir" "2026"',
 '"Ümit Özlale" "fon" "kanun teklifi" "2/" 2026',
 '"Ümit Özlale" "tasfiye" "kanun teklifi" 24 eylül 2026 esas numarası',
]]
items=[
 ('https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/122/Ham/824e2a72-561f-4031-a097-138f2f468abb.html','38d374df7534834cb6fae4b8937f225bcf055c094859881ebea38a416810be78','2026-11-21T20:46:19+00:00','7 Ağustos 122. birleşim ham tutanağında Yeni Parti grubunun barınma araştırma önergesini öne alma önerisi, görüşmeleri ve başkanın kabul edilmediği açıklaması ardışık okundu. Bu sonuç öne alma grup önerisine ilişkindir; temel araştırma önergesinin tüm sonraki işlemleri hakkında iddia değildir. Python capture bağlantı sıfırlaması sonrası curl HTTP 200 ile gerçek HTML baytları alındı; yayın tarihi bilinmiyor.'),
 ('https://tbmm.gov.tr/Haber/Detay?Id=6c53cbfc-a5ce-45fd-ae8b-01a0d32b2a5c','a2d3d10eef2796f2144795d47249d49d704052c1b56a0c1e26cff53d307bb01e','2026-11-21T20:45:09.147090+00:00','TBMM 24 Eylül haberinde Özlale fonlar hakkında hazırlanan teklif ve daha sonra araştırma önergesi planını anlatıyor; hazırlık ve sunum ayrı aşamalardır.'),
]
for url,digest,when,note in items:
 q['initial_readings'].append(dict(read_at='2026-11-21',url=url,section='TBMM metni',note=note))
 q['captures'].append(dict(url=url,sha256=digest,accessed_at=when,state='source_records_draft'))
q['candidate_leads'].append(dict(url='https://tbmm.gov.tr/milletvekili/UyeKomisyonKonusmaTutanakDetay?tutanakId=90375',state='read_capture_failed',note='Komisyon konuşması 28 Eylül Özlale teklifinin sunulduğunu belirtiyor; capture bağlantı sıfırlandı. Bağımsız dizinde 2/3895; resmi teklif kaydı ve 2/3939 farklı teklifin ayrı sonucu takip edilmeli.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
