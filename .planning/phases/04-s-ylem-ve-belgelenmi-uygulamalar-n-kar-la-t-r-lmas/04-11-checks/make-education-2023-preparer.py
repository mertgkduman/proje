from pathlib import Path
p=Path(__file__).resolve().parent
original=(p/'prepare-village-2691.py').read_text()
prefix=original.split("assert party=='saadet'")[0].replace('village-2691-source-records.json','education-2023-source-records.json').replace('village-2691-reading-','education-2023-reading-').replace('2/2691 Genel Kurul konuşması ve oylaması özgün TBMM belgelerinden incelendi.','Parti açıklaması ve YÖK yazısı incelendi.').replace('2/2691 teklifinin Genel Kurul konuşması ve oylamasına ilişkin TBMM kaydı.','Yüz yüze eğitim çağrısı ve YÖK kararı.')
suffix='for entry in entries:'+original.split('for entry in entries:',1)[1]
suffix=suffix.replace('village-2691-draft.json','education-2023-draft.json').replace('village-2691-review-draft.json','education-2023-review-draft.json')
body='''assert party=='saadet'
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='1ffba5e74656068953dd6157a87dd0d212a4ed7e471ac9b1bb9072aa8570d161'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='6680c0291b2048552e28a9762d31b60bb10bdf1d31a2b51b978ed76b3566ef16'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(36,32,0)
topic='yuksekogretim'; stem='0411-saadet-education-2023'; src='0411-education-2023-'
statement,target,quote=(stem+s for s in ('-statement','-target','-quote'))
goal='Saadet Partisi Genel Başkanı Temel Karamollaoğlu, üniversitelerin derhal yüz yüze eğitime başlamasını istedi.'
limit='22 Şubat çağrısı derhal yüz yüze eğitim istiyordu. 30 Mart YÖK kararı uzaktan öğretimi sürdürürken 3 Nisan’dan itibaren isteyenler için yüz yüze seçenek tanıdı. Üniversitelerin fiilî uygulaması ve öğrenci katılımı bu yazıyla doğrulanmıyor. Kararın Saadet çağrısı nedeniyle alındığı gösterilmiyor.'
sp=[src+'statement-call']; finding(target,goal,sp,'Saadet Partisi yayımındaki genel başkan açıklaması.')
finding(quote,passages[sp[0]]['exact'],sp,'Karamollaoğlunun yüz yüze eğitim çağrısı.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2023-02-22',date_precision='day',version_id=passages[sp[0]]['version_id'],period_basis='Parti API yayım damgasının Türkiye yerel günü 22 Şubat 2023.',uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-yuksekogretim'))
readings(topic,'statement',sp)
for kind,claim in [('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',passages[sp[0]]['exact'])]: task(kind,statement,claim,limit)
ep=[(src+'yok-decision','action','document','Yükseköğretim Genel Kurulu 30 Mart’ta değerlendirme yaptı.'),(src+'yok-effective','result','document','YÖK yazısına göre seçenek 3 Nisan’dan itibaren uygulanabilir.'),(src+'yok-choice','result','document','Uzaktan öğretim sürerken isteyenlere devam şartı olmadan yüz yüze eğitim seçeneği tanındı.'),(src+'yok-university','result','document','İlgili düzenlemeler üniversitelerin yetkili kurullarına bırakıldı.')]
context='30 Mart 2023 YÖK kararıyla bahar döneminde uzaktan öğretimin yanında yüz yüze eğitim seçeneği.'
eid=event(stem,'2023-03-30','YÖK’ün 2023 bahar dönemi için yüz yüze öğretim seçeneği kararı',context,ep,limit)
records['practice_event'][-1].update(common_event_key='yok-2023-03-30-bahar-yuzyuze-secenegi',occurrence_basis='31 Mart tarihli YÖK yazısının TBMM 7/193 cevabındaki tarihli eki.')
eids=[r[0] for r in ep]; scope=readings(topic,'event',eids); rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
observed='YÖK 30 Mart’ta uzaktan öğretim sürerken isteyenler için 3 Nisan’dan itibaren yüz yüze seçenek tanıdı.'
compare='22 Şubat’ta istenen derhal yüz yüze eğitimin ardından YÖK 30 Mart’ta uzaktan öğretimin yanında isteğe bağlı yüz yüze seçenek kararı aldı.'
finding(result,observed,eids,'TBMM 7/193 cevabındaki 31 Mart tarihli YÖK yazısı.')
finding(explanation,compare+' '+limit,sp+eids,limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='22 Şubat 2023 çağrısı, 30 Mart YÖK kararı ve 3 Nisan seçenek başlangıcı.',authority_context='Çağrı Saadet Genel Başkanına, karar Yükseköğretim Genel Kuruluna aittir.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(eids)))
for kind,claim in [('practice_relation',compare),('practice_relation.target_finding_id',goal),('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare)]: task(kind,rid,claim,limit)
'''
(p/'prepare-education-2023.py').write_text(prefix+body+suffix)
