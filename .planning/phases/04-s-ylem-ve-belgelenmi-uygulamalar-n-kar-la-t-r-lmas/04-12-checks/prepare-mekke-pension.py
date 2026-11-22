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
aux=read(here/'mekke-pension-source-records.json')
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
        aid=f'mekke-pension-reading-{lane}-{topic}-{vid}'
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
assert party == 'demokrat'
base = '0412-policy-'
stem = '0412-demokrat-2026-mekke'
topic = 'dis-politika'
speech = base+'altintas-mekke-'
vote = base+'shared-ballot-vote'
tallies = [base+'shared-ballot-'+key for key in ('yes','no','duplicates')]
bill = base+'shared-bill-id'
st = stem+'-statement'
target = stem+'-target'
target_text = 'Haydar Altıntaş, 5 Kasım 2026’da Genel Kurulda Demokrat Parti olarak Mekke Anlaşmasına ret oyu vereceklerini söyledi.'
limit = ('Konuşma Demokrat Parti adına ifade edilen tutumu gösteriyor. Cetvel bireysel oyu kaydediyor. '
         '14 Kasım Resmî Gazete yayımı, 10 Kasım araştırma kesiminden sonra.')
finding(target,target_text,[speech+'speaker',speech+'quote',speech+'grounds'],
    'Özgün konuşmanın kimliği, bağlamı ve Demokrat Parti’ye atfı okundu.')
finding(stem+'-quote',passages[speech+'quote']['exact'],[speech+'quote'],
    'Genel Kurul tutanağındaki birebir cümle.',pair=target)
records['practice_statement'].append(dict(id=st,party_id=party,topic_id=topic,taxonomy_version=4,
   summary_finding_id=target,quote_finding_id=stem+'-quote',statement_at='2026-11-05',date_precision='day',
   version_id=passages[speech+'quote']['version_id'],
   period_basis='TBMM 14. Birleşim, 5 Kasım 2026, açık oylama öncesindeki konuşma.',
   uncertainty_reason=None,comparison_row_id='04-03-v3-0313-demokrat-dis-politika'))
readings(topic,'statement',[speech+'speaker',speech+'quote',speech+'grounds'])
for kind,claim in (('practice_statement',target_text),('practice_statement.summary_finding_id',target_text),
                   ('practice_statement.quote_finding_id',passages[speech+'quote']['exact'])):
    task(kind,st,claim,limit)
evidence = [
    (bill,'initiative','document','TBMM kaydında teklif esas numarası 2/3961.'),
    (vote,'action','document','Demokrat Parti etiketli Haydar Altıntaş satırında saat 23.49.42 ret oyu kayıtlı.'),
    (tallies[0],'result','document','TBMM açık oy cetvelinde kabul oyları 277.'),
    (tallies[1],'result','document','TBMM açık oy cetvelinde ret oyları 118.'),
    (tallies[2],'result','document','Üç mükerrer oy cetvelde ayrı satırda.'),
]
eid = event(stem,'2026-11-05','2/3961 Mekke Anlaşması onay teklifinin açık oylaması',
    'TBMM 14. Birleşim açık oylamasında 2/3961 teklifi kabul edildi.',evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-5-014-2-3961-mekke-7597',
    occurrence_basis='TBMM 2/3961 yasama kaydı ve 14. Birleşim isimli açık oy cetveli.')
refs = [row[0] for row in evidence]
scope = readings(topic,'event',refs+[speech+'authority'])
person = stem+'-altintas-person'
actor = stem+'-altintas-representative'
cid = stem+'-altintas-contribution'
cf = stem+'-altintas-finding'
auth = speech+'authority'
new('person',id=person,name='HAYDAR ALTINTAŞ')
new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,authorization_passage_id=auth)
contribution = target_text + ' Cetvelde Altıntaş saat 23.49.42’de ret oyu verdi.'
finding(cf,contribution,[auth,speech+'quote',vote],
    'Konuşmacı ile Demokrat Parti adına beyan aynı tutanakta, adla kayıtlı oy farklı cetvelde okundu.')
records['practice_contribution'].append(dict(id=cid,event_id=eid,party_id=party,actor_id=actor,
    contribution_kind='objection',finding_id=cf,authority_passage_id=auth,membership_passage_id=None,
    responsibility_limit=limit))
records['practice_actor_period'].append(dict(contribution_id=cid,valid_from='2026-11-05',valid_to='2026-11-05',
    identity_passage_id=speech+'speaker'))
task('practice_contribution',cid,contribution,limit)
task('practice_contribution.finding_id',cid,contribution,limit)
rid=stem+'-relation'
expl=stem+'-explanation'
result=stem+'-result'
compare = 'Altıntaş’ın Demokrat Parti adına konuşması ile açık oy, aynı 2/3961 teklifine ilişkin.'
connection = 'Altıntaş tutanakta Demokrat Parti adına ret açıklaması yaptı. Cetveldeki kendi oyu ret. TBMM teklifi kabul etti.'
outcome = 'TBMM, 2/3961 teklifini 277 kabul ve 118 ret oyuyla kabul etti. Üç mükerrer oy ayrı kayıtlı.'
finding(expl,connection,[speech+'quote',speech+'speaker',vote,*tallies],
    'Beyan, bireysel oy ve toplam karar satırları ayrı kaynaklara bağlandı.')
finding(result,outcome,tallies,'Açık oy cetveli toplam ve mükerrer oy satırlarıyla okundu.')
records['practice_relation'].append(dict(id=rid,statement_id=st,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,
    comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=expl,
    temporal_context='5 Kasım konuşması ve açık oyu ayrı aşamalar. 14 Kasım yayımı kesim sonrasında.',
    authority_context='Konuşmada Demokrat Parti adına tutumu bildiren Altıntaş. Bireysel açık oy ayrı.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',connection),('practice_relation.target_finding_id',target_text),
                   ('practice_relation.result_finding_id',outcome),('practice_relation.explanation_finding_id',connection)):
    task(kind,rid,claim,limit)

topic = 'sosyal-guvenlik'
stem = '0412-demokrat-2026-2-3489'
bill = base+'dp-3489-'
signed = bill+'signed-'
press = base+'dp-retirement-press-'
limit = ('Demokrat Parti’nin 29 Ocak açıklaması komisyona sevkten sonra. Erişilen TBMM kaydında Komisyonda yazıyor. '
         'Yasama sonucu ve ödeme uygulaması araştırılıyor.')
summary = 'Haydar Altıntaş’ın 2/3489 teklifi, belirli emeklilerin ek ödemesini 2.345 gösterge ve memur maaş katsayısının çarpımına bağlamayı önerdi.'
evidence = [
    (bill+'id','initiative','document','2/3489 esas numarası TBMM teklif kaydında.'),
    (bill+'submitted','initiative','document','TBMM Başkanlığına geliş 22 Ocak 2026.'),
    (signed+'signature','initiative','document','Üst yazı Haydar Altıntaş imzalı.'),
    (signed+'basis','initiative','document','Gerekçede makam, görev veya temsil tazminatı almayan ilgili emekliler sayılıyor.'),
    (signed+'proposal','initiative','document',summary),
    (bill+'assigned','action','document','23 Ocak 2026 esas ve tali komisyon giriş kaydı.'),
]
eid = event(stem,'2026-01-23','2/3489 emekli ek ödemesi teklifinin komisyona sevki',summary,evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-4-2-3489-komisyona-sevk',
    occurrence_basis='TBMM imzalı teklif, geliş kaydı ve esas/tali komisyon tarihleri.')
refs = [row[0] for row in evidence]
scope = readings(topic,'event',refs+[bill+'status',bill+'initial',press+'role',press+'amount'])
stscope = readings(topic,'statement',[press+'role',press+'amount'])
why = ('Arşivli program emekli haklarının iyileştirilmesini genel hedef olarak belirtiyor. 29 Ocak parti açıklaması '
       'sevkten sonra. Aynı ödeme grubu ve göstergeyi önceleyen açıklama aranıyor.')
cid=stem+'-candidate'
records['practice_candidate'].append(dict(id=cid,scope_id=scope,event_id=eid,relation_id=None,
    state='unmatched',reason=why,passage_ids=encoded(refs)))
task('practice_candidate',cid,why,limit)
records['practice_attempt_v2'].append(dict(id=stem+'-dated-statement-search',scope_id=stscope,
    attempted_at=when,query='site:dp.org.tr Haydar Altıntaş 2345 Ek 81 emekli asker polis MİT teklif',
    url=None,result='results',source_version_id=None,
    reason='Parti yayını 29 Ocak 2026 tarihli ve 23 Ocak komisyon girişinden sonra. Daha eski aynı ölçüt ve ödeme grubu açık.'))
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
for name,content in [('mekke-pension-draft.json',package),('mekke-pension-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
