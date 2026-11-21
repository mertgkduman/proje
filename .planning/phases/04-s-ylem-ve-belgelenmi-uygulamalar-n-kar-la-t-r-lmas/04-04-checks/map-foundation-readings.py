import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text());count=0
for t in q['tranches']:
 matches=[s for s in q['source_queue'] if s['version_id'] in t['source_ids'] and s['section'] in t['source_section_ranges'] and t['topic_id'] in s['topic_ids'] and s['state']=='source_read_pending_scope']
 if matches:
  t['foundation_reading']={'read_at':'2026-11-21','source_inventory_ids':[s['inventory_id'] for s in matches],'note':'İlgili kurucu kaynak bölümleri toplu okundu; bu yalnız kaynak bağlamı okumasıdır, olay araması veya kapsam kapanışı değildir.'};count+=1
assert count==230
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print('FOUNDATION_MAPPED',count,'remaining pending',sum(t['state']=='pending' for t in q['tranches']))
