from pathlib import Path
from hashlib import sha256
import json,sys
here=Path(sys.argv[1]); template=(here.parent/'04-09-checks'/'prepare-diyarbakir-cng.py').read_text(); head=template[:template.index("assert party == 'dbp'")]
head=head.replace("read(here/'diyarbakir-cng-source-records.json')","read(here/'joint-2020-emep-source-records.json')").replace("read(here/'baglar-cemr-draft.json')","read(data/'practices/04-emep.json')").replace("read(here/'baglar-cemr-review-draft.json')","read(data/'practices/04-emep-review.json')").replace('cng-reading-','joint-2020-emep-reading-').replace('Diyarbakır belediye ulaşımı ve DBP’nin belgelenen katkısı dar kapsamda incelendi.','18 Mayıs 2020 ortak bildirisi ve EMEP imzası dar kapsamda incelendi.').replace('27 Mayıs 2015 tarihli Temsilci haberi ve ayrı belediye ulaşımı kaynakları.','18 Mayıs tarihli ortak açıklama ve 19 Mayıs BirGün basılı sayı, sayfa 8.')
head=head.replace("2015 tanıtımı ve belediye ulaşımının ilgili kaynak bağlamı.","18 Mayıs 2020 ortak bildirisinin yayın tarihi ve imzacıları.")
exec(head,globals())
assert sha256((data/'practices/04-emep.json').read_bytes()).hexdigest()=='faf5b3a8e52a67c1fbf0d946ee81044bbbfef3a8231c58567bfd8b159a9390b2'
assert sha256((data/'practices/04-emep-review.json').read_bytes()).hexdigest()=='9a325e0e74acbab72c7edbf35ff62b04db9fb2db0e6efae9677d5227adc8e7f6'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(83,79,0)
stem='0410-joint-2020-emep'; h='0410-joint-2020-hdp-'; b='0410-joint-2020-birgun-'; day='2020-05-18'
limit='HDP ortak bildirinin yayıncısıdır; EMEP imzacıdır. 19 Mayıs BirGün sonraki tarihli haberdir. Bildirinin atamalara ve hukuka dair ifadeleri imzacıların beyanıdır; beş ayrı idari atama ve kişisel sonuç bu olay değildir.'
ev=[(h+'date','action','document','HDP yayımında ortak bildirinin tarihi 18 Mayıs 2020dir.'),(h+'signature','action','document','Ortak bildiride EMEP imzacı olarak listelenir.'),(b+'title','action','independent_report','BirGün sonraki gün ortak bildiriyi haberleştirdi.'),(b+'signature','action','independent_report','BirGün basılı haberi EMEPyi imzacı listesinde sayar.')]
eid=event(stem,day,'Yerel yönetimlere ilişkin 18 Mayıs 2020 ortak bildirisi','18 Mayıs 2020 tarihli ortak bildirinin yayımlanması.',ev,limit);records['practice_event'][-1]['common_event_key']='yerel-yonetimler-2020-05-18-ortak-bildiri'
refs=[v[0] for v in ev]; scope=readings('demokrasi-katilim','event',refs); reason='Önceki ayrı ve aynı bildiriyi konu alan EMEP sözü araştırmaya açıktır; ortak metnin kendisi olaydır.'
cid=stem+'-unmatched';records['practice_candidate'].append(dict(id=cid,scope_id=scope,event_id=eid,relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(refs)));task('practice_candidate',cid,reason,limit)
actor=stem+'-actor';contribution=stem+'-contribution';fid=stem+'-finding';new('actor',id=actor,kind='institution',party_id='emep',person_id=None,authorization_passage_id=None)
claim='EMEP, 18 Mayıs 2020 tarihli yerel yönetimler ortak bildirisi imzacıları arasında yer aldı.';finding(fid,claim,[h+'signature',b+'signature'],limit)
records['practice_contribution'].append(dict(id=contribution,event_id=eid,party_id='emep',actor_id=actor,contribution_kind='support',finding_id=fid,authority_passage_id=None,membership_passage_id=None,responsibility_limit=limit))
for kind in ('practice_contribution','practice_contribution.finding_id'):task(kind,contribution,claim,limit)
footer=template[template.index('for entry in entries:'):];footer=footer.replace("f'diyarbakir-cng{suffix}-draft.json'","'joint-2020-emep-draft.json'").replace("f'diyarbakir-cng{suffix}-review-draft.json'","'joint-2020-emep-review-draft.json'");exec(footer,globals())
