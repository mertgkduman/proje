import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "10/4641" okul masrafları 2026','"Yeni Parti" "2026" "sağlık" "randevu" meclis araştırması','"Yeni Parti" 2026 "işçi sağlığı" "iş kazaları" meclis araştırması 10/']]
q['candidate_leads'] += [
    dict(url='https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/35801ab5-85b1-4318-8a53-01a11b8bb800',state='read_partial_unbound',note='TBMM arama görünümünde 8 Ekim 10/4641 artan okul masraflarının araştırılması önergesi. İlk imza ve tam künye TBMM aslıyla doğrulanmalı; önerge fiili eğitim desteği değildir.'),
    dict(url='https://vekilpedia.com/onerge/10-4975-mesem-uygulamalari-ile-is-kazalari-isci-olumleri-ve-cocuk-isciliginin-nedenlerinin-arasti',state='read_partial_unbound',note='Arama görünümünde Mehmet Tahtasız ilk imzalı 4 Kasım 10/4975 MESEM ve iş kazaları araştırma talebi. TBMM aslı, künye ve kimlik doğrulanmalı; 10/4687 ve 10/4553 ile farklı numaradır.'),
    dict(url='https://vekilpedia.com/onerge/10-4955-is-kazalari-ve-meslek-hastaliklari-sonucu-yasanan-olumler-arastirilarak-alinmasi-gereken-o',state='read_partial_unbound',note='Arama görünümünde Talat Dinçer ilk imzalı 3 Kasım 10/4955 iş kazası ve meslek hastalığı araştırma talebi; TBMM aslı ve künye doğrulanmalı.'),
    dict(url='https://tbmm.gov.tr/Haber/tbmm-genel-kurulu-toplandi-20261110161117',state='read_partial_unbound',note='TBMM 10 Kasım Genel Kurul haberinde iş kazaları üzerine Yeni Parti grup önerisi aktarılıyor. Kesim anı 14:38:46 UTC olduğu için kesin olay zamanı ve haberin saat dilimi araştırılmadan kapsam içi iddia kurulmayacak.'),
]
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
