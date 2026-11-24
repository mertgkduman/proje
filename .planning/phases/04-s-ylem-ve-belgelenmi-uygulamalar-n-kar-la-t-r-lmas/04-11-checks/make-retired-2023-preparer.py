from pathlib import Path

p = Path(__file__).resolve().parent
template = (p / 'prepare-six-leaders-2022.py').read_text()
prefix = template.split("assert party=='saadet'")[0]
prefix = (prefix.replace('six-leaders-2022-source-records.json', 'retired-2023-source-records.json')
          .replace('six-leaders-2022-reading-', 'retired-2023-reading-')
          .replace('Altı lider ortak açıklaması ve sonraki toplantı haberi okundu.', 'Emekli ödemesi hakkındaki konuşma, kanunlar ve SGK raporu okundu.')
          .replace('Altı liderin toplantı planı ve gerçekleşmesi.', 'Emekli ödemesinin kapsamı ve değişikliği.'))
suffix = 'for entry in entries:' + template.split('for entry in entries:', 1)[1]
suffix = suffix.replace('six-leaders-2022-draft.json', 'retired-2023-draft.json').replace('six-leaders-2022-review-draft.json', 'retired-2023-review-draft.json')
body = '''assert party=='saadet'
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='e273528bd5104b6556ea60bb028ccc95d61ac7d3a7376907eaf7334d31f580c2'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='d37c4bd2ecbaf6c82c856adcb9e9b20f706ff4d87d0be384ef463ea08d649d23'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(34,30,0)
topic='sosyal-guvenlik'
stem='0411-saadet-retired-2023'
src='0411-retired-2023-'
statement,target,quote=(stem+s for s in ('-statement','-target','-quote'))
goal='Saadet Partisi Genel Başkanı Temel Karamollaoğlu, çalışmayan emeklilerle sınırlı tek seferlik 5.000 TL ödemeyi kabul etmediklerini açıkladı.'
limit='İlk kanunda ölüm geliri veya aylığı alanlar için ayrı istisna vardı. Kapsamın genişlemesi, tek seferlik ödeme tutarına ilişkin eleştirinin karşılandığı anlamına gelmez. SGK verisi toplu ödeme verisidir. Bu kaynaklar Saadet Partisinin değişikliğe neden olduğunu göstermez.'
sp=[src+'speech-quote',src+'speech-role']
finding(target,goal,sp,'Parti yayımında konuşmacı ve ödeme değerlendirmesi okundu.')
finding(quote,passages[sp[0]]['exact'],[sp[0]],'Konuşmadaki ödeme ifadesi.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2023-10-11',date_precision='day',version_id=passages[sp[0]]['version_id'],period_basis='Saadet Partisi yayımında Genel Başkanın grup konuşması.',uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-sosyal-guvenlik'))
readings(topic,'statement',sp)
for kind,claim in [('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',passages[sp[0]]['exact'])]: task(kind,statement,claim,limit)
ep=[(src+'law7491-repeal','action','document','7491 sayılı kanunun 54. maddesi bu istisna fıkrasını kaldırdı.'),(src+'registry-gazette','action','document','TBMM sicili 7491 sayılı kanunun 28 Aralık 2023 tarihinde yayımlandığını gösteriyor.'),(src+'sgk-expanded','result','document','SGK çalışan emeklilerin de ödemeden yararlandığını bildiriyor.'),(src+'sgk-paid','result','document','SGK daha önce çalışma nedeniyle ödenmeyen yaklaşık 4,7 milyon kişiye toplam 23,4 milyar TL ödeme yapıldığını bildiriyor.')]
context='2023 yılında emeklilere yapılan bir defalık 5.000 TL ödemenin çalışan emeklileri de kapsaması.'
eid=event(stem,'2023-12-27','Çalışan emeklilere bir defalık ödeme kapsamı',context,ep,limit)
records['practice_event'][-1].update(common_event_key='turkiye-2023-7491-retirement-bonus-working',occurrence_basis='7464 ve 7491 sayılı kanun metinleri, TBMM yayım sicili ve SGK faaliyet raporu.')
eids=[row[0] for row in ep]
scope=readings(topic,'event',eids)
rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
observed='7491 sayılı kanun çalışanlara ilişkin istisnayı kaldırdı. SGK, daha önce çalışma nedeniyle ödeme almayan yaklaşık 4,7 milyon kişiye toplam 23,4 milyar TL ödendiğini bildirdi.'
compare='Açıklama ve sonraki düzenleme aynı 5.000 TL ödemenin çalışma durumuna göre kapsamına ilişkindir.'
connection='Çalışma nedeniyle kapsam dışında kalanlar için yasal istisna kaldırıldı ve SGK toplu ödeme bildirdi. Ödeme 5.000 TL ve bir defalık kaldı. Görüşülen teklifin 55. maddesi kabul edilen kanunda 54. madde oldu.'
finding(result,observed,[src+'law7491-repeal',src+'registry-gazette',src+'sgk-paid'],'Kanun metni, yayım sicili ve SGK ödeme verisi ayrı okundu.')
finding(explanation,connection,sp+[src+'law7464-amount',src+'law7464-excluded',src+'law7464-exception',src+'law7491-repeal',src+'debate-article',src+'sgk-paid'],'Tutar, kapsam ve gerçekleşen ödeme ayrı değerlendirildi.')
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='Ekim 2023 açıklaması, ilk kanun ve Aralık değişikliği ayrı tarihlerdir.',authority_context='Karamollaoğlu Saadet Partisi Genel Başkanı olarak konuştu. Kanunu TBMM kabul etti ve ödemeyi SGK bildirdi.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(eids)))
for kind,claim in [('practice_relation',compare),('practice_relation.target_finding_id',goal),('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',connection)]: task(kind,rid,claim,limit)
'''
(p / 'prepare-retired-2023.py').write_text(prefix + body + suffix)
