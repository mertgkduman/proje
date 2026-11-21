import json
from pathlib import Path

p=Path('data/practices/04-yeni-parti-tranches.json')
q=json.loads(p.read_text())
for lead in q['candidate_leads']:
    if lead['url']=='https://gunaydinaydin.com/yeni-parti-aydin-kongresi-basladi':
        lead['state']='source_records_draft'
        lead['note'] += ' Bağlı pasaj 0404-aydin-kongre-gunaydin-p; özgün bayt SHA256 8cc7ee7096adacf85147474e694dcc59843b32cde41e2e3289c4422f3376f3e1.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
