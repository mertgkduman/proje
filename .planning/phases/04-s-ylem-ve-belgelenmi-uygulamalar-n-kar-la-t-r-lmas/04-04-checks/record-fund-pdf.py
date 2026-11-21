import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
u='https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T2/WebOnergeMetni/02b7bb10-296b-4bee-b929-14db999ee954.pdf'
q['initial_readings'].append(dict(read_at='2026-11-21',url=u,section='PDF ilk sayfa ve genel gerekçe',note='TBMM 2/3895 sayfasındaki 12 sayfalık teklif metni açıldı; ilk sayfada Özlale imzası ve 1 Ekim komisyon havalesi, genel gerekçede özel tasfiye önerisi görüldü. Yerel PDF metninin OCR yanlışları korunuyor; teklif kabul veya uygulama olarak sunulmaz.'))
q['captures'].append(dict(url=u,sha256='0df31b1c2ab049142d3453f1cc490ddf967ff63ac99f2dc23193fb2f74fb5eda',accessed_at='2026-11-21T20:58:25+00:00',state='source_records_draft'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
