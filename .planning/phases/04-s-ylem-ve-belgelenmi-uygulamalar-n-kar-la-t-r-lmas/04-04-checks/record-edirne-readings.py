import json
from pathlib import Path

p = Path('data/practices/04-yeni-parti-tranches.json')
q = json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21', query=s) for s in [
 '"Mehmet Ergüleç" "disiplin" "Yeni Parti" 2026 karar',
 '"Mehmet Ergüleç" "ihraç" "Yeni Parti" ekim kasım 2026',
 '"Yeni Parti" "Edirne" "üyelik" "itiraz" 27 ağustos 2026',
]]
items = [
 ('https://www.edirneahval.com/siyaset/edirnede-yeni-parti-uyelikleri-askida-kongre-ne-zaman-yapilacak/104247','a41a476cee53a9f3528d5e8494d2d26dda6268a9288e8ecdea2b88836446ba81','2026-11-21T20:40:24.807472+00:00','Adem Batuhan Sever, 27 Ağustos: Edirne merkez ilçe başkanına atfen 1.799 üye, 1 Eylül askı, 5 Eylül itiraz süresi. Önceki /public/index.php/ adresi 404 idi; gerçek adres bulundu ve yakalandı. Bir itiraz kararı gösterilmiyor.'),
 ('https://www.batiekspres.com/edirne/yeni-parti-edirne-de-uye-listeleri-askida-bin-799-uye-var-203693','0078f775cf4fc3d50955ce0140090ff5e43ac5ab645db1c28d2c85173dcb9e1e','2026-11-21T20:40:26.087374+00:00','Uğur Akagündüz, 27 Ağustos: aynı ilçe başkanına atfedilen 1.799 ve 1 Eylül askı bitişi. Aynı açıklamaya dayanması bağımsız üye kaydı olduğu anlamına gelmez.'),
]
for url, digest, when, note in items:
 q['initial_readings'].append(dict(read_at='2026-11-21', url=url, section='Haber gövdesi ve ilçe başkanının açıklaması', note=note))
 q['captures'].append(dict(url=url, sha256=digest, accessed_at=when, state='source_records_draft'))
q['candidate_leads'].append(dict(url='https://www.gazianteppusula.com/haber/29017471/yeni-parti-gaziantepte-disiplin-depremi', state='read_search_index_capture_blocked', note='20 Ekim 13:28 metni arama indeksinde okundu; Ermayası açıklamasına dayanarak sevk ve kurul kararı beklentisi bildiriliyor. Aynı açıklama bağımsız nihai karar kanıtı değildir; doğrudan capture önceki girişimde 403.'))
p.write_text(json.dumps(q, ensure_ascii=False, indent=2)+'\n')
