import json
from pathlib import Path

p = Path('data/practices/04-yeni-parti-tranches.json')
q = json.loads(p.read_text())
q['candidate_leads'] += [
    dict(url='https://tbmm.gov.tr/Yasama/KanunTeklifi/d026dc83-3d6c-42f1-8ac0-01a13ff8e1d8', state='source_records_draft', note='TBMM 2/3952: Aydın Milletvekili Evrim Karakoz 15 Ekim 2026, yurt yerleşimi sağlanamayan ihtiyaç sahibi öğrenciye barınma desteği ile ilk kira ve depozito teklifi. HTTP 200 özgün HTML SHA256 a91657281014ffd719ec751e1a841d168d95fd91a328d6342b19443de4957ab7, özet 0404-tbmm-housing-access-3952-p. Teklif kabul edilmiş yasa veya fiili ödeme değildir.'),
    dict(url='https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/30dc341b-9222-4a0e-85a3-01a14467c33d', state='source_records_draft', note='TBMM 10/4686: Ayça Taşkent ve 19 milletvekili 12 Ekim 2026 kira ve hane geliri etkileri araştırma talebi. HTTP 200 özgün HTML SHA256 8c55bf6c468640f54f44d5f834b6637527f373160a5f797a7f91fd05911b2d6f, özet 0404-tbmm-housing-access-104686-p. Komisyon veya uygulama sonucu çıkarılmaz.'),
    dict(url='https://www.tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/4809b13c-21c0-4890-ab38-01a1a5753575', state='source_records_draft', note='TBMM 7/52416: Mustafa Sezgin Tanrıkulu 3 Kasım 2026 Diyarbakır engelli hizmetlerinin erişilebilirliğine ilişkin yazılı soru. HTTP 200 özgün HTML SHA256 ec230d864f8938f750c36f326bdfd705e66d90a735cdd24905823b1bdcc885ae, özet 0404-tbmm-housing-access-752416-p. Dinamik sayfadaki sonraki yanıt durumu kesime taşınmaz; soru uygulama sonucu sayılmaz.'),
]
p.write_text(json.dumps(q, ensure_ascii=False, indent=2)+'\n')
