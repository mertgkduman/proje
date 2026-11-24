import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

c = Path(__file__).resolve().parent
page = c / 'party-api-pages/page-25.json'
post = next(p for p in json.loads(page.read_text()) if p['id'] == 3305)
body = post['content']['rendered']
start, end = 36000, 48000
assert len(body) == 75374 and end <= len(body)
digest = lambda text: hashlib.sha256(text.encode('utf-8')).hexdigest()
receipt = {
    'tranche_id': '0410-emep-api-282', 'read_at': datetime.now(timezone.utc).isoformat(),
    'method': 'Özgün İngilizce HTML gövdesinin Python karakter indisleriyle yarı açık [36000,48000) aralığı okundu; tam gövde ve aralık UTF-8 SHA-256 ile bağlandı.',
    'post_id': post['id'], 'url': post['link'], 'api_date': post['date'], 'page': str(page),
    'body_sha256': digest(body), 'start_char': start, 'end_char': end,
    'total_char': len(body), 'slice_sha256': digest(body[start:end]),
    'reading_note': 'V. bölümün devamında reel ücretler, güvencesiz çalışma, kamusal hizmetlerin özelleştirilmesi, uluslararası kurumlar ve savaşlar konusunda program değerlendirmesi bulunur; kâr amacıyla üretimin doğayı ve ekolojik dengeyi tehdit ettiğini savunur. VI. bölüm Türkiye kapitalizminin bağımlılığına, Kurtuluş Savaşı ve sonrasına, Kürtlerin ulusal haklarına, bölgesel eşitsizliklere, köy boşaltmaları ve kırdan göçe ilişkin tarihsel ve siyasal analizini sunar. Aralık VI. bölüm 6. maddesinin içinde kesilir.',
    'limitations': ['Bu içerik programın siyasi ve tarihsel değerlendirmesidir; kesin tarihsel sonuçlar veya ölçülmüş çevresel etkiler olarak bağımsız doğrulanmadı.', '48000 sonrası bu makbuzda okunmadı; çevre konusundaki genel sav doğrudan Akbelen için somut izin veya uygulama kanıtı sayılmadı.'],
    'next_unread': {'post_id': 3305, 'start_char': end, 'total_char': len(body)}, 'closure_refs': []
}
with (c / 'party-api-282-source-reading.json').open('x') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('API282_READING_OK', end - start, receipt['slice_sha256'])
