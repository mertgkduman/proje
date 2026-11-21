import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json')
q=json.loads(p.read_text())
q['candidate_leads'] += [
 dict(url='https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/2b8512b1-652e-4c99-b67a-01a1207db7cd',state='read_unbound',note='TBMM sayfası web okumasında 10/4676, Başkanlığa geliş 9 Ekim, Kayıhan Pala ve 20 milletvekili, meslek hastalıklarının tanı/bildirim/önlenmesi için araştırma isteği görülüyor. Sayfadaki güncel durum kesim anına uygulanmadı. Özgün HTML yakalama her iki hostta bağlantı sıfırlanmasıyla başarısız; arşiv bağı henüz yok.'),
 dict(url='https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T10/WebOnergeMetni/99af6ef2-6f2e-4bd0-a0a9-487eda8124cf.pdf',state='captured_unbound',note='TBMM bağlı PDF HTTP 200; 3 sayfa, SHA256 a6b8b16c15ebdac19848682812aa6176d7a565634e7dd891dc1f09f6fb35271e. İlk sayfa metin çıkarımı yalnız 10/4676 üretiyor; tarama sayfaları doğrudan okunup indeksli pasajın doğrulanabilirliği araştırılacak. Başka sitedeki OCR özgün pasaj olarak kullanılmadı.'),
]
q['captures'].append(dict(url='https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T10/WebOnergeMetni/99af6ef2-6f2e-4bd0-a0a9-487eda8124cf.pdf',sha256='a6b8b16c15ebdac19848682812aa6176d7a565634e7dd891dc1f09f6fb35271e',accessed_at='2026-11-21',state='captured_unbound'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
