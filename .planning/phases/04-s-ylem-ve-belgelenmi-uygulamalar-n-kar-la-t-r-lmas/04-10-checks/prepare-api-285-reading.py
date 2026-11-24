import hashlib, html, json, re
from datetime import datetime, timezone
from pathlib import Path

c = Path(__file__).resolve().parent
page = c / 'party-api-pages/page-25.json'
post = next(p for p in json.loads(page.read_text()) if p['id'] == 3305)
body = post['content']['rendered']
start, end = 72000, len(body)
assert end == 75374
digest = lambda text: hashlib.sha256(text.encode('utf-8')).hexdigest()
normalized = ' '.join(html.unescape(re.sub('<[^>]*>', ' ', body)).split())
prior = [json.loads((c / f'party-api-{n}-source-reading.json').read_text()) for n in range(279, 285)]
parts = [next(p for p in prior[0]['parts'] if p['post_id'] == 3305)] + prior[1:]
assert all(p['body_sha256'] == digest(body) and p['total_char'] == end for p in parts)
assert parts[0]['start_char'] == 0 and parts[-1]['end_char'] == start
assert all(parts[i]['end_char'] == parts[i+1]['start_char'] for i in range(len(parts)-1))
receipt = {
    'tranche_id': '0410-emep-api-285', 'read_at': datetime.now(timezone.utc).isoformat(),
    'method': 'Özgün İngilizce HTML gövdesinin Python karakter indisleriyle yarı açık [72000,75374) son aralığı okundu; önceki makbuzların aralık sürekliliği ve tam gövde özeti bağımsız kontrol edildi.',
    'post_id': post['id'], 'url': post['link'], 'api_date': post['date'], 'page': str(page),
    'body_sha256': digest(body), 'start_char': start, 'end_char': end,
    'total_char': len(body), 'slice_sha256': digest(body[start:end]),
    'reading_note': 'Son bölüm bilim ve spora erişim, çevresel ve kentsel kararlarda halk denetimi, engelli ve yaşlıların katılımı, çocuk hakları, toplumsal cinsiyet eşitliği, kadınlara şiddetin önlenmesi ve sığınmacılara ayrımcılık yapılmaması taleplerini içerir. Yurt dışında yaşayan Türkiyeli işçilerin eşitliği ve zorunlu askerlikten muafiyet de önerilir. Gövde sonunda Kasım 2016 tarihi basılıdır; API yayın tarihi ayrı korunur.',
    'normalization_check': {'method': 'HTML etiketlerini boşluğa çevir, entity çöz ve tüm whitespace dizilerini tek boşluğa indir.', 'normalized_text_chars': len(normalized), 'normalized_text_sha256': digest(normalized), 'range_coordinate_system': 'Özgün HTML gövdesi; normalize düz metin değildir.'},
    'prior_279_count': {'combined_chars': sum(p['end_char']-p['start_char'] for p in prior[0]['parts']), 'other_seven_bodies_chars': sum(p['end_char']-p['start_char'] for p in prior[0]['parts'] if p['post_id'] != 3305), 'post_3305_chars': 12000},
    'limitations': ['Program talepleri gerçekleşmiş uygulamalar değildir.', 'Bu tek özgün program gövdesinin tamamlanması bütün parti kaynağı veya faz kapsamının kapanması değildir.'],
    'next_unread': 'API kaynak sırasındaki 3305 sonrası sonraki gövde incelenmeli.', 'closure_refs': []
}
with (c / 'party-api-285-source-reading.json').open('x') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('API285_READING_OK', end - start, receipt['slice_sha256'], len(normalized))
