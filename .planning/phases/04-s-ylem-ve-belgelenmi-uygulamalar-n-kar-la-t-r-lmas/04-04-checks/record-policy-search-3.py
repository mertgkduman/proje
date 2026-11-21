import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "2026" "Avrupa Birliği" "milletvekili" meclis','"Yeni Parti" "2026" "yenilenebilir enerji" "kanun teklifi"','"Yeni Parti" "2026" "yargı bağımsızlığı" "kanun teklifi"','"Yeni Parti" "2026" "yurttaşlık geliri" TBMM']]
q['candidate_leads'] += [
 dict(url='https://www.tbmm.gov.tr/Haber/Detay?Id=0b3aae58-965a-4323-8ef1-01a136f8ee67',state='read_unbound',note='13 Ekim TBMM haberine göre Yüksel Taşkın AB Uyum Komisyonu başkanvekili seçildi; bu görev seçimi tek başına AB politikası uygulaması değildir. Özgün arşiv ve toplantıda kendi beyanları ayrıca takip edilmeli.'),
 dict(url='https://www.numedya24.tv/yeni-partiden-cerceve-yasa-icin-ek-gorus/',state='read_unbound',note='9 Ağustos haberinde Yeni Parti Adalet Komisyonu üyelerinin çerçeve teklifine ek görüşü ve yargı bağımsızlığı dahil önerileri aktarılıyor; doğrudan teklif/komisyon metni, aşama ve atıf araştırılmalı.'),
 dict(url='https://tbmm.gov.tr/Haber/enerjiye-ve-sosyal-guvenlige-iliski-20261118153951',state='outside_cutoff_lead',note='TBMM 18 Kasım komisyon haberinde Yeni Parti milletvekili usul değerlendirmesi ve önergesi var; 10 Kasım kesiminden sonra.'),
]
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
