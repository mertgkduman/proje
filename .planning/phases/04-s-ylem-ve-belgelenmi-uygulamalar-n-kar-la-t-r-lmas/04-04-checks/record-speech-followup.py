import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "Samsun" "kongre" "söz hakkı" "tüzük" "25 Ekim" 2026','"Mehmet Özdağ" "kongre" "söz" "divan" "üye" 2026','"Yeni Parti" "Samsun" "kongrede" "tüzük" "konuşma" tartışması 2026','"Yeni Parti" "Samsun" "kongre" "konuşmasına izin verilmedi" 2026']]
for lead in q['candidate_leads']:
    if lead['url']=='https://samsunilkhaber.com.tr/yeni-parti-samsun-il-kongresinde-tuzuk-tartismasi':
        lead['note']+=' 21 Kasım sonraki dört aramada aynı yazı yeniden okundu; üyenin talebi ve divanın inceleme/iletme yanıtı var, ret veya nihai sonuç belirlenmedi. Karşıt kaynak, karar ve tutanak araştırması açık.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
