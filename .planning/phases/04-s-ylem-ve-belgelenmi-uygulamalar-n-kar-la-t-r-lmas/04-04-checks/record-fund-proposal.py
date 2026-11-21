import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json'); q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['site:tbmm.gov.tr "2 / 3895" "Özlale" fon','"2/3895" "Yatırımcıların Korunması" TBMM','"Özlale" "Adil Tasfiyesi" "28/09/2026" kanun teklifi','site:cdn.tbmm.gov.tr "Yatırımcıların Korunması Amacıyla Bazı Yatırım Fonlarının Adil Tasfiyesi"']]
url='https://tbmm.gov.tr/Yasama/KanunTeklifi/8bdc192b-ef6a-4ef2-befe-01a0e803dd24'
q['initial_readings'].append(dict(read_at='2026-11-21',url=url,section='TBMM teklif künyesi ve komisyon bilgileri',note='2/3895 Özlale ilk imzası, 28 Eylül Başkanlığa geliş ve 1 Ekim komisyon havalesi kayıtlı. Dinamik sayfanın bugünkü komisyon durumu, kesim anındaki durum olarak otomatik çıkarılmadı. Başka 2/3939 teklifinden ayrı. Python capture bağlantı sıfırlanınca curl HTTP 200 ile asıl HTML yakalandı.'))
q['captures'].append(dict(url=url,sha256='724f6b88fea0443df4881deefed05dfa28970649831a81c5008678963cf4f744',accessed_at='2026-11-21T20:52:02+00:00',state='source_records_draft'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
