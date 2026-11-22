import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['candidate_leads'].append(dict(url='https://api.yeni-parti.org.tr/uploads/yayinlar/yayin-1794902310469-811605043.pdf',state='source_records_draft',note='Erişilen PDF özgün bayt SHA256 a46c73ade5a7800e3df4a4c3baafc5d4e8d14e077964652cbdda1b6a7c9d0bf0; XMP dönüşümü 16 Kasım 2026, yayın tarihi bilinmiyor. İndeks 137/basılı 138 Geçici Madde 6, 9 Kasım Kurucular Kurulu kararına atıfla 160 asıl ve 30 yedek yazıyor. 9 Kasım haber ve açıklamadaki 150/30 anlatımıyla farklılık açık; kesim sonrası üretilen sürümün aynı ifadesinin kesimde yürürlükte olduğu varsayılamaz. Kesim öncesi karar aslı ve olası sonraki değişiklik izlenmeli.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
