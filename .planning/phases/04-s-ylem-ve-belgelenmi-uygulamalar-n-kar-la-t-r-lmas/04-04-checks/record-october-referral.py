import json
from pathlib import Path

p = Path('data/practices/04-yeni-parti-tranches.json')
q = json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21', query=s) for s in [
    '"Yeni Parti" disiplin ihraç Gaziantep 2026',
    '"Yeni Parti" 2026 il kongresi itiraz seçim',
    '"Yeni Parti" 2026 parti meclisi toplantısı kararları',
]]
q['initial_readings'] += [
    dict(read_at='2026-11-21', url='https://www.referansgazetesi.com.tr/yeni-parti-gaziantepte-flas-karar-eski-belediye-baskanina-ihrac-soku', section='20 Ekim haber gövdesi', note='Ayhan Duman, 20 Ekim 10:53, 11:14 güncelleme: Oğuzeli ilçe başkanının açıklamasına dayanarak Mehmet Ergüleç için kesin ihraç talebiyle disipline sevki aktarıyor. Metin kurul kararının beklendiğini söylüyor; başlıktaki ihraç ifadesi kesinleşmiş karar kanıtı değildir. Bu kişi Seydi Ahmet Keleş dosyasından ayrıdır. Ham yakalama ve kurul sonucu izlenecek.'),
    dict(read_at='2026-11-21', url='https://gazeteoksijen.com/turkiye/yeni-parti-kongre-takvimini-acikladi-286490', section='19 Ağustos takvim duyurusu', note='Parti sözcüsünün açıklamasında 26 Ağustos askı ve itiraz başlangıcı, 12 Eylül ilçe ve 18 Ekim il seçimi başlangıcı, 27 Ekim il kongreleri son tarihi aktarılıyor. Bu planlanan takvim tek tek gerçekleşen kongre sonuçlarıyla özdeş değildir.'),
]
q['candidate_leads'].append(dict(url='https://www.edirneahval.com/public/index.php/siyaset/edirnede-yeni-parti-uyelikleri-askida-kongre-ne-zaman-yapilacak/104247', state='open_failed', note='Arama sonucu 27 Ağustos Edirne askı ve itiraz takvimini gösterdi; 21 Kasım tam sayfa açma HTTP 404 verdi. Metin ve alternatif kaynak araştırılacak; yokluk sonucu değildir.'))
p.write_text(json.dumps(q, ensure_ascii=False, indent=2) + '\n')
