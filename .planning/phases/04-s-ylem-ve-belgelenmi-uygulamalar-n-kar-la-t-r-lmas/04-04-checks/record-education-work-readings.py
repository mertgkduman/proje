import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['candidate_leads'] += [
 dict(url='https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/35801ab5-85b1-4318-8a53-01a11b8bb800',state='source_records_draft',note='TBMM 10/4641, Ayhan Barut ve 19 milletvekili, 8 Ekim: okul masraflarının etkisi için araştırma talebi. HTTP 200 özgün HTML SHA256 cbb473b64cb905bcb64df7dc6937a58b448f1fa676d8b202d56ddfaee14a6865, özet 0404-tbmm-egitim-is-104641-p. Fiili eğitim desteği çıkarılmaz.'),
 dict(url='https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/1f0d45c3-5602-4965-a724-01a1abe8d35d',state='source_records_draft',note='TBMM 10/4975, Mehmet Tahtasız ve 20 milletvekili, 4 Kasım: MESEM ve iş kazaları araştırma talebi. HTTP 200 özgün HTML SHA256 30227263499f5d3d509d11951edd17a059e7ace2d4aaf8e117764f066f4e97b2, özet 0404-tbmm-egitim-is-104975-p. 10/4687 ve 10/4553 ile ayrı kayıttır; sonuç çıkarılmaz.'),
 dict(url='https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/49081965-6eb5-4f30-96bf-01a1a072c472',state='source_records_draft',note='TBMM 10/4955, Talat Dinçer ve 20 milletvekili, 3 Kasım: iş kazaları ve meslek hastalığı ölümleri araştırma talebi. HTTP 200 özgün HTML SHA256 bfd0cc2131df01e7cf4ac6729b50b05459988d159fc9b45d0a342c57476bd9bc, özet 0404-tbmm-egitim-is-104955-p. Komisyon veya fiili sonuç çıkarılmaz.'),
]
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
