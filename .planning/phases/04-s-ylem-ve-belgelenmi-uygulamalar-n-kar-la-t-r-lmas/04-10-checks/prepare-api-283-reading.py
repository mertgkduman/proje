import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

c = Path(__file__).resolve().parent
page = c / 'party-api-pages/page-25.json'
post = next(p for p in json.loads(page.read_text()) if p['id'] == 3305)
body = post['content']['rendered']
start, end = 48000, 60000
assert len(body) == 75374 and end <= len(body)
digest = lambda text: hashlib.sha256(text.encode('utf-8')).hexdigest()
receipt = {
    'tranche_id': '0410-emep-api-283', 'read_at': datetime.now(timezone.utc).isoformat(),
    'method': 'Özgün İngilizce HTML gövdesinin Python karakter indisleriyle yarı açık [48000,60000) aralığı okundu; tam gövde ve aralık UTF-8 SHA-256 ile bağlandı.',
    'post_id': post['id'], 'url': post['link'], 'api_date': post['date'], 'page': str(page),
    'body_sha256': digest(body), 'start_char': start, 'end_char': end,
    'total_char': len(body), 'slice_sha256': digest(body[start:end]),
    'reading_note': 'VI. bölümün devamı halk iktidarı ve kurucu meclis önerilerini sunar. Seçilmiş yerel meclisler, yargıçların seçimi, eşit haklar, açık kamusal veriler, dolaylı vergilerin kaldırılması, sendika ve grev hakları, Kürt ulusu dahil ulusların kendi kaderini tayini ve anadilde kamu hizmeti ister. Din ve devletin ayrılması, vicdani ret, ücretsiz laik eğitim, seçilmiş üniversite kurulları ve ücretsiz sağlık hizmetleri savunulur. Aralık bağımsız ülke başlığındaki ilk maddenin içinde kesilir.',
    'limitations': ['Bunlar parti programının talepleridir; kabul edilmiş kanun veya gerçekleştirilmiş hizmet sayılmaz.', '60000 sonrası bu makbuzda okunmadı; başka sürümlerle aynı olduğu varsayılmadı.'],
    'next_unread': {'post_id': 3305, 'start_char': end, 'total_char': len(body)}, 'closure_refs': []
}
with (c / 'party-api-283-source-reading.json').open('x') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('API283_READING_OK', end - start, receipt['slice_sha256'])
