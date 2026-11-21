import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
for lead in q['candidate_leads']:
    if lead['url']=='https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/85b6bbae-2234-406d-9487-01a11b942e6a':
        lead['state']='source_records_draft';lead['note']+=' Özgün TBMM HTTP 200 HTML SHA256 48336797e511cc491574a68bcaaf159bb8fc199a12169ce7fd0a440688d7efa6; önerge amacı 0404-tbmm-deprem-4638-p pasajına bağlandı. Teklif sahibi ve tarihi kaynakta ayrı görülüyor, uygulama veya komisyon kararı çıkarılmaz.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
