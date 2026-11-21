import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "Edirne" "8 Kasım" "genel başkan" "ön seçim" 2026','"Yeni Parti" "Eskişehir" "8 Kasım" "genel başkan" "ön seçim" 2026','"Yeni Parti" "Edirne" "Eskişehir" "genel başkanlık" 8 kasım önseçim']]
items=[
 ('https://hudutgazetesi.com/siyaset/98lik-demokrasi-cinari/','700c536e9c8c0ba0ed50b98d1eb4568fac610099a413cd79f66cd90b2da097d7','2026-11-21T21:03:18.874789+00:00','Olgay Güler, 8 Kasım 15:43: Edirne merkez AKM genel başkan adaylığı ön seçimi sandık ve oy kullanan üye haberi. Yerel sandık ulusal 81 il olayıyla örtüşür, ona ayrıca toplanmaz; haber ulusal sonuç veya kurultay kararı değildir.'),
 ('https://siyasetakademi.com/haber/yeni-parti-il-baskani-yalaz-genel-baskanimizin-sonuna-kadar-yanindayiz','68f50c0b70340b3305e52c98bf0de9ef3531bf5016964ca4d5ddfc4f70e0f18f','2026-11-21T21:03:21.096280+00:00','8 Kasım 10:12, Siyaset Akademi Eskişehir Haber Ajansına atıfla Eskişehir ön seçim başlangıcı, 11.645 oy hakkı bulunan üye ve 39 sandık bildiriyor; sayı kullanılan oy veya ulusal toplam değildir.'),
]
for url,digest,when,note in items:
 q['initial_readings'].append(dict(read_at='2026-11-21',url=url,section='8 Kasım yerel genel başkan ön seçimi haberi',note=note));q['captures'].append(dict(url=url,sha256=digest,accessed_at=when,state='source_records_draft'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
