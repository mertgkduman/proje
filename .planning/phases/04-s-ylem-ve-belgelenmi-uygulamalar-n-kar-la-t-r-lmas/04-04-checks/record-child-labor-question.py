import json
from pathlib import Path

p = Path('data/practices/04-yeni-parti-tranches.json')
q = json.loads(p.read_text())
url = 'https://www.tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/3b62f539-25e5-4155-b4f1-01a17d34c9f1'
leads = [x for x in q['candidate_leads'] if x['url'] == url]
assert len(leads) == 1 and leads[0]['state'] == 'lead_unread'
leads[0]['state'] = 'source_records_draft'
leads[0]['note'] = 'TBMM 7/51913: İstanbul Milletvekili Ayşe Sibel Yanıkömeroğlu 23 Ekim 2026 çocuk işçiliğiyle mücadele konusunda Çalışma ve Sosyal Güvenlik Bakanına yazılı soru yöneltti. 21 Kasım özgün HTML SHA256 d8deccb63168c5581249b62bed77a56e23f4d7d0c5f487370d2e6f2a4c367b13; soru özeti 0404-tbmm-cocuk-soru-51913-p. TBMM güncel dinamik durumunun kesim tarihinde geçerli olduğu varsayılmaz; yanıt veya fiili sonuç çıkarılmaz.'
p.write_text(json.dumps(q, ensure_ascii=False, indent=2)+'\n')
