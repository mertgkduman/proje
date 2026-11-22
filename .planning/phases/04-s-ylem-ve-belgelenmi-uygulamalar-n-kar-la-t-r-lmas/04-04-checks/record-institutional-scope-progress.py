import json
from pathlib import Path

p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
for row in q['tranches']:
    if row['topic_id']=='tbmm-grup':
        row['partial_readings']=[dict(at='2026-11-21',sources=['epm-charter-v1','0404-grup-kurulus-dunya-v1','0404-grup-yonetim-ekonomim-v1'],note='Tüzük grup hükmü ve 24/28 Temmuz ayrı grup seçim/kurul haberleri okundu. 0827149 pakette iki açık envanter kapsamı, üç inceleme ve iki aday taslak hâlindedir; henüz paket kontrolü veya kapsam kapanışı değildir.')]
    elif row['topic_id']=='uyelik-kabul-itiraz':
        row['partial_readings']=[dict(at='2026-11-21',sources=['epm-charter-v1','0404-cevrimici-uyelik-cesme-v1','0404-yeni-parti-haber-49-v1','0404-yeni-parti-haber-50-v1'],note='Kuruluş tüzüğü başvuru hükmü, 12 Ağustos yerel rehber haberi ve iki parti JSON açıklaması okundu; kesin açılış günü ve tekil kabul ayrı incelenmeli. İlişki yalnız ayrı taslaktadır, kapsam kapanmadı.')]
    else:continue
    assert row['state']=='pending' and not row['closure_refs']
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
