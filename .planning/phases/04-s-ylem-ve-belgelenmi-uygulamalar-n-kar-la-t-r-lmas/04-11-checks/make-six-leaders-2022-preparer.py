from pathlib import Path
p=Path(__file__).resolve().parent
original=(p/'prepare-village-2691.py').read_text()
prefix=original.split("assert party=='saadet'")[0].replace('village-2691-source-records.json','six-leaders-2022-source-records.json').replace('village-2691-reading-', 'six-leaders-2022-reading-').replace('2/2691 Genel Kurul konuşması ve oylaması özgün TBMM belgelerinden incelendi.','Altı lider ortak açıklaması ve sonraki toplantı haberi okundu.').replace('2/2691 teklifinin Genel Kurul konuşması ve oylamasına ilişkin TBMM kaydı.','Altı liderin toplantı planı ve gerçekleşmesi.')
suffix="for entry in entries:"+original.split("for entry in entries:",1)[1]
suffix=suffix.replace('village-2691-draft.json','six-leaders-2022-draft.json').replace('village-2691-review-draft.json','six-leaders-2022-review-draft.json')
body='''assert party=='saadet'
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='7f78c4fbe5248d6513beb56dd9d4298d98995737d3d773abf8cd14da27848da8'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='edce38a01ac2411f44ac8e531894c84c8a0e3de731e3df9be95f398c8f23fbd8'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(33,29,0)
topic='siyasal-ittifaklar'; stem='0411-saadet-six-leaders-2022'; src='0411-six-leaders-2022-'
statement,target,quote=(stem+s for s in ('-statement','-target','-quote'))
goal='Saadet ev sahipliğindeki 21 Ağustos 2022 toplantısının ortak açıklamasında altı lider, 2 Ekimde CHP Genel Merkezinde yeniden buluşacaklarını duyurdu.'
limit='21 Ağustosta ev sahibi Saadet, 2 Ekimde ev sahibi CHPdir; açıklama altı liderin ortaktır. Gazete, Karamollaoğlunun 13.59da geldiğini ve toplantının 14.11de başladığını bildirir; açıklamadaki 14.00 planlanan saattir. 2 Ekim 364 katalog gövdesinin slugı 29 Mayıs 332 kaydına döndüğü için 364 okunmuş sayılmadı. Toplantının gerçekleşmesi ortak politika hedeflerinin uygulanması veya seçim sonucunun doğrulanması değildir.'
sp=[src+'statement-date',src+'statement-host',src+'statement-next']; finding(target,goal,sp,'Saadet yayımındaki tarihli altı lider ortak açıklaması.')
finding(quote,passages[sp[2]]['exact'],[sp[2]],'Açıklamadaki bir sonraki toplantı yer ve saat ifadesi.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2022-08-21',date_precision='day',version_id=passages[sp[2]]['version_id'],period_basis='Saadet sitesindeki 21 Ağustos tarihli altı lider ortak açıklaması.',uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-scope-siyasal-ittifaklar-row'))
readings(topic,'statement',sp)
for kind,claim in [('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',passages[sp[2]]['exact'])]: task(kind,statement,claim,limit)
ep=[(src+'meeting-arrival','action','document','Habere göre Saadet Genel Başkanı Karamollaoğlu, DP Genel Başkanı Uysal ve İYİ Parti Genel Başkanı Akşener CHP Genel Merkezine geldi.'),(src+'meeting-opening','action','document','Independent Türkçe haberine göre CHP Genel Merkezindeki görüşme saat 14.11de başladı.'),(src+'meeting-joint','result','document','Habere göre toplantı sonrasında altı liderin ortak bildirisi yayımlandı.')]
context='Altı siyasi parti liderinin 2 Ekim 2022 tarihinde CHP Genel Merkezindeki ikinci tur ilk toplantısı.'
eid=event(stem,'2022-10-02','Altı liderin CHP Genel Merkezindeki ikinci tur ilk toplantısı',context,ep,limit)
records['practice_event'][-1].update(common_event_key='six-leaders-2022-10-02-chp-second-round-meeting',occurrence_basis='2 Ekim 2022’de CHP’nin ev sahipliğinde yapılan ikinci turun ilk toplantısını 2 Ekim ortak açıklaması ve Independent Türkçe’nin tarihli haberi belgeliyor. Katılımcılar arasında Temel Karamollaoğlu, Gültekin Uysal ve Meral Akşener vardı.')
eids=[r[0] for r in ep]; scope=readings(topic,'event',eids); rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
observed='Altı lider 2 Ekimde CHP Genel Merkezinde toplandı; Karamollaoğlu katıldı ve altı liderin ortak açıklaması yayımlandı.'
compare='21 Ağustos ortak açıklaması sonraki toplantıyı 2 Ekimde CHP Genel Merkezinde duyurdu; haber aynı gün ve yerde altı liderin buluştuğunu bildiriyor.'
finding(result,observed,eids,'Independent Türkçe / ANKA toplantı haberi.')
finding(explanation,compare+' '+limit,sp+eids,limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='21 Ağustos 2022 ortak planı ve 2 Ekim 2022 ikinci tur ilk toplantısı.',authority_context='Altı genel başkan ortak plan açıkladı; Saadet 21 Ağustosta, CHP 2 Ekimde ev sahibiydi.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(eids)))
for kind,claim in [('practice_relation',compare),('practice_relation.target_finding_id',goal),('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare)]: task(kind,rid,claim,limit)
'''
(p/'prepare-six-leaders-2022.py').write_text(prefix+body+suffix)
