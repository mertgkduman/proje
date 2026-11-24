import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

checks = Path(__file__).resolve().parent
page = checks / 'party-api-pages/page-24.json'
posts = {p['id']: p for p in json.loads(page.read_text())}
notes = {
 3519: (6811, 'Gürkan röportajının devamında özel sağlık kuruluşlarının kalıcı kamulaştırılmasını ve zorunlu sektörler dışındaki üretimin geçici durdurulması ile ücretli izni savunuyor. Metin sonunda röportajın Evrensel kaynaklı olduğu belirtilir; yeniden yayımlama ayrı röportaj değildir.'),
 3513: (0, 'CIPOML Avrupa bileşenlerinin ortak deklarasyonunda ücretsiz sağlık ve koruyucu araç, işten çıkarmaların durdurulması ve gelir güvencesi istenir. İmzacılar arasında EMEP Türkiye vardır; tüm metin tek parti yazarlığı sayılamaz.'),
 3510: (0, 'EMEP Bölge Örgütü Batman, Silvan, Lice ve Ergani belediyelerine görevlendirme ve eşbaşkanların gözaltına alınması iddiasını eleştirir, serbest bırakılmalarını ister. Her yer ve işlem yetkili kayıtla ayrı doğrulanmalı.'),
 3507: (0, 'Levent Tüzel cezaevi salgın riskine karşı yaşlı, hasta, kadın ve çocukların infazına ara verilmesini veya adli kontrolle salıverilmesini ister; paketin hangi taslak olduğu ve hukuki kapsam ayrı doğrulanmalı. 7242 kabulüyle tek başına aynı olay değildir.'),
 3505: (0, 'Şükran Doğan sağlık hizmetlerinin ticarileştirilmesini eleştirir, koruyucu hizmetlerin öncelenmesi ve eşit ücretsiz nitelikli sağlık hizmeti ister. Beş milyon GSS kapsam dışı iddiası ve şehir hastanesi garantileri bağımsız veri ve sözleşmelerle doğrulanmalı.')
}
parts = []
for pid, (start, note) in notes.items():
 p = posts[pid]; body = p['content']['rendered']; part = body[start:]
 digest = lambda text: hashlib.sha256(text.encode()).hexdigest()
 parts.append(dict(post_id=pid, url=p['link'], page=str(page), body_sha256=digest(body), start_char=start, end_char=len(body), slice_sha256=digest(part), body_temporal_status='last_modified_at_or_before_cutoff', reading_note=note))
out = dict(tranche_id='0410-emep-api-270', read_at=datetime.now(timezone.utc).isoformat(), method='Özgün API HTML gövdeleri doğrudan okundu; her aralık ve tam gövde UTF-8 SHA-256 ile bağlandı. 3519 yalnız 269da kalan devamdır.', limitations=['Beyanlar, hukuki ve sağlık iddiaları bağımsız doğrulanmadı.', 'CIPOML ortak açıklamasının imzacılığı bağımsız parti kararı veya yetki ispatlamaz.', 'Yeni kapsam kapanışı yoktur.'], parts=parts, closure_refs=[])
assert sum(p['end_char']-p['start_char'] for p in parts) < 48000
with (checks/'party-api-270-source-reading.json').open('x') as f:
 json.dump(out, f, ensure_ascii=False, indent=2); f.write('\n')
print('API270_READING_OK',sum(p['end_char']-p['start_char'] for p in parts))
