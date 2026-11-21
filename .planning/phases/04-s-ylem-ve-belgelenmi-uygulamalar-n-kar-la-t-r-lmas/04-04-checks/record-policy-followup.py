import json
from pathlib import Path

p = Path('data/practices/04-yeni-parti-tranches.json')
q = json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21', query=s) for s in [
 '"Yeni Parti" "kanun teklifi" "2026" grup "kadın"',
 '"Yeni Parti" "TBMM" "kanun teklifi" eylül 2026 seçim',
 '"Yeni Parti" grup önerisi "kira" 2026 7 ağustos',
]]
items = [
 ('https://www.referandom.com/onergeler/barinma-krizinin-nedenleri-ve-sonuclari','db13f4aded14574e053d3c46aa5068bbc5cb5d7c1b01d7917182bff3ed2d5c98','2026-11-21T20:42:48.886541+00:00','Tarihi belirtilmeyen ikincil sayfa: 7 Ağustos 2026 grup önerisinin görüşülmesini reddedildi diye aktarıyor. Güncel sayfanın tarihsel sürümü bilinmiyor; temel araştırma önergesinin nihai sonucu ile grup önerisi oylaması farklıdır. Resmî tutanak takip edilecek.'),
 ('https://gazeteoksijen.com/turkiye/fon-kriziyle-ilgili-yeni-partiden-kanun-teklifi-zarar-sorumlularin-mal-varliklariyla-karsilansin-290188','b40111718d0ddebf351225fbbc4cb1803f30ce0ce72c8868c4ccc38e6340c021','2026-11-21T20:42:51.156503+00:00','21 Eylül haberinde parti sözcüsü fon tasfiyeleri hakkındaki teklifin o hafta sunulacağını söylüyor. Sunulma veya yasalaşma kaydı değildir; TBMM esas numarası ve sonraki işlem araştırılacak.'),
]
for url,digest,when,note in items:
 q['initial_readings'].append(dict(read_at='2026-11-21',url=url,section='Haber veya kaynak gövdesi',note=note))
 q['captures'].append(dict(url=url,sha256=digest,accessed_at=when,state='source_records_draft'))
q['candidate_leads'].append(dict(url='https://tbmm.gov.tr/Milletvekili/UyeGenelKurulKonusmalariDetay?eid=148101',state='read_capture_failed',note='TBMM 7 Ağustos 122. birleşiminde DEM Parti grubu adına konuşma ve Yeni Parti grup önerisi konusu web üzerinden okundu; doğrudan capture SSL record layer failure. Tam tutanak sayfasında içerik web aracında yüklenmedi; karar aslı aranacak.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
