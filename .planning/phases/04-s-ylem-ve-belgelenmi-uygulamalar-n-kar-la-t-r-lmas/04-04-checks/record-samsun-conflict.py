import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text());q['candidate_leads'].append(dict(url='https://diyekonustu.com/kamera-rezaletinin-golgesinde-kongre-yeni-parti-samsunda-yarin-secim-var-kavgalar-ve-on-secimler-hafizalarda',state='source_records_draft',note='24 Ekim haberinde 18 Ekim Samsun ön seçimi için Özdağ 3.998 ve Özçelik 3.798 olarak aktarılıyor; daha önceki Samsun Olay pasajı 3.999 ve 3.796 bildirir. Sayılar uzlaştırılmadı. Haberde kamera tartışması ve itiraz iddiaları başka kaynaklara atfedilir; gerçek durum ayrıca araştırılmalı. Özgün SHA256 6b37f4d5c9daa761caea32b5a270f68158cb1d0eb952c036f1ebef649b53486c, pasaj 0404-samsun-onsecim-diye-p.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
