import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json'); q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query='"10/4651" "iklim" "2026" meclis önergesi ilk imza'),dict(at='2026-11-21',query='"10/4651" "iklim krizinin" tarım işçileri')]
q['candidate_leads'].append(dict(url='https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/35ebbaef-ef4c-4f18-abcf-01a11b750c08',state='source_records_draft',note='TBMM 10/4651: Ayhan Barut ve 19 milletvekili 8 Ekim 2026 iklim krizinin tarım işçilerinin çalışma ve yaşam koşullarına etkileri için araştırma istedi. 21 Kasım özgün HTML SHA256 3df91b271b68b8ef783993db41eb229e70ff154ea3fbbc6546b3390ceb95e9cb; özet 0404-tbmm-iklim-tarim-4651-p. Talep komisyon veya fiili iklim uyumu sonucu değildir.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
