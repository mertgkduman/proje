from pathlib import Path
p=Path(__file__).resolve().parent
original=(p/'prepare-village-2691.py').read_text()
prefix=original.split("assert party=='saadet'")[0].replace('village-2691-source-records.json','election-2023-source-records.json').replace('village-2691-reading-','election-2023-reading-').replace('2/2691 Genel Kurul konuşması ve oylaması özgün TBMM belgelerinden incelendi.','Parti çağrısı, seçim kararı ve TBMM tutanağı incelendi.').replace('2/2691 teklifinin Genel Kurul konuşması ve oylamasına ilişkin TBMM kaydı.','Seçim çağrısı ve sonraki seçim işlemleri.')
suffix='for entry in entries:'+original.split('for entry in entries:',1)[1]
suffix=suffix.replace('village-2691-draft.json','election-2023-draft.json').replace('village-2691-review-draft.json','election-2023-review-draft.json')
body='''assert party=='saadet'
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='4dc52f051576cdc4f2eab0bec4361569eb3e172572757e655c5c852f86b6e74f'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='cd17be98c22acb24f1ed778e3d4869a31bd661c96524ef6a4718a80fbcb15f31'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(37,33,0)
topic='secim-siyasi-partiler'; stem='0411-saadet-election-2023'; src='0411-election-2023-'
statement,target,quote=(stem+s for s in ('-statement','-target','-quote'))
goal='Saadet Partisi Genel Başkanı Temel Karamollaoğlu, 18 Ocak 2023’te seçim kararının o gün alınmasını ve en geç iki ay içinde seçime gidilmesini istedi.'
limit='18 Ocak’tan iki takvim ayı sonrası 18 Mart’tır. Yenileme kararı çağrıdan 51 gün sonra, oy verme ise 116 gün sonra gerçekleşti. 10 Mart kararından 14 Mayıs oy verme gününe 65 gün geçti. Cumhurbaşkanının yenileme kararı ve YSK’nın gün belirleme yetkisi ayrıdır. Çağrının karar üzerinde etkisi gösterilmiyor.'
sp=[src+'statement-call'];finding(target,goal,sp,'Parti yayımındaki genel başkan açıklaması.');finding(quote,passages[sp[0]]['exact'],sp,'Karamollaoğlunun seçim çağrısı.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2023-01-18',date_precision='day',version_id=passages[sp[0]]['version_id'],period_basis='Parti API yayım damgasının Türkiye yerel günü 18 Ocak 2023.',uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-secim-siyasi-partiler'))
readings(topic,'statement',sp)
for kind,claim in [('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',passages[sp[0]]['exact'])]: task(kind,statement,claim,limit)
ep=[(src+'ysk-renew','initiative','document','Cumhurbaşkanı 10 Mart’ta seçimlerin yenilenmesine karar verdi.'),(src+'ysk-day','action','document','YSK 10 Mart’ta oy verme gününü 14 Mayıs olarak belirledi.'),(src+'floor-parliament','result','document','TBMM tutanağı milletvekili seçiminin 14 Mayıs’ta yapıldığını kaydediyor.'),(src+'floor-president','result','document','TBMM tutanağı cumhurbaşkanı seçiminin ilk turunun 14 Mayıs’ta yapıldığını kaydediyor.')]
context='10 Mart 2023 seçim yenileme kararı, YSK’nın oy verme günü kararı ve 14 Mayıs 2023 seçimleri.'
eid=event(stem,'2023-03-10','2023 seçimlerinin yenilenmesi ve oy verme günü',context,ep,limit)
records['practice_event'][-1].update(common_event_key='turkiye-2023-03-10-secim-yenileme',occurrence_basis='10 Mart YSK kararı seçim yenileme ve oy verme gününü, TBMM ilk birleşim tutanağı 14 Mayıs seçimlerini belgeliyor.')
eids=[r[0] for r in ep];scope=readings(topic,'event',eids);rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
observed='Cumhurbaşkanı seçimleri 10 Mart’ta yeniledi. YSK oy verme gününü 14 Mayıs olarak belirledi ve seçimler o gün yapıldı.'
compare='18 Ocak çağrısında aynı gün karar ve iki ay içinde seçim istendi. Yenileme kararı 10 Mart’ta, oy verme 14 Mayıs’ta gerçekleşti.'
finding(result,observed,eids,'10 Mart YSK kararı ve TBMM ilk birleşim tutanağı.');finding(explanation,compare+' '+limit,sp+eids,limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='18 Ocak çağrısı, 10 Mart yenileme kararı ve 14 Mayıs ilk oy verme günü.',authority_context='Çağrı Saadet Genel Başkanına, yenileme kararı Cumhurbaşkanına ve oy verme gününün belirlenmesi YSK’ya aittir.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(eids)))
for kind,claim in [('practice_relation',compare),('practice_relation.target_finding_id',goal),('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare)]:task(kind,rid,claim,limit)
'''
(p/'prepare-election-2023.py').write_text(prefix+body+suffix)
