import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Samsun" "Özdağ" "Özçelik" "3 bin 999" "2026" ön seçim','"Samsun" "Özdağ" "Özçelik" "3 bin 998" ön seçim 2026','"Mehmet Özdağ" "Turgay Özçelik" "3798" 3998','"Mehmet Özdağ" "Turgay Özçelik" "3796" 3999']]
q['candidate_leads'].append(dict(url='https://www.samsunsondakika.com.tr/yeni-parti-samsun-il-baskanligi-on-seciminde-kazanan-mehmet-ozdag-zaferi-atakum-getirdi/44621',state='source_records_draft',note='19 Ekim Ahmet Can imzalı yerel haber Özdağ 3.999 ve Özçelik 3.796 bildiriyor; diğer 3.998/3.798 haberleriyle fark korunuyor. Kaynak tutanak göstermez ve yayınların köken bağı ayrıca incelenmeli. Özgün SHA256 5c5b0cd1b7b054ee5f7663d3af23eaf3489488ead38dcd26db59a4e2eb5bf139, pasaj 0404-samsun-onsecim-sondakika-p.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
