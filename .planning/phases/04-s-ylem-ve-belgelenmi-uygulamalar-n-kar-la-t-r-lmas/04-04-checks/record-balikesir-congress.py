import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "Balıkesir" "25 Ekim 2026" il kongresi Erden Köybaşı','"Yeni Parti" Balıkesir il kongresi Köybaşı Ekim 2026 seçildi','"Yeni Parti" "Muğla" 2026 25 Ekim kongresi seçim itiraz','"Yeni Parti" "Ankara" 18 Ekim 2026 ön seçim başkanı Karaca']]
q['candidate_leads'] += [
 dict(url='https://www.korfezdehaber.com/yeni-parti-kongresinde-erden-koybasi-partinin-ilk-il-baskani-oldu/135997',state='source_records_draft',note='25 Ekim 18.25 Körfezde Haber kongrede Erden Köybaşı ve listesinin seçildiğini bildiriyor; 18 Ekim üyeler ön seçimi ayrı aşamadır. Özgün SHA256 c2f438ee6df56ee1bff2e42e259432e79e2df1d610cbf296c28b0cd4da8fdd7f, pasaj 0404-balikesir-kongre-korfez-p.'),
 dict(url='https://balikesirsonhaber.tr/haber/yeni-parti-balikesir-il-kongresinde-ayvalik-krizi-erden-koybasi-secildi-mesut-ergin-salonu-terk-etti-8752',state='read_unbound',note='25 Ekim kongre haberi Ayvalık örgütünün yönetimde yer alması konusunda görüş ayrılığı iddiası içeriyor; karşı yanıt, orijinal yayın künyesi, fotoğraf/tutanak ve kaynak bağları araştırılmalı.'),
]
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
