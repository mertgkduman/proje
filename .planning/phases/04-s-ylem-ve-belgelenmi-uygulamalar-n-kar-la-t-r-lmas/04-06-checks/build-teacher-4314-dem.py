"""47 olaylı öncül üzerinde 10/4314 için ayrı, henüz yayımlanmamış aday."""
import datetime, hashlib, json
from pathlib import Path

c = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
package, review = c/'nov03-4961-dem-draft.json', c/'nov03-4961-dem-review-draft.json'
assert sha(package) == '0e498c38317c2746319cd8e9fa1f2cc0139a0c804fa43e8ff4ab55853ff41557'
assert sha(review) == '4b757c1210852cace464e8fa98b530683ed92f41c27eec6b0b3c63fbc771c66a'
pkg, rev = json.loads(package.read_text()), json.loads(review.read_text())
entries = json.loads((c/'teacher-4314-source-records.json').read_text())['entries']
passages = {x['values']['id']:x['values'] for x in entries if x['kind']=='passage'}
versions = {x['values']['id']:x['values'] for x in entries if x['kind']=='document_version'}
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
q = lambda s:'0406-dem-teacher-4314-'+s
event, finding, contribution, candidate = (q(x) for x in ('event','finding','contribution','candidate'))
scope='practice-6d723d84e08e10e71b638b6fc76bd056dfa1e68397cee2e00b65a557cdf1570d'
points=[('signed-number','initiative'),('signed-scope','initiative'),('register-number','initiative'),('register-date','initiative'),('proposal','initiative'),('identity','action'),('support','action'),('result','result')]
ids=[q(x) for x,_ in points]
def add(kind,**values): pkg['practice_records'].setdefault(kind,[]).append(values)
add('practice_scope_v2',id=scope,party_id='dem',topic_id='ekonomi-emek-v2',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='Yalnız 24 Haziran 2026 öğretmenlerin çalışma koşulları hakkındaki grup görüşü ve gündem kararı; emek kapsamı araştırması sürüyor.')
entries.append(dict(kind='finding',values=dict(id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='24 Haziran 2026 Genel Kurulunda DEM Parti Grubu adına Yılmaz Hun, özel sektör ve ücretli öğretmenlerin çalışma koşulları ile atama mülakatlarına değinerek Yeni Yol’un araştırma önerisinin görüşülmesini destekledi. Genel Kurul 10/4314 araştırmasının aynı birleşimde ön görüşmeye alınması yönündeki grup önerisini kabul etmedi. Bu gündem kararı, esas araştırma önergesinin sonucu ve isimli oy ayrı konulardır.',provenance='summary',epistemic_type='claim')))
for suffix,stage in points:
 pid=q(suffix); passage=passages[pid]
 entries.extend([dict(kind='finding_evidence',values=dict(finding_id=finding,passage_id=pid,role='support')),dict(kind='verification',values=dict(finding_id=finding,passage_id=pid,checked_at=now,result='confirmed',reason='İmzalı dosya, sicil ve tutanak ilgili bölümleri okundu.'))])
 add('practice_event_evidence',event_id=event,passage_id=pid,supported_point=passage['section'],stage=stage,concrete_basis='TBMM imzalı 10/4314 önergesi, esas sicili ve 24 Haziran birleşim tutanağı.',limitation='Sözlü destek, gündem kararı, esas dosyası ve isimli oy ayrıdır.',epistemic_type='claim')
 add('practice_evidence_assessment',event_id=event,passage_id=pid,stage=stage,basis_kind='document')
entries.append(dict(kind='review',values=dict(id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Grup aidiyeti, sözlü destek ve ayrı gündem kararı kontrol edildi.')))
add('practice_event',id=event,common_event_key='tbmm-28-4-106-10-4314-gundem',event_at='2026-06-24',date_precision='day',date_unknown_reason=None,title='10/4314 öğretmenlerin çalışma şartları araştırmasının ön görüşme talebinin reddi',scope_context='Yeni Yol Grubu, Bülent Kaya ve diğer milletvekillerinin öğretmenlerin çalışma şartları ve atamalarına ilişkin 10/4314 araştırma önergesinin ön görüşmesinin 24 Haziran 2026 birleşiminde yapılmasını istedi. Genel Kurul bu gündem talebini reddetti.',occurrence_basis='TBMM 28. Dönem 4. Yasama Yılı 106. Birleşim tam tutanağı, imzalı 10/4314 önergesi ve TBMM esas kaydı.')
add('practice_contribution',id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='support',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM grubu adına açık sözlü destek; isimli oy ve esas araştırmanın sonucu çıkarılmaz.')
add('practice_candidate',id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Öğretmen çalışma koşullarına özgü bağımsız önceki parti söylemi araştırması açık; sözlü destek, gündem kararı ve esas dosyası ayrıdır.',passage_ids=json.dumps(ids,ensure_ascii=False))
targets=[('practice_event_evidence',event+'|'+q(n)+'|'+stage,[q(n)],passages[q(n)]['section']) for n,stage in points]
targets += [('practice_event',event,ids,'10/4314 ve ayrı gündem kararı.'),('practice_contribution',contribution,ids,'DEM grubu adına sözlü destek.'),('practice_contribution.finding_id',contribution,ids,'Konuşma ve karar sınırı.'),('practice_candidate',candidate,ids,'Önceki söylem araştırması açık.')]
for typ,ident,refs,description in targets:
 rev['practice_source_review'].append(dict(subject_kind=typ,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(passages[x]['version_id'] for x in refs)),ensure_ascii=False),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps(list(dict.fromkeys(passages[x]['section'] for x in refs)),ensure_ascii=False),supported_claim=description,limitations='Sözlü destek isimli oy değildir; gündem kararı esas önergenin sonucu değildir.',result='reviewed',reason=('TBMM esas numarası incelendi.' if 'register-number|initiative' in ident else 'İmzalı önergenin ilk sayfasındaki esas numarası incelendi.' if 'signed-number|initiative' in ident else 'İlgili sicil, imzalı dosya ve tutanak okundu.')))
for suffix in ('floor-v1','register-v1','signed-v1'):
 vid=q(suffix); refs=[x for x in ids if passages[x]['version_id']==vid]
 add('practice_scope_source',scope_id=scope,version_id=vid,inspected_sections=json.dumps([passages[x]['section'] for x in refs],ensure_ascii=False),inspected_at=now)
 add('practice_attempt_v2',id=q(suffix+'-reading'),scope_id=scope,attempted_at=now,query='24 Haziran 2026 10/4314 öğretmenler ve DEM grup konuşması',url=versions[vid]['original_url'],result='examined',reason='İlgili bölüm okundu; imzalı önergenin dört sayfası görsel incelendi.',source_version_id=vid)
pkg['entries']+=entries
rev['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in rev['practice_source_review']]
for name,obj in [('teacher-4314-dem-draft.json',pkg),('teacher-4314-dem-review-draft.json',rev)]:
 path=c/name;path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(path))
