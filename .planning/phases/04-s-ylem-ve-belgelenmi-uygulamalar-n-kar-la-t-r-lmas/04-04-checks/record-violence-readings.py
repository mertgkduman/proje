import json
from pathlib import Path

p = Path('data/practices/04-yeni-parti-tranches.json'); q = json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21', query=s) for s in ['"Yeni Parti" 2026 "kadın" "şiddet" meclis araştırması önergesi', '"Yeni Parti" 2026 "iklim" "kuraklık" meclis araştırması önergesi', '"Yeni Parti" 2026 "deprem" "konut" meclis araştırması önergesi', '"10/4651" "2026" "TBMM" iklim tarım işçilerinin']]
q['candidate_leads'] += [
    dict(url='https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/d1ebf2ae-d7fd-40ca-a759-01a1446123b7', state='source_records_draft', note='TBMM 10/4683: Ayça Taşkent ve 19 milletvekili 12 Ekim 2026 kadına yönelik şiddetin önlenmesi için araştırma istedi. 21 Kasım HTTP 200 özgün HTML SHA256 93ecb54a5c7fc54120d85000f6f7c1d8ba37ae013b7652a4e10fc814985c95a0; özet 0404-tbmm-kadina-siddet-104683-p. Talep komisyon kurulması veya fiili sonuç değildir.'),
    dict(url='https://www.tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/c1c96224-192e-42eb-a3e8-01a0f1bcb328', state='source_records_draft', note='TBMM 7/49746: Ali Gökçek 29 Eylül 2026 kadına yönelik şiddet ve kadın cinayetlerinin önlenmesine dair yazılı soru yöneltti. 21 Kasım HTTP 200 özgün HTML SHA256 f1440dc19710b02a15d803c4f99a13bf4fe6f619f1ed8c874c1ebc6ffd1f6452; özet 0404-tbmm-kadina-siddet-749746-p. Soru yanıt veya fiili sonuç değildir.'),
    dict(url='https://tbmm.gov.tr/Milletvekili/UyeMeclisArastirmaOnergeleri?Id=f72877c2-dcc4-037b-e050-007f01005610&ortakDonemId=134155f0-c3d6-4d24-893b-f3a2ef695ae7', state='read_partial_unbound', note='TBMM arama görünümünde 8 Ekim 10/4651 iklim krizinin tarım işçilerine etkisi araştırma önergesi listeleniyor. Liste ortak imzayı gösterebilir; teklifin özgün künyesi, ilk imzacı ve parti kimliği ayrıca okunmalı.'),
]
p.write_text(json.dumps(q, ensure_ascii=False, indent=2)+'\n')
