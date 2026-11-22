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
aux=read(here/'aged-source-records.json')
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
        aid=f'aged-reading-{lane}-{topic}-{vid}'
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
assert party == 'iyi'
topic = 'sosyal-hizmet'
stem = '0407-iyi-2024-10-437-gundem'
base = '0407-aged-'
proposal = base+'iyi-437-'
signed = proposal+'signed-'
session = base+'pension-2024-session-'
summary = base+'pension-2024-summary-'
program = '0306-iyi-program-sosyal-hizmet-instrument-passage'
target = stem+'-target'
quote = stem+'-quote'
st = stem+'-statement'
target_text = 'İYİ Parti milletvekillerinin 12 Ekim 2023 tarihli 10/437 araştırma önergesi, huzurevlerinin ve yaşlıların yaşam koşullarının incelenmesini istedi.'
limit = ('17 Ocak oylaması gündeme alma önerisine ilişkin. 10/437’nin erişimde görülen son dosya durumu Gündemde. '
         'Açılan araştırmanın ve fiilen değişen hizmetlerin kanıtı açık.')
statement_limit = 'Ekim araştırma önerisinin gerekçesinde huzurevi incelemesi var. Program sürümünün kabul ve yürürlük günü açık.'
finding(target,target_text,[signed+'quote',signed+'condition'],'Gerekçenin iki taranmış sayfası görsel olarak okundu.')
finding(quote,passages[signed+'quote']['exact'],[signed+'quote'],
    'İmzalı önergenin gerekçesindeki birebir cümle.',pair=target)
records['practice_statement'].append(dict(id=st,party_id=party,topic_id=topic,taxonomy_version=4,
   summary_finding_id=target,quote_finding_id=quote,statement_at='2023-10-12',date_precision='day',
   version_id=passages[signed+'quote']['version_id'],period_basis='10/437 kapağı ve TBMM geliş kaydında 12 Ekim 2023.',
   uncertainty_reason=None,comparison_row_id='04-03-v3-0306-iyi-program-sosyal-hizmet-row'))
readings(topic,'statement',[signed+'quote',signed+'condition',program])
for kind,claim in (('practice_statement',target_text),('practice_statement.summary_finding_id',target_text),
                   ('practice_statement.quote_finding_id',passages[signed+'quote']['exact'])):
    task(kind,st,claim,statement_limit)
evidence = [
    (proposal+'id','initiative','document','10/437 esas numarası TBMM dosya kaydında.'),
    (proposal+'submitted','initiative','document','Önerge 12 Ekim 2023’te Başkanlığa geldi.'),
    (session+'proposal','action','document','İYİ Parti Grubu, 10/437’nin 17 Ocak’ta gündeme alınmasını istedi.'),
    (session+'sunat','action','document','Şenol Sunat tutanakta İYİ Parti Grubu adına konuştu.'),
    (session+'dem-role','action','document','Adalet Kaya tutanakta DEM Parti Grubu adına söz aldı.'),
    (session+'dem-support','action','document','Kaya yaşlı bakımevlerine ilişkin önergeye DEM Parti Grubu adına sözlü destek verdi.'),
    (summary+'topic','action','document','Birleşim özeti İYİ Parti önerisini aynı gün görüşülmek üzere listeliyor.'),
    (summary+'result','result','document','TBMM birleşim özeti gündeme alma önerisinin kabul edilmediğini bildiriyor.'),
]
eid = event(stem,'2024-01-17','10/437 için Genel Kurul gündemine alma önerisi',
    'İYİ Parti Grubu 10/437 araştırma önergesinin 17 Ocak günü görüşülmesini istedi. Genel Kurul bu öneriyi kabul etmedi.',
    evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-2-050-10-437-gundem',
    occurrence_basis='TBMM 10/437 dosyası, 17 Ocak 50. Birleşim tam tutanağı ve işlem özeti.')
refs = [row[0] for row in evidence]
scope = readings(topic,'event',[*refs,proposal+'status',proposal+'first',session+'sunat-statement'])
actor_id = stem+'-sunat-group'
person_id = stem+'-sunat-person'
cid = stem+'-sunat-contribution'
contribution = stem+'-sunat-finding'
authority = session+'sunat'
contribution_text = 'Şenol Sunat, İYİ Parti Grubu adına 10/437 araştırma önergesini ve gündeme alma isteğini savundu.'
climit = 'Grup adına görüşme ve gerekçe belgelendi. İsimli oy ve araştırmanın açılması için ayrı sonuç kaydı açık.'
new('person',id=person_id,name='ŞENOL SUNAT')
new('actor',id=actor_id,kind='authorized_representative',party_id=party,person_id=person_id,authorization_passage_id=authority)
finding(contribution,contribution_text,[authority,session+'sunat-statement',session+'proposal'],
    'Tutanaktaki konuşmacı başlığı, temsil sıfatı ve ilgili gündem önerisi birlikte okundu.')
records['practice_contribution'].append(dict(id=cid,event_id=eid,party_id=party,actor_id=actor_id,
    contribution_kind='support',finding_id=contribution,authority_passage_id=authority,
    membership_passage_id=None,responsibility_limit=climit))
records['practice_actor_period'].append(dict(contribution_id=cid,valid_from='2024-01-17',valid_to='2024-01-17',
    identity_passage_id=authority))
task('practice_contribution',cid,contribution_text,climit)
task('practice_contribution.finding_id',cid,contribution_text,climit)
rid = stem+'-relation'
result = stem+'-result'
expl = stem+'-explanation'
compare = 'Ekim 2023 huzurevleri araştırması ve Ocak 2024 gündeme alma girişimi aynı 10/437 önergesine ilişkin.'
outcome = 'Genel Kurul 17 Ocak 2024’te 10/437’nin o gün görüşülmesi önerisini kabul etmedi.'
connection = ('İYİ Parti milletvekilleri yaşlıların yaşam koşulları ve huzurevi hizmetlerini araştırmayı istedi. '
              'İYİ Parti Grubunun 17 Ocak gündeme alma önerisi kabul edilmedi. '
              'Erişilen 10/437 dosya durumu Gündemde.')
finding(result,outcome,[summary+'topic',summary+'result'],'Gündem sonucunun kapsadığı işlem TBMM tam tutanağıyla doğrulandı.')
finding(expl,connection,[signed+'quote',signed+'condition',session+'proposal',summary+'result',proposal+'status'],
    'İmzalı araştırma gerekçesi, gündem sonucu ve sonraki dosya durumu ayrı kaynaklardan.')
records['practice_relation'].append(dict(id=rid,statement_id=st,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=expl,temporal_context='12 Ekim araştırma önergesi ve 17 Ocak gündeme alma oylaması ayrı.',
    authority_context='Araştırma 20 milletvekili imzasıyla sunuldu. 17 Ocak gündem önerisini İYİ Parti Grubu verdi.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
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
for name,content in [('aged-draft.json',package),('aged-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
