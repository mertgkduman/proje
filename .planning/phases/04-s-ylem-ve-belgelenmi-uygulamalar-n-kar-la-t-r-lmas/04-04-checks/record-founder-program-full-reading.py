import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text());url='https://cdn.yeni-parti.org.tr/site/calisma_programi.pdf';rows=[x for x in q['candidate_leads'] if x['url']==url];assert len(rows)==1
rows[0]['note']+=' PDF indeks 0 kapak, 3 içindekiler, 4–20 bütün metin sayfaları okundu; 1–2 ve 21–23 boş. İndeks 14–20 yerel yönetim, toplum, AB, mali şeffaflık, etik, seçim hazırlığı ve dönem sonu hedeflerini içerir. Metindeki iddialar sahibine aittir; vaatler fiilî sonuç sayılmaz.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
