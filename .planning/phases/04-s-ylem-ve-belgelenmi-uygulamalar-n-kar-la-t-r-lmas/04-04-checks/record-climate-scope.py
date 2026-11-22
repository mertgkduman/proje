import json
from pathlib import Path

p = Path('data/practices/04-yeni-parti-tranches.json')
q = json.loads(p.read_text())
url = 'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/35ebbaef-ef4c-4f18-abcf-01a11b750c08'
leads = [x for x in q['candidate_leads'] if x['url'] == url]
assert len(leads) == 1
leads[0]['note'] += ' Faz 3 seçili 04-03-v3-0303-epm-program-scope-tarim-iscisi-row kanonik veritabanında no_explicit_statement durumunda; tarım işçilerine özgü kaynaklı hedef uydurulmadı. İlişkisiz olay ve kapsam adımları ayrıca değerlendirilecek.'
p.write_text(json.dumps(q, ensure_ascii=False, indent=2)+'\n')
