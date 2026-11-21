import json
from pathlib import Path

path = Path('data/practices/04-yeni-parti-tranches.json')
queue = json.loads(path.read_text())
queue['candidate_leads'] += [
    dict(url='https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/679bdb2f-a46e-41f2-ba81-01a144692e1f', state='source_records_draft', note='TBMM 10/4687: Ayça Taşkent ve 19 milletvekili 12 Ekim 2026 çocuk yoksulluğu, çocuk işçiliği ve MESEM için araştırma önergesi. 21 Kasım özgün HTML SHA256 fabd52ee4d48f3054d2a1b53a374710e3b5a59136e9a93fe39625c222a73e619; özet pasajı 0404-tbmm-cocuk-emegi-4687-p. Bu önerge 10/4682 ve 10/4553 ile ayrı kimliktedir; uygulama sonucu değildir.'),
    dict(url='https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/e67c5f6e-b36d-4bdb-bac5-01a0f6a6484a', state='source_records_draft', note='TBMM 10/4553: Turan Taşkın Özer ve 20 milletvekili 30 Eylül 2026 çocuk işçiliği ve MESEM hak ihlalleri için araştırma önergesi. 21 Kasım özgün HTML SHA256 d6f0a1dce9a2a6a33057c1afd7b6357df7cd0a23263b5cbfd944bb6e494d75ce; özet pasajı 0404-tbmm-cocuk-emegi-4553-p. Başvuru ayrı künye ve olaydır; kabul ya da fiili politika kanıtı değildir.'),
]
path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + '\n')
