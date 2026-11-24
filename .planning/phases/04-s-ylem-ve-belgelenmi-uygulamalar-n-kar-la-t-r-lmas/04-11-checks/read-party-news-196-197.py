from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
from pathlib import Path
import json, re

here = Path(__file__).resolve().parent
catalog = json.loads((here/'party-news-catalog.json').read_bytes())
posts = {int(p['id']): p for p in catalog['posts']}
cases = [
 (196,384,'Deprem sonrası kadınların koşulları ve afet yönetimi.','Konuşma deprem sonrasındaki barınma ve koordinasyon sorunlarını ele alıyor ve kadınların ihtiyaçlarını anlatıyor.','Parti yayımı 9 Mart 2023 tarihli konuşma metni içeriyor.','Metinde konuşmacının kimliği bu gövdede açık değil. Aktarılan eleştiriler bağımsız olarak doğrulanmış olay sonucu değildir.','Depremin ardından bölgede kalan veya göç eden kadınların halihazırda yaşadıkları sorunlara her geçen gün yenileri ekleniyor.'),
 (197,383,'Deprem sonrası eğitim ve afet hazırlığı.','Karamollaoğlu üniversitelerin derhal yüz yüze eğitime başlamasını istiyor.','22 Şubat yerel günlü parti yayımı, çağrıyı haftalık basın toplantısına atfediyor.','YÖK kararı ve üniversitelerin fiilî uygulaması bu gövdede kanıtlanmıyor. Derhal tam yüz yüze eğitim talebi ile sonradan alınabilecek karma eğitim kararı ayrı incelenmeli.','üniversiteler derhal yüz yüze eğitime başlamalıdır'),
]
for tranche, pid, point, statement, evidence, uncertainty, selected in cases:
    original = Path('/tmp/gsd0411-body'+str(pid)+'.json')
    raw = original.read_bytes()
    item = json.loads(raw)['veri']['haber']
    assert int(item['id']) == pid
    text = unescape(unescape(item['detay']))
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    start = text.index(selected)
    accessed = datetime.fromtimestamp(original.stat().st_mtime, timezone.utc).isoformat()
    dest = here/'party-news-bodies'/f'{pid}.json'
    assert not dest.exists()
    dest.write_bytes(raw)
    p = posts[pid]
    read = dict(post_id=pid, publisher=p['publisher'], public_url=p['public_url'], source_url=p['body_url'], published_at=p['published_at'], updated_at=None, accessed_at=accessed, original_path=f'party-news-bodies/{pid}.json', sha256=sha256(raw).hexdigest(), normalized_body_sha256=sha256(text.encode()).hexdigest(), source_section_range=[0,len(text)], state='examined', reading=statement, selected_passages=[dict(start=start,end=start+len(selected),exact=selected)], point=point, statement=statement, concrete_evidence=evidence, open_provenance=uncertainty)
    record = dict(tranche_id=f'saadet-party-news-{tranche}', party_id='saadet', reviewer_kind='agent', processed_at=datetime.now(timezone.utc).isoformat(), reads=[read], completed_pre_cut_bodies=281+(tranche-195), remaining_pre_cut_bodies=368-(tranche-195), closure_refs=[], normalization='HTML varlıkları iki kez çözüldü. Etiketler kaldırıldı ve boşluklar birleştirildi. Erişim zamanı indirme dosyasının ilk yazılma zamanıdır.')
    (here/f'party-news-{tranche}-reading.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(pid, len(text), read['sha256'])
