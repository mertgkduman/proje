from pathlib import Path

p=Path(__file__).resolve().parent
original=(p/'prepare-village-2691.py').read_text()
prefix=original.split("assert party=='saadet'")[0].replace('village-2691-source-records.json','agriculture-2025-source-records.json').replace('village-2691-reading-', 'agriculture-2025-reading-').replace('2/2691 Genel Kurul konuşması ve oylaması özgün TBMM belgelerinden incelendi.','Parti açıklaması ve kurumların tarım sayımı belgeleri incelendi.').replace('2/2691 teklifinin Genel Kurul konuşması ve oylamasına ilişkin TBMM kaydı.','Tarım sayımı açıklaması ve kurumsal kayıt.')
suffix="for entry in entries:"+original.split("for entry in entries:",1)[1]
suffix=suffix.replace('village-2691-draft.json','agriculture-2025-draft.json').replace('village-2691-review-draft.json','agriculture-2025-review-draft.json')
body='''assert party=='saadet'
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='b2654e0d49a257a68b0b3da7bd73be327a221a9469e6fd65ce4915d8824d0771'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='584745fa96f553464802964ca44de84fdc519dfec26c65fbc1187fe6f69c2d21'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(32,28,0)
topic='tarim-hayvancilik'; stem='0411-saadet-agriculture-2025'; src='0411-agriculture-2025-'
statement,target,quote=(stem+s for s in ('-statement','-target','-quote'))
goal='Saadet Partisi Antalya Milletvekili Şerafettin Kılıç 8 Kasım 2024te yeni bir tarım sayımının ivedilikle yapılması çağrısında bulundu.'
limit='Kılıçın açıklaması parti kaynağındaki basın toplantısıdır; bir kurumsal karar veya sayımı yürütme yetkisi değildir. Sayımın çağrı nedeniyle başlatıldığına ilişkin kanıt yoktur. TÜİK genelgesinin yayım günü bilinmiyor. Veri derleme süresinin uzatılması sayım sonuçlarının yayımlandığını göstermez.'
sp=[src+'party-identity',src+'party-call']; finding(target,goal,sp,'Saadet Partisi API özgün gövdesindeki Kılıç açıklaması.')
finding(quote,passages[sp[1]]['exact'],[sp[1]],'Açıklamadaki tarım sayımı çağrısı.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2024-11-08',date_precision='day',version_id=passages[sp[1]]['version_id'],period_basis='Parti API yayım günlü basın toplantısı haberi.',uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-tarim-hayvancilik'))
readings(topic,'statement',sp)
for kind,claim in [('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',passages[sp[1]]['exact'])]: task(kind,statement,claim,limit)
ep=[(src+'ministry-start','action','document','Bakanlık sayımın 1 Temmuz 2025te başladığını bildirdi.'),(src+'circular3-extension','result','document','TÜİK 3 numaralı genelgeyle veri derleme süresini 30 Ocak 2026ya uzattı.')]
eid=event(stem,'2025-07-01','2025 Genel Tarım Sayımının başlaması','Bakanlık ve TÜİK işbirliğindeki sayım 1 Temmuz 2025te başladı; veri derleme süresi 30 Ocak 2026ya uzatıldı.',ep,limit)
records['practice_event'][-1].update(common_event_key='tuik-2025-genel-tarim-sayimi-baslangic',occurrence_basis='Bakanlığın 2 Eylül 2025 duyurusu ve TÜİK 3 numaralı genelgesi.')
eids=[r[0] for r in ep]; scope=readings(topic,'event',eids); rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
observed='2025 Genel Tarım Sayımı 1 Temmuz 2025te başladı; TÜİK veri derleme süresini 30 Ocak 2026ya uzattı.'
compare='Kılıcın yeni tarım sayımı çağrısı ile Bakanlık ve TÜİKin sonraki genel tarım sayımı aynı genel sayım konusundadır.'
finding(result,observed,eids,'Bakanlık duyurusu ve TÜİK genelgesi.')
finding(explanation,compare+' '+limit,sp+eids,limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='8 Kasım 2024 açıklamasını 1 Temmuz 2025 sayım başlangıcı izledi.',authority_context='Kılıç Saadet milletvekili olarak çağrı yaptı; sayım Bakanlık ve TÜİK tarafından yürütüldü.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(eids)))
for kind,claim in [('practice_relation',compare),('practice_relation.target_finding_id',goal),('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare)]: task(kind,rid,claim,limit)
'''
(p/'prepare-agriculture-2025.py').write_text(prefix+body+suffix)
