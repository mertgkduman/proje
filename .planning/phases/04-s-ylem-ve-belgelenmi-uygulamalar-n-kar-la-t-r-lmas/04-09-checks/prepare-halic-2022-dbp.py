from pathlib import Path
from hashlib import sha256
import json,sys
here=Path(sys.argv[1]);template=(here/'prepare-diyarbakir-cng.py').read_text();head=template[:template.index("assert party == 'dbp'")]
head=head.replace("read(here/'diyarbakir-cng-source-records.json')","read(here/'halic-2022-dbp-source-records.json')").replace("read(here/'baglar-cemr-draft.json')","read(data/'practices/04-dbp.json')").replace("read(here/'baglar-cemr-review-draft.json')","read(data/'practices/04-dbp-review.json')").replace('cng-reading-','halic-2022-dbp-reading-').replace('Diyarbakır belediye ulaşımı ve DBP’nin belgelenen katkısı dar kapsamda incelendi.','Haliç halk buluşmasında DBP temsilcisi katılımı dar kapsamda incelendi.').replace('27 Mayıs 2015 tarihli Temsilci haberi ve ayrı belediye ulaşımı kaynakları.','24 Eylül 2022 tarihli Bianet haberi ve HDP yayını, Haliç Kongre Merkezi’ndeki halk buluşmasını ve deklarasyonun açıklanmasını bildiriyor.')
exec(head,globals())
assert sha256((data/'practices/04-dbp.json').read_bytes()).hexdigest()=='005fda05b3e462a76c0a5d8a33248eb38c149d6adcdd8ea2e84c376695b6cccd'
assert sha256((data/'practices/04-dbp-review.json').read_bytes()).hexdigest()=='4dac79689061ea897d70c201265b0efeb4707fc76e0c6ba7f7d0932fcabf58be'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(66,7,0)
stem='0409-halic-2022-dbp';src='0409-halic-2022-bianet-';day='2022-09-24';limit='Bianet güncellenmiş haberi Bayındırı salondaki kişiler arasında DBP eş genel başkanı olarak sayar. Konuşma, imza veya altı kurucu ittifak bileşeninden biri olarak DBP katılımı çıkarılmaz. Haber 15.24te yayımlanmış, erişilen sürüm 23.08de güncellenmiştir.'
ev=[(src+'event','action','independent_report','Bianet Haliç halk buluşmasını bildirir.'),(src+'declaration','result','independent_report','Bianet buluşmada deklarasyonun açıklandığını bildirir.'),(src+'attendance','action','independent_report','Bianet Bayındırı salonda bulunanlar arasında sayar.')]
eid=event(stem,day,'Emek ve Özgürlük İttifakı’nın Haliç halk buluşması','24 Eylül 2022’de İstanbul Haliç Kongre Merkezi’nde düzenlenen Emek ve Özgürlük İttifakı halk buluşması ve deklarasyonun açıklanması.',ev,limit);records['practice_event'][-1]['common_event_key']='halic-emek-ozgurluk-2022-09-24'
refs=[v[0] for v in ev];authority=src+'identity';scope=readings('demokrasi-katilim','event',refs+[authority]);reason='Bianet DBP eş genel başkanını katılımcılar arasında bildirir. Önceden aynı somut buluşmayı hedefleyen DBP açıklaması araştırmaya açık.';cid=stem+'-unmatched';records['practice_candidate'].append(dict(id=cid,scope_id=scope,event_id=eid,relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(refs)));task('practice_candidate',cid,reason,limit)
actor=stem+'-actor';contribution=stem+'-contribution';fid=stem+'-finding';new('actor',id=actor,kind='authorized_representative',party_id='dbp',person_id='0409-dbp-2023-3-761-person',authorization_passage_id=authority)
claim='Bianet, DBP Eş Genel Başkanı Keskin Bayındır’ı Haliç halk buluşmasında salonda bulunanlar arasında saydı.';finding(fid,claim,[authority,src+'attendance'],limit)
records['practice_contribution'].append(dict(id=contribution,event_id=eid,party_id='dbp',actor_id=actor,contribution_kind='unknown',finding_id=fid,authority_passage_id=authority,membership_passage_id=None,responsibility_limit=limit));records['practice_actor_period'].append(dict(contribution_id=contribution,valid_from=day,valid_to=day,identity_passage_id=authority))
for kind in ('practice_contribution','practice_contribution.finding_id'):task(kind,contribution,claim,limit)
footer=template[template.index('for entry in entries:'):]
footer=footer.replace("f'diyarbakir-cng{suffix}-draft.json'","'halic-2022-dbp-draft.json'").replace("f'diyarbakir-cng{suffix}-review-draft.json'","'halic-2022-dbp-review-draft.json'")
exec(footer,globals())
