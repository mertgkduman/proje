import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text());url='https://www.cesmeninsesi.com.tr/haber/yeni-partide-online-uyelik-sistemi-acildi-basvuru-nasil-yapilacak-1786521038'
items=[x for x in q['candidate_leads'] if x['url']==url];assert len(items)==1
items[0]['state']='source_records_draft';items[0]['note']='Çeşme’nin Sesi 12 Ağustos tarihli haberde çevrim içi sistemin açıldığını ve ilçe başkanlığının 12 sayfalık rehberini bildiriyor. 21 Kasım HTTP 200 özgün HTML SHA256 168f132c8999a2aced91a47f554ebac322aeeb31e9ac524942b534fae9aacade; 0404-cevrimici-uyelik-cesme-p. Haberin tarihi açılışın kesin günü değildir; 11 Ağustos sistem ve 13 Ağustos kampanya anlatımları ayrı araştırılır. Tekil başvuru kabulü kanıtlanmaz.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
