import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "2026" "kadın" "meclis araştırması" şiddet','"Yeni Parti" "2026" "engelli" "kanun teklifi" TBMM','"Yeni Parti" "2026" "orman yangınları" grup önerisi kabul edilmedi','"Yeni Parti" "2026" "genç işsizlik" araştırma önergesi']]
q['candidate_leads'] += [
 dict(url='https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/da56f7fb-b6de-4318-aa4e-01a1786d5869',state='read_unbound',note='TBMM 10/4875: 23 Ekim nüfus politikalarının kadın hakları, toplumsal cinsiyet eşitliği ve sosyal refah bakımından araştırılması talebi; ilk imza Kayıhan Pala ve 24 milletvekili. Özgün bayt ve kesim tarihindeki işlem ayrıca incelenmeli; araştırma talebi kabul edilmiş politika değildir.'),
 dict(url='https://www.tbmm.gov.tr/Milletvekili/UyeGenelKurulKonusmalariDetay?eid=147857',state='read_unbound',note='TBMM 5 Ağustos 120. birleşimde başka parti adına orman yangınları konulu Yeni Parti grup önerisi hakkında konuşma gösteriyor. Yeni Parti önerisi, oylanan işlemin kapsamı ve gerçek sonuç özgün tam tutanaktan ayrı okunmalı; tek konuşmadan sonuç çıkarılmaz.'),
 dict(url='https://tbmm.gov.tr/milletvekili/UyeMeclisArastirmaOnergeleri?Id=f72877c2-d9e0-037b-e050-007f01005610&ortakDonemId=134155f0-c3d6-4d24-893b-f3a2ef695ae7',state='read_partial_unbound',note='TBMM listesinde görülen 9 Mart 2026 10/3918 kadın istihdamı önergesi kuruluş öncesidir; sayfanın güncel parti etiketiyle geçmişte Yeni Partiye atfedilmez. Kesim içi uygun teklifler ayrı aranır.'),
]
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
