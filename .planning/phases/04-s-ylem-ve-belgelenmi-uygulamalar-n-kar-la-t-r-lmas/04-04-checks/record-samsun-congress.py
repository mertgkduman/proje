import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json')
q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "İstanbul" "25 Ekim 2026" il kongresi başkan seçim','"Yeni Parti" "İstanbul" "18 Ekim 2026" il başkanlığı ön seçim sonuç','"Yeni Parti" "Samsun" "25 Ekim 2026" il kongresi seçim itiraz']]
q['candidate_leads'] += [
 dict(url='https://www.samsunobjektif.com/index.php/yeni-parti-samsun-il-kongresi-sona-erdi-mehmet-ozdag-yeniden-baskan',state='source_records_draft',note='25 Ekim 22.23 haberinde delegelerle yapılan il kongresinde Mehmet Özdağ’ın seçildiği ve 278 geçerli oydan 276 aldığı bildiriliyor. 18 Ekim ön seçimi ve o sürece ilişkin kamera/itiraz haberleri ayrı. Bağlı pasaj 0404-samsun-kongre-objektif-p; özgün bayt SHA256 a7785dcb788b4516878d3804a17f2f02ea8f91cdc8523fa3383f6a840ce7cf77; yönlendirme son adresi sürüm kaydında tutuldu.'),
 dict(url='https://samsunilkhaber.com.tr/yeni-parti-samsun-il-kongresinde-tuzuk-tartismasi',state='read_unbound',note='25 Ekim 13.24 haberinde kongrede bir üyenin tüzük ve söz hakkı itirazı ile divanın yanıtı aktarılıyor; sandıkların 17.00’ye kadar süreceği belirtiliyor. İddialar ve yanıtlar aynı kaynakta atıfla korunmalı, haber sonucu veya tutanak yerine geçirilmemeli.'),
 dict(url='https://www.indyturk.com/node/784009/haber/%C3%B6zg%C3%BCr-%C3%A7elik-yeni%CC%87-parti-i%CC%87stanbul-i%CC%87l-ba%C5%9Fkan%C4%B1-se%C3%A7ildi',state='read_unbound',note='18 Ekim ANKA kaynaklı İstanbul ön seçim haberi Özgür Çelik için resmî olmayan sonuç bildiriyor; kongre oylamasıyla özdeşlenmemeli, özgün bayt ve pasaj bağlanmalı.'),
]
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
