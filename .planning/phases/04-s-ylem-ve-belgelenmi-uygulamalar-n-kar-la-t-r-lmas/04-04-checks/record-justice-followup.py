import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "ek görüş" "9 Ağustos 2026" "adalet komisyonu" teklif','"Süleyman Bülbül" "Atakan Ünver" "Cumhur Uzun" "ek görüş" 2026 teklif','"Yeni Parti" "2026" "yargı bağımsızlığı" "meclis" komisyon','"Yeni Parti" "2026" "temel vatandaşlık geliri" teklif']]
q['candidate_leads'].append(dict(url='https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/7bc94634-26a4-4c0c-99b4-01a1abfb1424',state='read_unbound',note='TBMM 10/4984 araştırma önergesi, 4 Kasım 2026, ilk imza Mehmet Tahtasız ve 20 milletvekili: hukuk devleti, yargı bağımsızlığı ve çalışanların temel hakları hakkında araştırma talebi. Bu 30 Eylül 10/4551 ayrı önergesinden farklıdır; özgün bayt, gerekçe ve kesim anındaki işlem ayrı araştırılır. Teklif edilmiş araştırma kabul veya uygulama değildir.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
