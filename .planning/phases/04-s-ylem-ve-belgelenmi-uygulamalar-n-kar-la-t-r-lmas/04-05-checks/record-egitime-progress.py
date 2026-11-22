import json
from datetime import datetime, timezone
from pathlib import Path

path=Path('data/practices/04-tip-tranches.json'); data=json.loads(path.read_text()); count=0
for row in data['tranches']:
    if row['topic_id']!='egitime-erisim': continue
    assert row['state']=='pending' and row['processed_at'] is None and not row['closure_refs']
    row['research_progress']={
        'recorded_at':datetime.now(timezone.utc).isoformat(),
        'note':'Faz 3 programının her düzeyde parasız eğitim hakkı bağlamı, 2021 öğrenci barınmasına ilişkin 2/3833 taramasının altı sayfası ve haberde aktarılan destek okundu. Yurt barınması ile eğitim ücretlendirmesi aynı konu değildir; programın 2021 sürümü, diğer olay ve uçlar araştırılmalı.',
        'source_ids':['0203-tip-program-v1','0405-tip-yurt-273833-v1','0405-tip-yurt-gercek-v1'],
        'urls':['https://tip.org.tr/parti-programi','https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y5/T2/WebOnergeMetni/dd7a45ef-6f9b-4dfb-80eb-651a7f840f6f.pdf','https://www.gercekhaberci.com/gundem/yurt-krizi-tbmm-ye-tasindi-tip-li-4-vekilden-kanun-teklifi/147956'],
        'status':'partial'}
    count+=1
assert count==2
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('PARTIAL_SCOPE_LINKS',count)
