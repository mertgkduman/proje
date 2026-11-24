from pathlib import Path
from hashlib import sha256
import json,sys
here=Path(sys.argv[1]); template=(here/'prepare-diyarbakir-cng.py').read_text(); head=template[:template.index("assert party == 'dbp'")]
head=head.replace("read(here/'diyarbakir-cng-source-records.json')","read(here/'joint-2020-dbp-source-records.json')").replace("read(here/'baglar-cemr-draft.json')","read(data/'practices/04-dbp.json')").replace("read(here/'baglar-cemr-review-draft.json')","read(data/'practices/04-dbp-review.json')").replace('cng-reading-','joint-2020-dbp-reading-').replace('Diyarbakır belediye ulaşımı ve DBP’nin belgelenen katkısı dar kapsamda incelendi.','18 Mayıs 2020 ortak bildirisi ve DBP imzası dar kapsamda incelendi.').replace('27 Mayıs 2015 tarihli Temsilci haberi ve ayrı belediye ulaşımı kaynakları.','18 Mayıs tarihli ortak açıklama ve 19 Mayıs BirGün basılı sayı, sayfa 8.')
exec(head,globals())
assert sha256((data/'practices/04-dbp.json').read_bytes()).hexdigest()=='3e1e0bd7bc3f05adf2cf8ca32a5d3fe0544c9f810faf15af076098bb8a86e134'
assert sha256((data/'practices/04-dbp-review.json').read_bytes()).hexdigest()=='b5b55ae18b0851ac620adc1cfe56b774c416ae86c8623ae986e107e9b856f8fe'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(67,7,0)
stem='0409-joint-2020-dbp'; h='0409-joint-2020-hdp-'; b='0409-joint-2020-birgun-'; day='2020-05-18'
limit='HDP ortak bildirinin yayıncısıdır; DBP imzacıdır. 19 Mayıs BirGün sonraki tarihli haberdir. Bildirinin atamalara ve hukuka dair ifadeleri imzacıların beyanıdır; beş ayrı idari atama ve kişisel sonuç bu olay değildir.'
ev=[(h+'date','action','document','HDP yayımında ortak bildirinin tarihi 18 Mayıs 2020dir.'),(h+'signature','action','document','Ortak bildiride DBP imzacı olarak listelenir.'),(b+'title','action','independent_report','BirGün sonraki gün ortak bildiriyi haberleştirdi.'),(b+'signature','action','independent_report','BirGün basılı haberi DBPyi imzacı listesinde sayar.')]
eid=event(stem,day,'Yerel yönetimlere ilişkin 18 Mayıs 2020 ortak bildirisi','18 Mayıs 2020 tarihli ortak bildirinin yayımlanması.',ev,limit);records['practice_event'][-1]['common_event_key']='yerel-yonetimler-2020-05-18-ortak-bildiri'
refs=[v[0] for v in ev]; scope=readings('demokrasi-katilim','event',refs); reason='Önceki ayrı ve aynı bildiriyi konu alan DBP sözü araştırmaya açıktır; ortak metnin kendisi olaydır.'
cid=stem+'-unmatched';records['practice_candidate'].append(dict(id=cid,scope_id=scope,event_id=eid,relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(refs)));task('practice_candidate',cid,reason,limit)
actor=stem+'-actor';contribution=stem+'-contribution';fid=stem+'-finding';new('actor',id=actor,kind='institution',party_id='dbp',person_id=None,authorization_passage_id=None)
claim='DBP, 18 Mayıs 2020 tarihli yerel yönetimler ortak bildirisi imzacıları arasında yer aldı.';finding(fid,claim,[h+'signature',b+'signature'],limit)
records['practice_contribution'].append(dict(id=contribution,event_id=eid,party_id='dbp',actor_id=actor,contribution_kind='support',finding_id=fid,authority_passage_id=None,membership_passage_id=None,responsibility_limit=limit))
for kind in ('practice_contribution','practice_contribution.finding_id'):task(kind,contribution,claim,limit)
footer=template[template.index('for entry in entries:'):];footer=footer.replace("f'diyarbakir-cng{suffix}-draft.json'","'joint-2020-dbp-draft.json'").replace("f'diyarbakir-cng{suffix}-review-draft.json'","'joint-2020-dbp-review-draft.json'");exec(footer,globals())
