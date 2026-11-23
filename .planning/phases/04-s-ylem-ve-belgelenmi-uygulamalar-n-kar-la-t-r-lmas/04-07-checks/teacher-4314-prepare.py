from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from uygulamalar import practice_review_package_targets, validate_practice_source_review, validate_practices

here=Path(sys.argv[1])
data=Path('data')
def read(path):
    return json.loads(path.read_bytes())
def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)
aux=read(here/'teacher-4314-source-records.json')
party=aux['party_id']
package=read(data/f'practices/04-{party}.json')
review=read(data/f'practices/04-{party}-review.json')
snapshot=read(data/'releases'/package['base_release']/'records.json')
inventory=read(data/'practices/04-inventory.json')
entries=package['entries']; entries.extend(aux['entries'])
records=package['practice_records']
when=datetime.now(timezone.utc).isoformat()
passages={r['id']:r for r in snapshot['passage']}
passages.update({e['values']['id']:e['values'] for e in entries if e['kind']=='passage'})
versions={r['id']:r for r in snapshot['document_version']}
versions.update({e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'})
tasks={}
def new(table,**row):
    entries.append(dict(kind=table,values=row))
def finding(id,body,refs,reason,pair=None):
    new('finding',id=id,party_id=party,heading='Belgelenmiş uygulamalar',text=body,pair_id=pair or id,
        provenance='quote' if pair else 'summary',epistemic_type='claim')
    for pid in refs:
        new('finding_evidence',finding_id=id,passage_id=pid,role='support')
        new('verification',finding_id=id,passage_id=pid,checked_at=when,result='confirmed',reason=reason)
    new('review',id='review-'+id,kind='finding',subject_id=id,reviewer_kind='agent',
        reviewed_at=when,result='reviewed',reason=reason)
def task(kind,identity,body,limitation):
    tasks[(kind,identity)]=(body,limitation)
def scope_for(topic,lane):
    cell=next(row for row in inventory['cells']
              if (row['party_id'],row['topic_id'],row['research_kind'])==(party,topic,lane))
    sid=cell['cell_id']
    if not any(s['id']==sid for s in records['practice_scope_v2']):
        records['practice_scope_v2'].append(dict(id=sid,**{k:cell[k] for k in
            ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')},
            boundary_reason='İlgili politika söylemi ve TBMM işlem zinciri dar kapsamda incelendi.'))
    return sid
def readings(topic,lane,refs):
    sid=scope_for(topic,lane)
    grouped={}
    for pid in refs:
        p=passages[pid]
        grouped.setdefault(p['version_id'],set()).add(p['section'])
    for vid,sections in grouped.items():
        existing=[r for r in records['practice_scope_source'] if (r['scope_id'],r['version_id'])==(sid,vid)]
        if existing and set(json.loads(existing[-1]['inspected_sections']))>=sections:
            continue
        if existing:
            sections.update(json.loads(existing[-1]['inspected_sections']))
            if existing[-1]['inspected_at']==when:
                existing[-1]['inspected_sections']=encoded(sorted(sections))
                continue
        url=versions[vid]['final_url']
        aid=f'teacher-4314-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='İlgili politika söylemi, önerge veya kanun teklifi.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='TBMM 28. Dönem 4. Yasama Yılı 106. Birleşim tam tutanağı, imzalı 10/4314 önergesi ve TBMM esas kaydı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid

assert party=='iyi'
assert sha256((data/'practices/04-iyi.json').read_bytes()).hexdigest()=='b268cf0188bb5b785378d27db0605e8e9e83106c8d40740c553ac013cee180fe'
assert sha256((data/'practices/04-iyi-review.json').read_bytes()).hexdigest()=='6ef5d3804433db824a71e1f70bf4d98a7be978b30a2c61abce41f3f3a6f73a4d'
stem='0407-iyi-teacher-4314';prefix=stem+'-';authority=prefix+'identity';limit='Ret, ön görüşmenin 24 Haziran birleşiminde yapılması talebine aittir; esas araştırma sonucu ve kişisel oy bilinmiyor.'
evidence=[(prefix+'register-number','initiative','document','TBMM esas numarası 10/4314.'),(prefix+'register-date','initiative','document','TBMM esas kaydında geliş tarihi 24 Haziran 2026.'),(prefix+'signed-number','initiative','document','İmzalı önergenin esas numarası 10/4314.'),(prefix+'signed-scope','initiative','document','İmzalı gerekçe atama sistemi için araştırma komisyonu istemektedir.'),(prefix+'proposal','action','document','Yeni Yol aynı gün ön görüşme istedi.'),(authority,'action','document','Başkan Türkoğlu’na İYİ Parti Grubu adına söz verdi.'),(prefix+'support','action','document','Türkoğlu önergeye sözlü destek verdi.'),(prefix+'result','result','document','Başkan gündem talebinin kabul edilmediğini açıkladı.')]
context='Yeni Yol Grubu, Bülent Kaya ve diğer milletvekillerinin öğretmenlerin çalışma şartları ve atamalarına ilişkin 10/4314 araştırma önergesinin ön görüşmesinin 24 Haziran 2026 birleşiminde yapılmasını istedi. Genel Kurul bu gündem talebini reddetti.'
eid=event(stem,'2026-06-24','10/4314 öğretmenlerin çalışma şartları araştırmasının ön görüşme talebinin reddi',context,evidence,limit)
records['practice_event'][-1]['common_event_key']='tbmm-28-4-106-10-4314-gundem'
refs=[x[0] for x in evidence];scope=readings('guvencesiz-istihdam','event',refs)
person=prefix+'person';actor=prefix+'actor';contribution=prefix+'contribution';fid=prefix+'finding'
new('person',id=person,name='Yüksel Selçuk Türkoğlu');new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,authorization_passage_id=authority)
body='Yüksel Selçuk Türkoğlu, İYİ Parti Grubu adına Yeni Yol’un 10/4314 öğretmenlerin çalışma şartları ve atamalarına ilişkin araştırma önergesinin ön görüşmesinin aynı gün yapılması talebini destekledi. Başkan gündem talebinin kabul edilmediğini açıkladı.'
finding(fid,body,refs,'Birinci gündem önerisi, grup adına sözlü destek ve sonucu ile esas dosya ayrı kaynaklarda incelendi.')
records['practice_contribution'].append(dict(id=contribution,event_id=eid,party_id=party,actor_id=actor,contribution_kind='support',finding_id=fid,authority_passage_id=authority,membership_passage_id=None,responsibility_limit='Türkoğlu grup adına sözlü destek verdi; isimli açık oy gösterilmedi.'))
records['practice_actor_period'].append(dict(contribution_id=contribution,valid_from='2026-06-24',valid_to='2026-06-24',identity_passage_id=authority))
task('practice_contribution',contribution,body,limit);task('practice_contribution.finding_id',contribution,body,limit)
cid=prefix+'candidate';reason='Önceleyen aynı ölçekte tarihli İYİ Parti söylemi henüz doğrulanmadı; araştırma açıktır.'
records['practice_candidate'].append(dict(id=cid,scope_id=scope,event_id=eid,relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(refs)));task('practice_candidate',cid,reason,limit)
for entry in entries:
 destination=snapshot.setdefault(entry['kind'],[])
 if entry['values'] not in destination:destination.append(entry['values'])
for table,rows in records.items():
 destination=snapshot.setdefault(table,[]);destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot,records,[entry['values']['id'] for entry in entries if entry['kind']=='passage'],party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
 pids,owners=targets[(kind,identity)];assert party in owners
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),supported_claim=claim,limitations=limitation,result='reviewed',reason=kind+' kaynak metni, tarih ve kapsam sınırları okundu. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews];package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('teacher-4314-draft.json',package),('teacher-4314-review-draft.json',review)]:
 path=here/name
 with path.open('x') as output:output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
 print(name,sha256(path.read_bytes()).hexdigest())
print('TEACHER_4314_SEMANTIC_PASS',len(tasks))
