import json
from pathlib import Path

p = Path('data/practices/04-yeni-parti-tranches.json')
q = json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21', query=s) for s in [
    '"Yeni Parti" "Aydın" "26 Ekim 2026" "Demir" kongre seçildi',
    '"Dilaver Demir" "26 Ekim" "2026" kongre Yeni Parti Aydın',
    '"Yeni Parti" "2026" "10/4638" deprem Barut önergesi',
]]
q['candidate_leads'] += [
    dict(url='https://www.bultenaydin.com/haber/yeni-parti-il-yonetimi-belli-oldu-omer-gunel-kurultay-delegesi-secildi', state='source_records_draft', note='26 Ekim 16.33 tarihli Bülten Aydın haberi Dilaver Demir’in il kongresinde seçildiğini bildiriyor. 18 Ekim üyelerin ön seçimiyle ayrı olaydır. Aynı gün 14.36 Günaydın haberi sandıkların 17.00’de kapanmasının beklendiğini bildirir; erken sonuç haberinin zamanlaması ve gerekçesi doğrulanmamıştır. Özgün pasaj 0404-aydin-kongre-bulten-p.'),
    dict(url='https://gunaydinaydin.com/yeni-parti-aydin-kongresi-basladi', state='read_unbound', note='26 Ekim 14.36 haberinde kongrede oy vermenin başladığı ve sandıkların 17.00’de kapanmasının beklendiği yazıyor; sonuç ilanı değil. Tam bayta bağlama ve fiilî kapanış zamanı araştırılmalı.'),
    dict(url='https://siyasetakademi.com/haber/omer-gunel-demiparmakliklar-ardindan-yeni-parti-kurultay-delege-listesine-girdi', state='read_unbound', note='26 Ekim 16.50 Aydın Şafak kaynaklı aktarım kongreye 4.608 oy ve rakip atfediyor; bu anlatım diğer ön seçim ve tek aday haberleriyle karışmış olabilir, doğrulanmadan sonuç sayısı olarak kullanılmaz.'),
    dict(url='https://zeybekhaber.com/haber/yeni-parti-aydin-da-kongre-tarihi-netlesti-dilaver-demir-tek-aday-olarak-girecek-124654.html', state='read_unbound', note='19 Ekim haberi ön seçim için Demir’e 4.250 oy atfediyor; 4.094 ve 4.152 bildiren diğer kaynaklarla farklılık uzlaştırılmadı.'),
]
p.write_text(json.dumps(q, ensure_ascii=False, indent=2) + '\n')
