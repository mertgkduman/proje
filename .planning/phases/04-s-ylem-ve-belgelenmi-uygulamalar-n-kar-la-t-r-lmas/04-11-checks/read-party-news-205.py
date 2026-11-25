from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
from pathlib import Path
import json, re

here = Path(__file__).resolve().parent
source = Path('/tmp/gsd0411-body374.json')
raw = source.read_bytes()
item = json.loads(raw)['veri']['haber']
assert int(item['id']) == 374
catalog = json.loads((here/'party-news-catalog.json').read_bytes())
post = next(p for p in catalog['posts'] if int(p['id']) == 374)
body = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', unescape(unescape(item['detay'])))).strip()
selections = [
    'Emeklilerimizin maaşlarına her yıl ‘Refah Payı’ adı altında, en az o yılın büyüme oranı kadar ilave zam yapılarak, ekonomik büyümeden pay almaları sağlanacaktır.',
    'Asgari ücrette açlık sınırı değil ‘İnsanca Yaşam’ ücreti hedeflenecek.',
]
passages = []
for exact in selections:
    start = body.index(exact)
    passages.append(dict(start=start, end=start+len(exact), exact=exact))
target = here/'party-news-bodies/374.json'
assert not target.exists()
target.write_bytes(raw)
read = dict(post_id=374, publisher=post['publisher'], public_url=post['public_url'], source_url=post['body_url'], final_url=post['body_url'], http_status=200, published_at=post['published_at'], updated_at=None, accessed_at=datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(), original_path='party-news-bodies/374.json', original_bytes=len(raw), sha256=sha256(raw).hexdigest(), normalized_body_sha256=sha256(body.encode()).hexdigest(), source_section_range=[0,len(body)], state='examined', reading='Temel Karamollaoğlu ekonomik eleştiriler sunuyor ve parti iktidarı için emekli aylığı, asgari ücret, adalet ve şiddetle mücadele hedefleri açıklıyor.', selected_passages=passages, point='2023 parti vizyonunda emekli aylığı ve ücret hedefleri.', statement='Parti iktidarında emekli aylıklarına en az büyüme oranında yıllık refah payı eklenmesini ve asgari ücrette insanca yaşam ücretini hedefliyor.', concrete_evidence='Parti yayımı 7 Aralık 2022 yerel günlü haftalık basın toplantısı metnini aktarıyor. Metin hedefleri gelecekteki iktidar bağlamına yerleştiriyor.', open_provenance='Bunlar siyasi hedeflerdir. Daha sonraki ücret, büyüme ve parti yetkisi ayrı kaynaklarla karşılaştırılmadı. Metindeki bütçe görüşmesi olayı ve diğer ekonomik iddialar da bu gövdeden bağımsız doğrulanmadı.')
receipt = dict(tranche_id='saadet-party-news-205', party_id='saadet', reviewer_kind='agent', processed_at=datetime.now(timezone.utc).isoformat(), reads=[read], completed_pre_cut_bodies=292, remaining_pre_cut_bodies=357, closure_refs=[], source_token_observation='Tam tekil gövdenin okuma çıktısı araç tarafından yaklaşık 5.172 token olarak raporlandı ve 12.000 token sınırının altında.', normalization='HTML varlıkları iki kez çözüldü. Etiketler kaldırıldı ve boşluklar birleştirildi. Erişim zamanı indirme dosyasının ilk yazılma zamanıdır.')
(here/'party-news-205-reading.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print('read',read['post_id'],read['sha256'],len(body))
