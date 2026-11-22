import json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text

comparison=json.loads(Path('data/comparisons/03-tip-program.json').read_text())['records']
source=html_source_text(Path('data/objects/6aa8a0087e2426e808defbc8e427281f08862b1206fdad2ae847fd294854c7e0/original.html.bin').read_bytes())
topics={
 'inanc-mezhep-esitligi':(['0304-tip-program-inanc-p1','0304-tip-program-inanc-p2'],'Program Alevilerin eşit yurttaşlığı, zorunlu din dersleri ve Diyanet yanında, din işlerinin tüm din ve mezheplere eşit mesafeli bir kurumda yeniden düzenlenmesini de içerir.'),
 'anadilde-egitim':(['0304-tip-program-egitim-dil-p1'],'Program her düzeyde nitelikli, parasız, anadilde, laik ve bilimsel eğitim hakkını savunur.'),
 'tarim-hayvancilik':(['0304-tip-program-tarim-p1'],'Program tohum üretim merkezleri, kooperatif taban fiyatı, mera koruması ve yerli hayvancılık desteğini birlikte önerir.')}
passages={x['values']['id']:x['values']['exact'] for x in comparison if x['kind']=='passage'}
for ids,_ in topics.values():
 for ident in ids: assert passages[ident] in source,ident
path=Path('data/practices/04-tip-tranches.json'); data=json.loads(path.read_text()); count=0
for row in data['tranches']:
 if row['research_kind']!='statement' or row['topic_id'] not in topics: continue
 assert row['state']=='pending' and row['processed_at'] is None and not row['closure_refs']
 ids,note=topics[row['topic_id']]
 row['research_progress']=dict(recorded_at=datetime.now(timezone.utc).isoformat(),note=note+' Bu kaynak tek başına dönem boyu bütün söylemleri veya tarihsel sürümü belirlemez; TBMM, parti, haber ve diğer uçlar açıktır.',source_ids=['0203-tip-program-v1'],urls=['https://tip.org.tr/parti-programi'],source_passage_ids=ids,status='partial')
 count+=1
assert count==3
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('PARTIAL_STATEMENT_LINKS',count)
