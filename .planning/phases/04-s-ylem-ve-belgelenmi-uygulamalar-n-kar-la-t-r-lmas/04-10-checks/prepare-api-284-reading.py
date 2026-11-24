import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

c = Path(__file__).resolve().parent
page = c / 'party-api-pages/page-25.json'
post = next(p for p in json.loads(page.read_text()) if p['id'] == 3305)
body = post['content']['rendered']
start, end = 60000, 72000
assert len(body) == 75374 and end <= len(body)
digest = lambda text: hashlib.sha256(text.encode('utf-8')).hexdigest()
receipt = {
    'tranche_id': '0410-emep-api-284', 'read_at': datetime.now(timezone.utc).isoformat(),
    'method': 'Özgün İngilizce HTML gövdesinin Python karakter indisleriyle yarı açık [60000,72000) aralığı okundu; tam gövde ve aralık UTF-8 SHA-256 ile bağlandı.',
    'post_id': post['id'], 'url': post['link'], 'api_date': post['date'], 'page': str(page),
    'body_sha256': digest(body), 'start_char': start, 'end_char': end,
    'total_char': len(body), 'slice_sha256': digest(body[start:end]),
    'reading_note': 'Bağımsız ülke başlığında NATOdan ayrılma, yabancı üslerin kapatılması, Kıbrıstan bütün yabancı askerlerin çekilmesi ve büyük işletme, maden ve ormanların kamulaştırılması istenir. Tarımda büyük toprakların paylaşımı, çiftçi borçlarının silinmesi ve üretici örgütlerinin söz hakkı savunulur. Çalışma başlığında yedi saatlik gün, fazla mesainin yasaklanması, ebeveyn izni, sendika ve grev hakları ile mevsimlik tarım işçileri için güvence istenir. Çevre bölümünde suyun metalaşmasına ve nükleer santrallere karşı çıkılır, ormanlar ve ekosistemlerin korunması savunulur. Son kısım kültür ve bilim tartışmasının içinde kesilir.',
    'limitations': ['Bunlar partinin program talepleridir; devletin izni, bireysel sonuç veya uygulamanın gerçekleştiği gösterilmez.', '72000 sonrası bu makbuzda okunmadı.'],
    'next_unread': {'post_id': 3305, 'start_char': end, 'total_char': len(body)}, 'closure_refs': []
}
with (c / 'party-api-284-source-reading.json').open('x') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('API284_READING_OK', end - start, receipt['slice_sha256'])
