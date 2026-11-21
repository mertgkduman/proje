import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text());u='https://tbmm.gov.tr/Yasama/KanunTeklifi/86a79e3f-10fa-4d58-8941-01a143f5093a'
q['initial_readings'].append(dict(read_at='2026-11-21',url=u,section='TBMM 2/3960 teklif künyesi, özet ve ilk imza',note='TBMM dinamik kayıt 16 Ekim 2026da İbrahim Arslanın ilk imzasıyla en düşük emekli aylığını net asgari ücret seviyesine çıkarma teklifini bildiriyor. Bu bireysel teklifin sunumu, parti grup önerisi, yasanın kabulü veya fiilî ödeme olarak sunulmaz; güncel komisyon durumu kesim tarihine otomatik taşınmadı.'))
q['captures'].append(dict(url=u,sha256='5a5b39805347c8e8903d2cd1e7435ceb76782517a6fba846877aabbcd11e4d89',accessed_at='2026-11-21T21:47:56+00:00',state='source_records_draft'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
