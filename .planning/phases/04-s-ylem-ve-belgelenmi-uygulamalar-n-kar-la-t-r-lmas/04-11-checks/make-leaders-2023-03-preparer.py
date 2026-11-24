from pathlib import Path
p = Path(__file__).resolve().parent
original = (p/'prepare-village-2691.py').read_text()
prefix = original.split("assert party=='saadet'")[0].replace('village-2691-source-records.json','leaders-2023-03-source-records.json').replace('village-2691-reading-', 'leaders-2023-03-reading-').replace('2/2691 Genel Kurul konuşması ve oylaması özgün TBMM belgelerinden incelendi.','Toplantı planı ve gerçekleşmesine ilişkin özgün yayınlar okundu.').replace('2/2691 teklifinin Genel Kurul konuşması ve oylamasına ilişkin TBMM kaydı.','Altı liderin toplantı planı ve gerçekleşmesi.')
suffix = 'for entry in entries:' + original.split('for entry in entries:',1)[1]
suffix = suffix.replace('village-2691-draft.json','leaders-2023-03-draft.json').replace('village-2691-review-draft.json','leaders-2023-03-review-draft.json')
body = '''assert party=='saadet'
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='2dfb4420d680fa466e49d9877106c767cc2fe24e356f3347f71c32f8ff70fa3a'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='e4af2c40825f06179d8319824fd0c02a50b06d35157b6c5f5fbcb0ed93a88195'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(35,31,0)
topic='siyasal-ittifaklar'; stem='0411-saadet-six-leaders-2023'; src='0411-leaders-2023-03-'
statement,target,quote=(stem+s for s in ('-statement','-target','-quote'))
goal='Saadet Partisi Genel Başkanı Temel Karamollaoğlu, 6 Mart 2023 tarihinde partisinin ev sahipliğinde yeniden bir araya geleceklerini duyurdu.'
limit='3 Mart açıklaması ABC Gazetesinin Karamollaoğlu aktarımından okunmuştur. 6 Mart tarihli Independent Türkçe haberi aynı gün 21.24’te güncellenmiştir. Saadet yayımının API zaman damgası 12 Mart yerel gününü göstermektedir. Toplantı ve ortak aday duyurusu, seçilme veya politika uygulaması sonucu değildir.'
sp=[src+'statement-plan']; finding(target,goal,sp,'ABC Gazetesinin 3 Mart tarihli açıklama aktarımı.')
finding(quote,passages[sp[0]]['exact'],sp,'Karamollaoğlunun sonraki buluşma ifadesi.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2023-03-03',date_precision='day',version_id=passages[sp[0]]['version_id'],period_basis='3 Mart 2023 tarihli haberin Karamollaoğlu açıklaması aktarımı.',uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-scope-siyasal-ittifaklar-row'))
readings(topic,'statement',sp)
for kind,claim in [('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',passages[sp[0]]['exact'])]: task(kind,statement,claim,limit)
ep=[(src+'party-host','initiative','document','Saadet yayımı toplantının parti ev sahipliğinde yapıldığını bildiriyor.'),(src+'meeting-event','action','document','6 Mart tarihli haber altı liderin Saadet Genel Merkezindeki toplantısını aktarıyor.'),(src+'meeting-announcement','result','document','Habere göre Karamollaoğlu ortak cumhurbaşkanı adayını açıkladı.')]
context='Altı siyasi parti liderinin 6 Mart 2023 tarihinde Saadet Partisi Genel Merkezindeki toplantısı ve ortak aday açıklaması.'
eid=event(stem,'2023-03-06','Altı liderin Saadet Genel Merkezindeki toplantısı',context,ep,limit)
records['practice_event'][-1].update(common_event_key='six-leaders-2023-03-06-saadet-meeting',occurrence_basis='6 Mart tarihli Independent Türkçe haberi ve Saadet Partisinin yayımladığı açıklama, toplantıyı ve ortak aday duyurusunu belgeliyor.')
eids=[r[0] for r in ep]; scope=readings(topic,'event',eids); rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
observed='Altı lider 6 Martta Saadet Partisi Genel Merkezinde toplandı ve Karamollaoğlu ortak adayı açıkladı.'
compare='Karamollaoğlu 3 Martta 6 Mart için Saadet ev sahipliğinde buluşma duyurdu. Tarihli haber ve parti yayımı toplantının gerçekleştiğini belgeliyor.'
finding(result,observed,eids,'6 Mart tarihli haber ve Saadet Partisi yayımı.')
finding(explanation,compare+' '+limit,sp+eids,limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='3 Mart 2023 toplantı planı ve 6 Mart 2023 buluşması.',authority_context='Planı Saadet Genel Başkanı duyurdu. Altı liderin buluşmasına Saadet Partisi ev sahipliği yaptı.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(eids)))
for kind,claim in [('practice_relation',compare),('practice_relation.target_finding_id',goal),('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare)]: task(kind,rid,claim,limit)
'''
(p/'prepare-leaders-2023-03.py').write_text(prefix+body+suffix)
