import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text());pkg=json.loads(Path('data/practices/04-yeni-parti.json').read_text());links=pkg['practice_records']['practice_legacy_link']
for name,kind,key in [('legacy_action_queue','action','finding_id'),('legacy_match_queue','match','id')]:
    ids={row['legacy_id'] for row in links if row['legacy_kind']==kind}
    assert all(row[key] in ids for row in q[name])
    for row in q[name]:
        row['reading_note']+=' 62377616 doğrulanmış ara paketinde bu önceki kimlik için practice_legacy_link var; kaynak uçları ve kapsamın tamamı hâlâ açıktır.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
