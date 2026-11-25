from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
from pathlib import Path
import json, re

here = Path(__file__).resolve().parent
catalog = json.loads((here / 'party-news-catalog.json').read_bytes())
posts = {int(p['id']): p for p in catalog['posts']}
cases = [
    (376, 'Asgari ücret, ekonomi ve altı lider toplantısı.',
     'Genel Başkan Temel Karamollaoğlu 8.500 liranın yetersiz olduğunu ve asgari ücretin en kısa zamanda yoksulluk sınırına çıkarılmasını hedeflediklerini söylüyor. Altı liderin gelecek ayın beşinde toplanacağını da belirtiyor.',
     'Parti API yayımı 29 Aralık 2022 yerel günü gösteriyor. Konuşma beş yıllık hedef ve 5 Ocak için sonraki toplantı ifadesi içeriyor.',
     'Yoksulluk sınırı ve ücret değerleri açıklamadaki siyasi değerlendirmedir. Takip eden toplantının gerçekleşmesi ve ücret verileri bu gövdeyle bağımsız doğrulanmadı.',
     '6’lı Masa’nın çalışmaları devam ediyor, önümüzdeki ayın 5’inde, biraz geciken toplantımızı inşallah gerçekleştireceğiz'),
    (375, 'Yerli üretim ve tarımsal destek önerileri.',
     'Kadın Kolları Genel Başkanı Nurgül Beytiye Ekinci üretimi ve tarımı güçlendirmeyi, tarımsal girdilere doğrudan destek ve vergi indirimi sağlamayı öneriyor.',
     '14 Aralık 2022 tarihli parti yayımı Yerli Malı Haftası basın toplantısı metninde Ekinci’nin parti adına önerilerini ve tarihsel sanayi iddialarını aktarıyor.',
     'Tarihsel fabrika sayıları ve CİMER’e atfedilen satış rakamları parti açıklamasıdır. Önerilerin fiilen uygulanması veya tarihsel iddialar burada bağımsız doğrulanmadı.',
     'Gübre, mazot, ilaç, tohum, elektrik, yem, sulama ücreti gibi girdi maliyetlerini doğrudan destek ve vergi indirimi yoluyla makul düzeylere çekeceğiz.'),
]
reads = []
for pid, point, statement, evidence, uncertainty, selected in cases:
    downloaded = Path('/tmp/gsd0411-body' + str(pid) + '.json')
    raw = downloaded.read_bytes()
    item = json.loads(raw)['veri']['haber']
    assert int(item['id']) == pid
    body = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', unescape(unescape(item['detay'])))).strip()
    start = body.index(selected)
    target = here / 'party-news-bodies' / f'{pid}.json'
    assert not target.exists()
    target.write_bytes(raw)
    p = posts[pid]
    reads.append(dict(post_id=pid, publisher=p['publisher'], public_url=p['public_url'], source_url=p['body_url'], final_url=p['body_url'], http_status=200, published_at=p['published_at'], updated_at=None, accessed_at=datetime.fromtimestamp(downloaded.stat().st_mtime, timezone.utc).isoformat(), original_path=f'party-news-bodies/{pid}.json', original_bytes=len(raw), sha256=sha256(raw).hexdigest(), normalized_body_sha256=sha256(body.encode()).hexdigest(), source_section_range=[0,len(body)], state='examined', reading=statement, selected_passages=[dict(start=start,end=start+len(selected),exact=selected)], point=point, statement=statement, concrete_evidence=evidence, open_provenance=uncertainty))
receipt = dict(tranche_id='saadet-party-news-204', party_id='saadet', reviewer_kind='agent', processed_at=datetime.now(timezone.utc).isoformat(), reads=reads, completed_pre_cut_bodies=291, remaining_pre_cut_bodies=358, closure_refs=[], total_original_bytes=sum(x['original_bytes'] for x in reads), source_token_observation='İki tam gövdenin okuma çıktısı araç tarafından yaklaşık 9.417 token olarak raporlandı. Her iki gövde birlikte 12.000 token sınırının altında.', normalization='HTML varlıkları iki kez çözüldü. Etiketler kaldırıldı ve boşluklar birleştirildi. Erişim zamanı indirme dosyasının ilk yazılma zamanıdır.')
(here/'party-news-204-reading.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print('read', [(r['post_id'],r['sha256'],r['source_section_range'][1]) for r in reads], 'total_bytes',receipt['total_original_bytes'])
