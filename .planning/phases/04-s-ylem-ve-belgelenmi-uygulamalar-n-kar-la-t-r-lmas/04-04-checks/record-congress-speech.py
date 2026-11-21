import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
q['queries'] += [dict(at='2026-11-21',query=s) for s in ['"Yeni Parti" "2026" "hesap" "denetim" parti mali','"Yeni Parti" "2026" "kongre" "söz hakkı" "tüzük"','"Yeni Parti" "2026" "aidat" üyelik','"Yeni Parti" "2026" "temel yurttaşlık geliri" teklifi']]
for lead in q['candidate_leads']:
    if lead['url']=='https://samsunilkhaber.com.tr/yeni-parti-samsun-il-kongresinde-tuzuk-tartismasi':
        lead['state']='source_records_draft'
        lead['note']+=' Üye talebi ve divan yanıtını birlikte kapsayan 0404-samsun-kongre-soz-p pasajı özgün SHA256 4b918f9bb18fc0e9dd14906f11a8e6886d83b3c02d009fe462ce6c41e8108a61 üzerine bağlandı.'
q['candidate_leads'].append(dict(url='https://www.yeniankara.com.tr/yeni-parti/yeni-partinin-ilk-kurultayi-ankarada-ozgur-ozelin-aciklamalari-ve-tum-gelismeler-canli-190136',state='outside_cutoff_lead',note='14 Kasım kurultayında sunulduğu bildirilen mali tablo daha önceki dönemi kapsasa da kamuya sunum ve haber kesimden sonradır; kesim içinde mevcut kanıt gibi kullanılmaz.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
