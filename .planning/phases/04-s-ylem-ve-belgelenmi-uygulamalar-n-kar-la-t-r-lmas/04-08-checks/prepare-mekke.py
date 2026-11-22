from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from uygulamalar import practice_review_targets, validate_practice_source_review, validate_practices

here=Path(sys.argv[1])
data=Path('data')
def read(path):
    return json.loads(path.read_bytes())
def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)
aux=read(here/'mekke-source-records.json')
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
        aid=f'followup-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='İmzalı teklif veya önerge, TBMM kayıt sayfası ve tutanak.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'yeni-yol'
stem = '0408-yeni-yol-2026-mekke'
topic = 'dis-politika'
base = '0408-mekke-'
authority = base+'caliskan-group-authority'
published = base+'caliskan-group-quote'
amendment = base+'kaya-response-speaker'
vote_reason = base+'kaya-vote-explanation-quote'
bulent = base+'ballot-bulent'
ertugrul = base+'ballot-ertugrul'
caliskan_ballot = base+'ballot-necmettin'
net = [base+'ballot-'+key for key in ('accept','reject','duplicate')]
votes = [row[0] for row in aux['vote_rows']]
bill = base+'bill-esas'
result_news = base+'mekke-general-result-result'
karal = base+'kaya-general-hasan-karal'
mustafa = base+'kaya-general-mustafa-kaya'
nato = base+'kaya-general-nato'
birol = base+'mekke-general-result-birol'
st = stem+'-statement'
target = stem+'-target'
q = stem+'-quote'
limit = ('Cetveldeki bireysel oylar sistem, pusula ve sonuç sütunlarıyla ayrı okunuyor. 4 Kasım konuşmaları, '
         '5 Kasım değişiklik görüşmesi, teklifin son oyu ve anlaşmanın sonraki uygulaması ayrı işlemler.')
target_text = ('Necmettin Çalışkan, 5 Kasım’da Yeni Yol Grubu adına konuşurken Mekke Anlaşması’nın '
               'gündeme getiriliş ve görüşülüş biçimini eleştirdi.')
reading_reason = 'TBMM konuşmasının grup başlığı ve cümlesi özgün sayfada birlikte okundu.'
finding(target,target_text,[authority,published],reading_reason)
finding(q,passages[published]['exact'],[published],reading_reason,pair=target)
records['practice_statement'].append(dict(id=st,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=q,statement_at='2026-11-05',date_precision='day',
    version_id=passages[published]['version_id'],
    period_basis='5 Kasım 2026 tarihli 14. Birleşimin açık oylama öncesi Yeni Yol grubu konuşması.',
    uncertainty_reason=None,comparison_row_id='04-03-v3-0307-yeni-yol-dis-politika-program'))
readings(topic,'statement',[authority,published])
for kind,claim in (('practice_statement',target_text),
                   ('practice_statement.summary_finding_id',target_text),
                   ('practice_statement.quote_finding_id',passages[published]['exact'])):
    task(kind,st,claim,'Yetki konuşma başlığında Yeni Yol TBMM Grubu adına veriliyor.')
evidence=[
    (bill,'initiative','document','Onaylamayı uygun bulma teklifinin TBMM esas numarası 2/3961.'),
    (amendment,'action','document','Bülent Kaya madde değişiklik önergesi üzerinde konuştu.'),
    (caliskan_ballot,'action','document','Necmettin Çalışkan’ın kişisel oy satırı 23.49.37 ret kaydını gösteriyor.'),
    (bulent,'action','document','Bülent Kaya, cetvelde 23.49.36’da ret oyu verdi.'),
    (ertugrul,'action','document','Ertuğrul Kaya, cetvelde 23.49.37’de kabul oyu verdi.'),
    (net[0],'result','document','TBMM açık oy cetveli 277 kabul oyu bildiriyor.'),
    (net[1],'result','document','TBMM açık oy cetveli 118 ret oyu bildiriyor.'),
    (net[2],'result','document','Cetvelde üç mükerrer oy ayrı kaydedildi.'),
    (result_news,'result','document','TBMM 6 Kasım’da teklifin Genel Kurulda kabulünü duyurdu.'),
]
eid = event(stem,'2026-11-05','2/3961 Mekke Anlaşması onay teklifinin açık oylaması',
    'TBMM’nin 14. birleşiminde teklifin tümüne ilişkin açık oylama yapıldı ve teklif kabul edildi.',evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-5-014-2-3961-mekke-7597',
    occurrence_basis='TBMM 5 Kasım 14. Birleşim açık oy cetveli, konuşma nüshaları ve 2/3961 yasama kaydı.')
event_refs = [p for p,_,_,_ in evidence]
discussion = [authority, published, vote_reason, karal, mustafa, nato, birol, caliskan_ballot]
scope = readings(topic,'event',list(dict.fromkeys([*event_refs,*votes,*discussion])))
ham_url = 'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/14/Ham/b9ac02f0-8eaa-42a9-aeb0-1e90e7779c6a.pdf'
records['practice_attempt_v2'].append(dict(id=stem+'-ham-pdf-attempt',scope_id=scope,
    attempted_at=when,query=ham_url,url=ham_url,result='failure',source_version_id=None,
    reason='TBMM ham tutanak PDF’sinin ilgili satırları tarayıcıda okundu. Düğümden özgün dosya alımı HTTP 404 döndü.'))
records['practice_lead'].append(dict(id=stem+'-ham-pdf-lead',scope_id=scope,url=ham_url,state='blocked',
    relevance_reason='Grup konuşması ve değişiklik önergelerinin Genel Kuruldaki işlemi.',
    attempt_ids=encoded([stem+'-ham-pdf-attempt'])))
person = stem+'-caliskan-person'
actor = stem+'-caliskan-group'
cid = stem+'-caliskan-contribution'
contribution = stem+'-group-speech'
contribution_limit = ('Tutanaktaki temsil yetkisi grup adına konuşmaya ait. Çalışkan’ın ret oyu ayrı satırda. '
                      'Bülent Kaya ve Ertuğrul Kaya’nın oyları ile grubun diğer üyelerinin oyları kişisel kayıtlardır.')
new('person',id=person,name='NECMETTİN ÇALIŞKAN')
new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,authorization_passage_id=authority)
contribution_text = target_text + ' Kişisel oyu cetvelde 23.49.37’de ret olarak kayıtlı.'
finding(contribution,contribution_text,[authority,published,caliskan_ballot],
        'Temsil başlığı, konuşma ve ayrı bireysel oy satırı denetlendi.')
records['practice_contribution'].append(dict(id=cid,event_id=eid,party_id=party,actor_id=actor,
    contribution_kind='objection',finding_id=contribution,authority_passage_id=authority,
    membership_passage_id=None,responsibility_limit=contribution_limit))
records['practice_actor_period'].append(dict(contribution_id=cid,valid_from='2026-11-05',valid_to='2026-11-05',
    identity_passage_id=authority))
task('practice_contribution',cid,contribution_text,contribution_limit)
task('practice_contribution.finding_id',cid,contribution_text,contribution_limit)
rid = stem+'-relation'
expl = stem+'-explanation'
result = stem+'-result'
compare = 'Yeni Yol grubu adına konuşma ve açık oylama aynı 2/3961 teklifine ilişkin.'
outcome = 'TBMM teklifi 277 kabul ve 118 ret oyuyla kabul etti. Cetvelde üç mükerrer oy ayrı gösteriliyor.'
connection = ('Çalışkan, Yeni Yol Grubu adına görüşme sürecini eleştirdi. Cetvelin Yeni Yol etiketli 20 satırında '
              '15 ret, 1 kabul ve 4 katılmadı kaydı var. Retlerin üçü pusulayla işlendi. '
              'Bülent Kaya ret, Ertuğrul Kaya kabul oyu verdi.')
finding(expl,connection,[authority,published,vote_reason,*votes],
    'Grup sözünün yetkisi ve cetvelin sistem, pusula ile sonuç sütunları ayrı denetlendi.')
finding(result,outcome,[*net,result_news],'Açık oy cetvelinin sonuç satırları ve TBMM kabul duyurusu karşılaştırıldı.')
records['practice_relation'].append(dict(id=rid,statement_id=st,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=expl,temporal_context='5 Kasım grup konuşmasını aynı birleşimde teklifin tümü üzerindeki açık oy izledi.',
    authority_context='Çalışkan görüşmede Yeni Yol Grubu adına konuştu. Açık oy cetveli milletvekillerinin ayrı oylarını gösteriyor.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(event_refs)))
for kind,claim in (('practice_relation',connection),('practice_relation.target_finding_id',target_text),
                   ('practice_relation.result_finding_id',outcome),('practice_relation.explanation_finding_id',connection)):
    task(kind,rid,claim,limit)
for entry in entries:
    dest=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in dest: dest.append(entry['values'])
for table,rows in records.items():
    dest=snapshot.setdefault(table,[])
    dest.extend(row for row in rows if row not in dest)
validate_practices(snapshot)
targets=practice_review_targets(snapshot,records)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limitation,result='reviewed',
        reason=kind+' hedefinin asıl kaynakları, tarihi ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,selection=records,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('mekke-draft.json',package),('mekke-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
