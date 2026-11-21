import json
from pathlib import Path

p = Path('data/practices/04-yeni-parti-tranches.json')
q = json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21', query=s) for s in ['"Yeni Parti" "Merkez Bankası" "2026" "faiz"', '"Yeni Parti" "2026" "barınma" "kira" kanun teklifi', '"Yeni Parti" "2026" "engelli" "erişilebilirlik" önergesi']]
q['candidate_leads'] += [
    dict(url='https://tbmm.gov.tr/Yasama/KanunTeklifi/d026dc83-3d6c-42f1-8ac0-01a13ff8e1d8', state='read_partial_unbound', note='TBMM arama görünümü 15 Ekim 2026 Evrim Karakoz ilk imzalı öğrenci barınma desteği kanun teklifini gösteriyor. Özgün sayfa, esas numarası, künye, bayt ve kesim tarihinde işlem doğrudan incelenmeli; teklif uygulanmış destek sayılmaz.'),
    dict(url='https://vekilpedia.com/onerge/10-4686-konut-kiralarinin-hane-gelirleri-ve-yasam-kosullari-uzerindeki-etkilerinin-arastirilarak-a', state='read_partial_unbound', note='Arama görünümünde Ayça Taşkent ve 19 milletvekilinin 12 Ekim tarihli kira etkileri için 10/4686 araştırma talebi gösteriliyor. TBMM aslı, sahibinin sayısı ve kesim tarihi işlemi doğrulanmalı; kurulmuş komisyon varsayılmıyor.'),
    dict(url='https://vekilpedia.com/soru-onergesi/7-52416-diyarbakir-da-engelli-bireylere-sunulan-hizmetlerin-erisilebilirlik-duzeyine-iliskin', state='read_partial_unbound', note='Arama görünümünde Mustafa Sezgin Tanrıkulu 3 Kasım 7/52416 erişilebilirlik yazılı sorusu gösteriliyor. TBMM aslı ve künye doğrudan incelenmeli; sonradan güncellenen yanıtın kesim anındaki varlığı varsayılmıyor.'),
]
p.write_text(json.dumps(q, ensure_ascii=False, indent=2)+'\n')
