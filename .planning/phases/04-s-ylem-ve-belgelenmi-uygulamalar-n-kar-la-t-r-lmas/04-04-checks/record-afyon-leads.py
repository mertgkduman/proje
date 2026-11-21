import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json')
q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" Afyon "18 Ekim 2026" ön seçim il başkanı','"Yeni Parti" Afyon "25 Ekim 2026" kongre il başkanı seçim','"Yeni Parti" Afyon 2026 il ön seçim sonuçlar kongre','"10/4445" "29.07.2026" "meslek hastalıkları"','"10/4445" "meslek hastalıkları" "Yeni Parti"','"2/3866" "Şeref Arpacı" teklif 2026']]
q['candidate_leads'] += [
 dict(url='https://afyonsehir.com/yeni-parti-il-kongresi-25-ekim-pazar-gunu/',state='source_records_draft',note='19 Ekim Afyon Şehir haberi il ön seçiminde Faruk Duha Erhan’ın birinci olduğunu, 25 Ekim kongresini ise henüz plan olarak bildiriyor. Pasaj 0404-afyon-onsecim-sehir-p, özgün bayt SHA256 59f22050ff1944df63a466fb9ba6bd1f3e7fbf4f2324fbafad41d6bb639064b8. Kongrenin fiilî sonucu ayrı araştırılacak.'),
 dict(url='https://www.afyonpostasi.com.tr/yeni-parti-afyonda-hangi-ilceden-hangi-adaya-kac-oy-cikti-iste-net-sonuclar',state='read_unbound',note='19 Ekim Afyon Postası ilçe bazlı ön seçim haberinde Faruk Duha Erhan ve Hasan Karadeniz adları ve ilçe oyları mevcut; özgün bayt ve tüm tablo ayrıca incelenecek.'),
 dict(url='https://www.afyonpostasi.com.tr/yeni-partinin-afyondaki-yonetimi-belli-oldu-iste-79-kisilik-tam-liste',state='read_unbound',note='25 Ekim 12.53 haberi kongre öncesi tek listeyi bildiriyor; fiilî kongre oylaması veya seçimin gerçekleşmesi olarak sunulamaz.'),
 dict(url='https://api.yeni-parti.org.tr/uploads/yayinlar/yayin-1794902310469-811605043.pdf',state='read_partial_unbound',note='16 Kasım tarihli tüzük PDF arama sonucu bazı hükümlerde 9 Kasım kurucular kurulu değişiklik notu gösteriyor. Yayın kesimden sonra; 10 Kasım kesimindeki tam yürürlük metni ve sonraki değişikliklerden ayrım araştırılmadan geçmişe uygulanmaz.'),
 dict(url='https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/2b8512b1-652e-4c99-b67a-01a1207db7cd',state='lead_unread',note='Vekilpedia 10/4676 için TBMM bağlantısı veriyor; web açma aracı erişemedi. 9 Ekim meslek hastalıkları önergesi ile 29 Temmuz 10/4445 ayrı kayıtlardır, TBMM ve özgün metin doğrudan okunacak.'),
]
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
