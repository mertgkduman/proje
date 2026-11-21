import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"İbrahim Karaca" "349" "357" 25 Ekim kongre','"İbrahim Karaca" "349" "Ankara" "kongresi" 2026','"İbrahim Karaca" "357" "372" "kongre" 25 ekim 2026','"Yeni Parti" "Ankara" "25 ekim" "divan" "oy" Karaca']]
q['candidate_leads'].append(dict(url='https://ankara24.com/news/yeni-parti-ankara-il-baskanligina-ibrahim-karaca-secildi-675145',state='read_search_index_unbound',note='25 Ekim 19:29 Mynet üzerinden AAya atfedilen özet 372 delege/357 oy bildiriyor; VTVdeki rakamla aynı olsa da kaynak zinciri ve Başkent Haberdeki 349 ile farkı çözülmedi. Sayfa arama indeksi okundu, henüz capture yok.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
