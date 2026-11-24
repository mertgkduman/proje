"""Append a bounded comparison; preserve the 33,000 TL unit ambiguity."""
from pathlib import Path
import sys

here=Path(sys.argv[1])
template=(here/'prepare-budget-1280.py').read_text()
prefix=template.split("assert party=='saadet'",1)[0].replace('budget-1280','minimum-wage-2026')
prefix=prefix.replace('Partiler arası temas duyurusu ve iki görüşmenin tarihli açıklamaları okundu.','2026 asgari ücret açıklaması ve ilgili komisyon duyurusu incelendi.')
prefix=prefix.replace('Ocak 2026 partiler arası temas duyurusu veya tarihli görüşme kaydı.','2026 asgari ücret talebi veya bakanlık kararı.')
exec(prefix)
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='b0d8265f71e2d970df440af9f2c9314d9ec9dcc5e2cd5c099b20d2b1c40f9e4b'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='e704061ce32e4b4c5f1b17c683ac82d7f3254a3077d4d3a7a14339573d3262da'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(27,23,0)
topic='asgari-ucret'; stem='0411-saadet-minimum-wage-2026'; sp=['0411-wage-2026-demand']; ep=['0411-wage-2026-official-net-brut']
statement,target,quote=(stem+s for s in ('-statement','-target','-quote'))
goal='Mahmut Arıkan 2026 asgari ücretinin en az yüzde 50 zamla 33.000 TL olmasını istedi.'
limit=('Talepte net veya brüt açıkça belirtilmemiştir. Komisyonu Saadet Partisi yönetmemiştir; talep ile karar arasında etki veya nedensellik gösterilmemiştir. Bakanlığın tutarları belirlenen ücrettir, tüm fiilî ödemeleri kanıtlamaz.')
finding(target,goal,sp,'22 Ekim parti açıklaması ve 23 Ekim imzalı haber okundu.')
finding(quote,passages[sp[0]]['exact'],sp,'İmzalı haberdeki birebir pasaj.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2025-10-22',date_precision='day',version_id=passages[sp[0]]['version_id'],period_basis='Parti API metninde 22 Ekim grup konuşması; haber 23 Ekimde yayımlandı.',uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-asgari-ucret'))
readings(topic,'statement',sp)
for kind,claim in [('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',passages[sp[0]]['exact'])]: task(kind,statement,claim,limit)
eid=event(stem,'2025-12-23','2026 asgari ücretinin belirlenmesi','Asgari Ücret Tespit Komisyonu 2026 için ücret belirledi; ÇSGB 23 Aralıkta net ve brüt tutarları açıkladı.',[(ep[0],'result','document','Bakanlık 2026 ücretini net 28.075,50 ve brüt 33.030 TL olarak duyurdu.')],limit)
records['practice_event'][-1].update(common_event_key='turkiye-minimum-wage-commission-2026-decision-2025-1',occurrence_basis='ÇSGB 23 Aralık duyurusu; yürürlük 1 Ocak 2026.')
scope=readings(topic,'event',ep); rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
observed='23 Aralıkta 2026 için 1 Ocaktan geçerli aylık net 28.075,50 TL ve brüt 33.030 TL duyuruldu.'
compare=('Talep ve karar 2026 asgari ücretiyle ilgilidir. Talebin net veya brüt niteliği açık olmadığından 33.000 TL eşiğinin karşılandığı kesin söylenemez. Talep net ise açıklanan net ücret 4.924,50 TL altındadır; 33.030 TL ise brüttür.')
finding(result,observed,ep,'ÇSGB tutarları ve yürürlük başlangıcı.')
finding(explanation,compare+' '+limit,sp+ep,limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='22 Ekim 2025 talebi, 23 Aralık 2025 komisyon kararı; yürürlük 1 Ocak 2026.',authority_context='Arıkan Saadet genel başkanı olarak talepte bulundu; ücretin tespiti Asgari Ücret Tespit Komisyonunun görevidir. Parti yetkisi veya nedensellik iddia edilmez.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(ep)))
for kind,claim in [('practice_relation',compare),('practice_relation.target_finding_id',goal),('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare)]: task(kind,rid,claim,limit)
tail=template.split('for entry in entries:',1)[1]
exec('for entry in entries:'+tail.replace('budget-1280','minimum-wage-2026'))
