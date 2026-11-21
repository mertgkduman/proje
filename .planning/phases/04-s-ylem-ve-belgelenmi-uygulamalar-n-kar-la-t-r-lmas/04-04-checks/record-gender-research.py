import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
for lead in q['candidate_leads']:
    if lead['url']=='https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/da56f7fb-b6de-4318-aa4e-01a1786d5869':
        lead['state']='source_records_draft';lead['note']+=' Özgün HTTP 200 HTML SHA256 b8b8a2795129974e1f85d4cbdf027844a5c2ec31048fbbcf860b2fe4147a1fc7; özet pasajı 0404-tbmm-gender-4875-p bağlı. Diğer aşamalar açık.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
