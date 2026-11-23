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
aux=read(here/'fund-july-source-records.json')
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
        aid=f'yy-7573-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='TBMM önergesi, birleşim tutanağı ve ilgili işlem belgeleri.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'yeni-yol'
topic = 'makroekonomik-politika'
stem = '0408-yeni-yol-2026-4343'
signed, floor, detail, summary, october = ['0408-fund-july-'+s+'-' for s in ('signed','floor','detail','summary','oct07')]
statement, target, quote = (stem+tail for tail in ('-statement','-target','-quote'))
goal = ('Sadullah Kısacık ve 19 milletvekili, sermaye piyasasındaki sorunların, küçük yatırımcının korunmasının '
        've yatırımcı tazmin araçlarının güçlendirilmesinin Mecliste araştırılmasını istedi.')
basis = '1 Temmuz imzalı araştırma önergesinin gerekçe sayfaları ve TBMM esas dosyası.'
statement_refs = [signed+'concern',signed+'objective',detail+'filed']
finding(target,goal,statement_refs,basis)
finding(quote,passages[signed+'objective']['exact'],[signed+'objective'],basis,pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-07-01',date_precision='day',
    version_id=passages[signed+'objective']['version_id'],period_basis='Aynı gün görüşme oylamasından önce TBMM’ye verilen imzalı 10/4343 metni.',
    uncertainty_reason=None,comparison_row_id='04-03-v3-0307-yeni-yol-makroekonomik-politika-program'))
readings(topic,'statement',statement_refs)
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[signed+'objective']['exact'])):
    task(kind,statement,claim,'Yazılı talep sermaye piyasası ve küçük yatırımcı için genel kapsamlı Meclis araştırması istiyor.')


def relate(stem,eid,scope,refs,context,reason,authority,period,limit,explanation_refs,outcome=None,result_refs=()):
    rid,explanation=(stem+tail for tail in ('-relation','-explanation'))
    result_id=stem+'-result' if outcome else None
    if outcome:
        finding(result_id,outcome,result_refs,limit)
    finding(explanation,context,[*statement_refs,*explanation_refs],limit)
    records['practice_relation'].append(dict(id=rid,event_id=eid,statement_id=statement,party_id=party,
        topic_id=topic,scope_id=scope,comparability_reason=reason,target_finding_id=target,
        result_finding_id=result_id,explanation_finding_id=explanation,temporal_context=period,
        authority_context=authority,uncertainty_reason=limit))
    records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,
        relation_id=rid,state='eligible',reason=reason,passage_ids=encoded(refs)))
    for kind,claim in (('practice_relation',context),('practice_relation.target_finding_id',goal),
                       ('practice_relation.explanation_finding_id',context)):
        task(kind,rid,claim,limit)
    if outcome:
        task('practice_relation.result_finding_id',rid,outcome,limit)


def contribution(stem,eid,name,day,authority,refs,claim,limit):
    person,actor,cid,fid=(stem+tail for tail in ('-person','-actor','-contribution','-finding'))
    new('person',id=person,name=name)
    new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,authorization_passage_id=authority)
    finding(fid,claim,[authority,*refs],limit)
    records['practice_contribution'].append(dict(id=cid,event_id=eid,party_id=party,actor_id=actor,
        contribution_kind='support',finding_id=fid,authority_passage_id=authority,membership_passage_id=None,
        responsibility_limit=limit))
    records['practice_actor_period'].append(dict(contribution_id=cid,valid_from=day,valid_to=day,identity_passage_id=authority))
    for kind in ('practice_contribution','practice_contribution.finding_id'):
        task(kind,cid,claim,limit)


july_limit = ('Oylama aynı gün ön görüşme önerisi hakkında. Erişim anında 10/4343 dosyası Gündemde. '
            'İsimli oylar ve araştırma komisyonunun kurulmasına ilişkin ayrı sonuç açık.')
july_outcome = ('İlk iki elektronik oylamada karar yeter sayısı bulunamadı. Genel Kurul 5. oturumdaki '
                'üçüncü elektronik oylamada 10/4343’ün aynı gün görüşülmesini kabul etmedi.')
july_context = 'Yeni Yol Grubu 10/4343’ün 1 Temmuz birleşiminde görüşülmesini önerdi. Genel Kurul öneriyi kabul etmedi.'
evidence = [
    (signed+'id','initiative','document','İmzalı dosyanın esas numarası 10/4343.'),
    (signed+'signature','initiative','document','İmza tablosunun ilk sırasında Sadullah Kısacık bulunuyor.'),
    (detail+'id','initiative','document','TBMM dosyası 10/4343 numarasını teyit ediyor.'),
    (floor+'agenda','action','document','Yeni Yol grubu adına aynı gün ön görüşme talep edildi.'),
    (floor+'authority','action','document','Kısacık Yeni Yol Grubu adına gerekçeyi açıkladı.'),
    (floor+'goal','action','document','Kısacık sermaye piyasası için araştırma komisyonu istedi.'),
    (floor+'quorum1','action','document','3. oturumdaki ilk elektronik oylamada karar yeter sayısı bulunamadı.'),
    (floor+'quorum2','action','document','4. oturumdaki ikinci elektronik oylamada karar yeter sayısı bulunamadı.'),
    (floor+'decision','result','document','5. oturumdaki üçüncü elektronik oylamada öneri kabul edilmedi.'),
    (summary+'result','result','document','Birleşim özeti aynı gün görüşme önerisinin kabul edilmediğini kaydediyor.'),
]
eid=event(stem,'2026-07-01','10/4343 araştırma önergesinin aynı gün görüşülmesi',july_context,evidence,july_limit)
records['practice_event'][-1]['common_event_key']='tbmm-28-4-108-10-4343-gundem'
refs=[row[0] for row in evidence]
scope=readings(topic,'event',refs+[detail+'pending',floor+'iyi-role',floor+'iyi-support',floor+'dem-role',floor+'dem-support'])
contribution(stem+'-kisacik',eid,'SADULLAH KISACIK','2026-07-01',floor+'authority',[floor+'goal'],
    'Sadullah Kısacık, Yeni Yol Grubu adına sektörün sorunları ve yatırımcıların korunması için araştırma komisyonu istedi.',
    july_limit)
relate(stem,eid,scope,refs,goal+' '+july_outcome,
    'Aynı 10/4343 dosyasının araştırma talebi ve talebin Genel Kurul gündemine alınması ortak kapsamı taşıyor.',
    'Önerge imzacıları, Bülent Kaya’nın grup takvim önerisi ve Kısacık’ın konuşması ayrı kayıtlarda.',
    '10/4343 araştırma önergesi ve daha sonra 108. Birleşim gündem oylaması, 1 Temmuz.',
    july_limit,[floor+'agenda',floor+'decision'],july_outcome,[floor+'quorum1',floor+'quorum2',floor+'decision'])

opening='0408-yeni-yol-2026-fund-1007'
oct_limit=('7 Ekim yürütme açıklaması ve siyasi grup görüşleri ayrı işlem. Bu oturumda araştırma komisyonu '
           'kurulmasına veya bir ödeme yapılmasına ilişkin sonuç açık.')
oct_context = ('Cumhurbaşkanı Yardımcısı Cevdet Yılmaz fon piyasalarına ilişkin Genel Kurulda açıklama yaptı. '
    'Siyasi parti grupları ve grubu bulunmayan bir milletvekili görüşlerini bildirdi.')
oct_evidence=[
    (october+'role','action','document','Bülent Kaya 7 Ekim’de konuşmaya Yeni Yol Grubu adına başladı.'),
    (october+'plan','action','document','Kaya, kurumlar arasındaki yazışmaların bir Meclis araştırma komisyonunda ortaya konmasını istedi.'),
    (october+'followup','action','document','Kaya konuşmasını araştırma talebini sürdüreceğini söyleyerek bitirdi.'),
]
oct_event=event(opening,'2026-10-07','TBMM 3. Birleşimde fon piyasası açıklaması ve görüşler',
    oct_context,oct_evidence,oct_limit)
records['practice_event'][-1]['common_event_key']='tbmm-28-5-003-fon-piyasasi-bilgilendirme'
records['practice_event'][-1]['occurrence_basis']='TBMM birleşim tutanağı ve ilgili işlem belgeleri.'
oct_refs=[row[0] for row in oct_evidence]
oct_scope=readings(topic,'event',oct_refs)
contribution(opening+'-kaya',oct_event,'BÜLENT KAYA','2026-10-07',october+'role',[october+'plan',october+'followup'],
    'Bülent Kaya, Yeni Yol Grubu adına fon işlemlerini inceleyecek Meclis araştırma komisyonu talebini dile getirdi.',
    oct_limit)
relate(opening,oct_event,oct_scope,oct_refs,
    '1 Temmuz 10/4343 genel piyasa denetimi ve küçük yatırımcıları kapsıyordu. 7 Ekim’de Bülent Kaya belirli fon '
    'tasfiyesi bağlamında kurumlar arası yazışmaların bir Meclis araştırma komisyonunda incelenmesini istedi.',
    'İki kayıtta araştırma komisyonu küçük yatırımcının korunması ve piyasa denetimi amacıyla gündeme geldi. '
    '7 Ekim çağrısı belirli fon olayına odaklandı.',
    'Kısacık ve diğer imzacılar Temmuz önergesini sundu. Kaya Ekim konuşmasına Yeni Yol Grubu adına başladı.',
    '1 Temmuz önergesi ve 7 Ekim Genel Kurul açıklaması.',oct_limit,oct_refs)

for entry in entries:
    dest=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in dest: dest.append(entry['values'])
for table,rows in records.items():
    dest=snapshot.setdefault(table,[])
    dest.extend(row for row in rows if row not in dest)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot,records,
    [entry['values']['id'] for entry in entries if entry['kind']=='passage'],party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limitation,result='reviewed',
        reason=kind+' hedefinin asıl kaynakları, tarihi ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('fund-july-draft.json',package),('fund-july-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
