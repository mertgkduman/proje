"""Record the 2/3778 filing and the separate 10/4625 agenda decision."""

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
aux=read(here/'staj-agenda-source-records.json')
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
        aid=f'staj-agenda-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='TBMM birleşim tutanağı ve ilgili işlem belgeleri.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'yeni-yol'
topic = 'sosyal-guvenlik'
bill, register, inquiry, inquiry_register, floor, summary = (
    '0408-staj-agenda-'+label+'-' for label in
    ('bill','bill-register','inquiry','inquiry-register','floor','summary')
)
july = '0408-yeni-yol-2026-3778'
october = '0408-yeni-yol-2026-4625'
july_limit = ('TBMM 2/3778 dosyasını Komisyonda gösteriyor. Yürürlüğe giren bir düzenleme, '
              'uygulama veya hak sahipliği sonucu için ayrı kanıt gerekiyor.')
july_evidence = [
    (bill+'identity','initiative','document','İmzalı üst yazı Selçuk Özdağ’ın Grup Başkanvekili sıfatını gösteriyor.'),
    (bill+'target','initiative','document','Gerekçe geçmiş staj, çıraklık ve eğitim sürelerinin sigorta başlangıcında değerlendirilmesini öneriyor.'),
    (bill+'window','initiative','document','4. madde geçmiş süreler için üç ay içinde talep ve geriye dönük borçlanma koşulu öneriyor.'),
    (register+'filed','action','document','TBMM 2/3778 dosyasının Başkanlığa gelişini 21 Temmuz olarak kaydetti.'),
    (register+'commission','result','document','Esas ve tali komisyon girişleri 22 Temmuz olarak kayda geçti.'),
    (register+'pending','result','document','TBMM’nin erişilen işlem satırı Komisyonda.'),
]
july_event = event(july,'2026-07-21','2/3778 staj ve çıraklık sigortası teklifi',
    'Selçuk Özdağ 5510 sayılı Kanun’da uzun vadeli sigortayı değiştiren teklifi TBMM’ye sundu.',
    july_evidence,july_limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-4-2-3778-filing',
    occurrence_basis='TBMM’nin kanun teklifi dosyası ve imzalı özgün teklif.')
july_refs = [r[0] for r in july_evidence]
july_scope = readings(topic,'event',july_refs+[
    bill+'stamp',bill+'bill-date',bill+'options',register+'owner',register+'id',
])

july_reason = ('2/3778 imzalı teklif, bu karşılaştırmanın ilk tarihli söylem kaynağı. '
               'Tekliften önce bu düzenleme için ayrıca tarihli Yeni Yol açıklaması araştırmaya açık.')
records['practice_candidate'].append(dict(id=july+'-unmatched',scope_id=july_scope,event_id=july_event,
    relation_id=None,state='unmatched',reason=july_reason,passage_ids=encoded(july_refs)))
task('practice_candidate',july+'-unmatched',july_reason,july_limit)

statement, target, quote = (july+ending for ending in ('-statement','-target','-quote'))
goal = ('Selçuk Özdağ, belirli kısa vadeli sigortalıların uzun vadeli sigorta kapsamına girebilmesini, '
        'geçmiş çıraklık, staj ve eğitim sürelerinin borçlanmayla değerlendirilebilmesini önerdi.')
statement_refs=[bill+'target',bill+'options',bill+'window',register+'filed',register+'owner']
finding(target,goal,statement_refs,'İmzalı 2/3778 gerekçesi ile geçici madde ve ilk imza kaydı okundu.')
finding(quote,passages[bill+'target']['exact'],[bill+'target'],
        'İmzalı 2/3778 belgesinin gerekçe sayfası görsel okundu.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-07-21',date_precision='day',
    version_id=passages[bill+'target']['version_id'],period_basis='21 Temmuz 2026 tarihli imzalı 2/3778 gerekçesi.',
    uncertainty_reason='Teklif ilk imza sahibinin yazılı yasama girişimi.',
    comparison_row_id='04-03-v3-0307-yeni-yol-sosyal-guvenlik-program'))
readings(topic,'statement',statement_refs)
for kind, claim in (
    ('practice_statement',goal),
    ('practice_statement.summary_finding_id',goal),
    ('practice_statement.quote_finding_id',passages[bill+'target']['exact']),
):
    task(kind,statement,claim,july_limit)

context = ('CHP Grubu 10/4625’in 20 Ekim birleşiminde ön görüşmeye alınmasını önerdi. '
           'Genel Kurul grup önerisini kabul etmedi.')
limit = ('İmzalı dilekçe 7 Ekim. TBMM esas kaydı Başkanlığa geliş gününü 8 Ekim ve durumu Gündemde gösteriyor. '
         '20 Ekim ret kararı o günkü ön görüşme önerisine ait. İsimli oy ve esas dosyanın sonraki sonucu açık.')
evidence = [
    (inquiry+'id','initiative','document','İmzalı araştırma dosyasının esas numarası 10/4625.'),
    (inquiry_register+'filed','initiative','document','TBMM dosya geliş tarihini 8 Ekim olarak gösteriyor.'),
    (floor+'call','action','document','CHP Grubu staj ve çıraklık araştırmasını 20 Ekim’de ön görüşmeye almayı önerdi.'),
    (floor+'role','action','document','Elif Esen bu gündem maddesinde Yeni Yol Grubu adına konuştu.'),
    (floor+'decision','result','document','Başkan CHP’nin ön görüşme önerisinin reddini ilan etti ve DEM grup önerisine geçti.'),
    (summary+'decision','result','document','Özet aynı gün ön görüşme tekliflerinin kabul edilmediğini kaydetti.'),
]
eid = event(october,'2026-10-20','10/4625 araştırma önergesinin 20 Ekim’de görüşülmesi',context,evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-5-008-10-4625-gundem',
    occurrence_basis='TBMM önergesi, birleşim tutanağı ve ilgili işlem belgeleri.')
refs = [item[0] for item in evidence]
scope = readings(topic,'event',refs+[inquiry+'models',inquiry_register+'pending',floor+'supports',summary+'call'])


def contribution(stem, event_id, person_id, day, kind, authority, claim, support, limit):
    actor, cid, fid = (stem+ending for ending in ('-actor','-contribution','-finding'))
    assert any(e['kind']=='person' and e['values']['id']==person_id for e in entries)
    new('actor',id=actor,kind='authorized_representative',party_id=party,
        person_id=person_id,authorization_passage_id=authority)
    finding(fid,claim,[authority,*support],limit)
    records['practice_contribution'].append(dict(id=cid,event_id=event_id,party_id=party,actor_id=actor,
        contribution_kind=kind,finding_id=fid,authority_passage_id=authority,membership_passage_id=None,
        responsibility_limit=limit))
    records['practice_actor_period'].append(dict(contribution_id=cid,valid_from=day,valid_to=day,
        identity_passage_id=authority))
    for key in ('practice_contribution','practice_contribution.finding_id'):
        task(key,cid,claim,limit)


contribution(july,july_event,'0408-yeni-yol-2026-3940-person','2026-07-21','task',bill+'identity',
    'Yeni Yol Grup Başkanvekili Selçuk Özdağ 2/3778’i ilk imza sahibi olarak sundu.',
    [register+'owner',register+'filed'],july_limit)
contribution(october,eid,'0408-elif-esen-person','2026-10-20','support',floor+'role',
    'Elif Esen, CHP’nin staj ve çıraklık araştırmasının ön görüşmesine Yeni Yol Grubu adına destek verdi.',
    [floor+'supports',floor+'call'],limit)

result, explanation, rid = (october+ending for ending in ('-result','-explanation','-relation'))
outcome = context+' TBMM esas dosyasında durum Gündemde.'
comparison = ('2/3778 uzun vadeli sigorta ve borçlanma hükümleri öneriyor. Elif Esen’in desteklediği '
              '10/4625 ön görüşme önerisi aynı sosyal güvenlik sorununu Mecliste araştırmaya yönelik.')
finding(result,outcome,[floor+'call',floor+'decision',summary+'decision',inquiry_register+'pending'],
        '20 Ekim ayrı oylaması, birleşim özeti ve esas dosyası karşılaştırıldı.')
finding(explanation,comparison+' '+outcome+' '+limit,statement_refs+refs+[inquiry+'models',floor+'supports'],limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,
    topic_id=topic,scope_id=scope,comparability_reason=comparison,target_finding_id=target,
    result_finding_id=result,explanation_finding_id=explanation,
    temporal_context='21 Temmuz 2/3778 başvurusu, 7 Ekim imzalı araştırma dilekçesi, 8 Ekim TBMM girişi ve 20 Ekim gündem oylaması.',
    authority_context='2/3778 ilk imza sahibi Özdağ. 10/4625 CHP araştırma dosyası. Esen birleşimde Yeni Yol Grubu adına konuştu.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=october+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=comparison,passage_ids=encoded(refs)))
for kind, claim in (
    ('practice_relation',comparison+' '+outcome),
    ('practice_relation.target_finding_id',goal),
    ('practice_relation.result_finding_id',outcome),
    ('practice_relation.explanation_finding_id',comparison),
):
    task(kind,rid,claim,limit)

for entry in entries:
    destination=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in destination:
        destination.append(entry['values'])
for table,rows in records.items():
    destination=snapshot.setdefault(table,[])
    destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot, records, [entry['values']['id'] for entry in entries if entry['kind']=='passage'], party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limitation,result='reviewed',
        reason=kind+' hedefinin kaynak metni, tarihi ve iddia sınırları okundu. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('staj-agenda-v2-draft.json',package),('staj-agenda-v2-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
