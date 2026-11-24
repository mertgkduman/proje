import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

c = Path(__file__).resolve().parent
page = c / 'party-api-pages/page-25.json'
post = next(p for p in json.loads(page.read_text()) if p['id'] == 3305)
body = post['content']['rendered']
start, end = 24000, 36000
assert len(body) == 75374 and end <= len(body)
digest = lambda text: hashlib.sha256(text.encode('utf-8')).hexdigest()
receipt = {
    'tranche_id': '0410-emep-api-281', 'read_at': datetime.now(timezone.utc).isoformat(),
    'method': 'Özgün İngilizce HTML gövdesinin Python karakter indisleriyle yarı açık [24000,36000) aralığı okundu; tam gövde ve aralık UTF-8 SHA-256 ile bağlandı.',
    'post_id': post['id'], 'url': post['link'], 'api_date': post['date'], 'page': str(page),
    'body_sha256': digest(body), 'start_char': start, 'end_char': end,
    'total_char': len(body), 'slice_sha256': digest(body[start:end]),
    'reading_note': 'III. bölümün sonu kapitalizm ile komünizm arasında sosyalist geçiş, kapitalizmin restorasyonu ve dünya ölçeğinde devrim görüşlerini işler. IV. bölüm Ekim Devrimi, SSCB, iki dünya savaşı, sömürgecilik karşıtı mücadeleler ve Sovyetler Birliği Komünist Partisinin 20. Kongresi üzerine partinin tarih yorumunu verir; revizyonizm, kapitalizmin geri dönüşü ve 1990larda Sovyetler Birliğinin dağılmasını bu çerçevede açıklar. V. bölümün başı işçi sınıfı hareketi ve eşitsizlik değerlendirmesine geçer; aralık V. bölüm 2. maddenin içinde kesilir.',
    'limitations': ['Tarihsel anlatı ve değerlendirmeler parti programına atfedilir; bağımsız tarihsel olgu doğrulaması değildir.', '36000 sonrası bu makbuzda okunmadı; başka program sürümleri ile eşitlenmedi.'],
    'next_unread': {'post_id': 3305, 'start_char': end, 'total_char': len(body)}, 'closure_refs': []
}
with (c / 'party-api-281-source-reading.json').open('x') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('API281_READING_OK', end - start, receipt['slice_sha256'])
