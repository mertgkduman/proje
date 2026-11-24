import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

c = Path(__file__).resolve().parent
page = c / 'party-api-pages/page-25.json'
post = next(p for p in json.loads(page.read_text()) if p['id'] == 3305)
body = post['content']['rendered']
start, end = 12000, 24000
assert len(body) == 75374 and end <= len(body)
digest = lambda text: hashlib.sha256(text.encode('utf-8')).hexdigest()
receipt = {
    'tranche_id': '0410-emep-api-280',
    'read_at': datetime.now(timezone.utc).isoformat(),
    'method': 'Özgün İngilizce HTML gövdesinin Python karakter indisleriyle yarı açık [12000,24000) aralığı okundu; tam gövde ve aralık UTF-8 SHA-256 ile bağlandı.',
    'post_id': post['id'], 'url': post['link'], 'api_date': post['date'],
    'page': str(page), 'body_sha256': digest(body), 'start_char': start,
    'end_char': end, 'total_char': len(body), 'slice_sha256': digest(body[start:end]),
    'reading_note': 'II. bölümün devamı tekellerin rekabetle birlikte var olduğu, sermaye ihracı, eşitsiz gelişme, paylaşım savaşları ve ezilen uluslar hakkında programın kuramsal görüşlerini açıklar; çevresel yıkımı azami kâr için teknoloji kullanımına bağlar. III. bölümün ilk maddeleri işçi ve halk mücadelelerinin uluslararası niteliğini, ulusal hareketlerle birleşmesini ve üretim araçlarının ortak mülkiyetini savunur. Aralık III. bölüm 5. maddesinin içinde kesilir.',
    'limitations': ['Metin parti programındaki görüş ve tarihsel yorumlardır; somut güncel uygulama veya bağımsız doğrulanmış ekonomik sonuç değildir.', '24000 sonrası bu makbuzda okunmadı; 2020 tarihli 3596 sürümüyle aynı gövde varsayılmadı.'],
    'next_unread': {'post_id': 3305, 'start_char': end, 'total_char': len(body)},
    'closure_refs': []
}
with (c / 'party-api-280-source-reading.json').open('x') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('API280_READING_OK', end - start, receipt['slice_sha256'])
