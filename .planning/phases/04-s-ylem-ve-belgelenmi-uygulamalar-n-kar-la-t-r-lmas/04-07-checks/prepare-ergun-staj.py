"""Record 2/1019 and the distinct 10/4625 preliminary agenda decision."""

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
aux=read(here/'ergun-staj-source-records.json')
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
        aid=f'ergun-staj-reading-{lane}-{topic}-{vid}'
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
assert party == 'iyi'
topic = 'sosyal-guvenlik'
base = '0407-ergun-staj-'
bill, register, conflict, end, inquiry, inquiry_register, floor, summary = (
    base+label+'-' for label in ('1019-signed','1019-detail','1019-oct','1019-end',
                                'inquiry','inquiry-register','floor','summary')
)
older = '0407-iyi-2018-1019'
october = '0407-iyi-2026-4625'
old_limit = ('Teklif yazısı ve TBMM evrak kaşesi 17 Eylül 2018 tarihli. TBMM esas dosyası 17 Eylül, '
             '16 Ekim tutanağındaki Gelen Kâğıtlar bölümü 14 Eylül geliş kaydediyor. Komisyon girişleri 15 Ekim. '
             'Hükümsüzlük sonraki dönem kaydında doğrulanıyor, kesin işlem günü açık.')
old_evidence = [
    (bill+'signature','initiative','document','İmzalı 2/1019 yazısı 17 Eylül 2018 tarihli.'),
    (bill+'stamp','initiative','document','Özgün dosyadaki gelen evrak kaşesi 17 Eylül 2018.'),
    (register+'ergun','initiative','document','İlk imzalardan biri İYİ Parti Muğla Milletvekili Metin Ergun.'),
    (register+'turkkan','initiative','document','İlk imzalardan diğeri İYİ Parti Kocaeli Milletvekili Lütfü Türkkan.'),
    (bill+'clause','initiative','document','Birinci madde borçlanma halinde staj veya çıraklık başlangıcını esas almayı öneriyor.'),
    (register+'filed','action','document','TBMM esas dosyasının geliş günü alanı 17 Eylül.'),
    (conflict+'conflict','action','document','16 Ekim tutanağının Gelen Kâğıtlar kaydı aynı 2/1019 için 14 Eylül geliş günü veriyor.'),
    (register+'committee','action','document','Üç komisyona giriş TBMM sicilinde 15 Ekim 2018.'),
    (end+'listing','result','document','28. dönem ilk birleşim ekinde 2/1019 hükümsüz sayılan teklifler içinde 1013. sırada.'),
]
old_context = ('İYİ Parti milletvekilleri Metin Ergun ve Lütfü Türkkan 2/1019 sayılı staj ve çıraklık sigortası '
               'teklifini imzaladı. 17 Eylül tarihli yazı, borçlanma ve sigorta başlangıcı düzenlemesi öneriyor.')
old_event = event(older,'2018-09-17','Ergun ve Türkkan’ın 2/1019 staj sigortası teklifi',old_context,old_evidence,old_limit)
records['practice_event'][-1].update(common_event_key='tbmm-27-2-2-1019-imza',
    occurrence_basis='17 Eylül 2018 tarihli imzalı teklif, TBMM dosyası ve birleşim kayıtları.')
old_refs = [item[0] for item in old_evidence]
old_scope = readings(topic,'event',old_refs+[register+'status'])
old_reason = '2/1019 ilk imzalı girişim. Bu tekliften önce iki imza sahibinin aynı araçları açıklayan tarihli beyanı araştırılıyor.'
records['practice_candidate'].append(dict(id=older+'-unmatched',scope_id=old_scope,event_id=old_event,
    relation_id=None,state='unmatched',reason=old_reason,passage_ids=encoded(old_refs)))
task('practice_candidate',older+'-unmatched',old_reason,old_limit)

statement, target, quote = (older+ending for ending in ('-statement','-target','-quote'))
goal = ('Metin Ergun ve Lütfü Türkkan, çırak veya stajyer öğrenci olarak çalışılan sürelerin '
        'borçlanılabilmesini ve bu çalışmaların ilk gününün uzun vadeli sigortalılık başlangıcı sayılmasını önerdi.')
statement_refs = [bill+'goal',bill+'signature',bill+'clause',register+'ergun',register+'turkkan']
finding(target,goal,statement_refs,'İmzalı 2/1019 belgeleri ve TBMM imza tablosu birlikte okundu.')
finding(quote,passages[bill+'goal']['exact'],[bill+'goal'],
        '2/1019 taramasındaki madde gerekçesi görsel olarak okundu.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2018-09-17',date_precision='day',
    version_id=passages[bill+'goal']['version_id'],period_basis='17 Eylül 2018 tarihli imzalı teklif ve madde gerekçesi.',
    uncertainty_reason='İki İYİ Parti milletvekilinin imzalı yasama girişimi. '+old_limit,
    comparison_row_id='04-03-v3-0306-iyi-program-sosyal-guvenlik-row'))
readings(topic,'statement',statement_refs)
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[bill+'goal']['exact'])):
    task(kind,statement,claim,old_limit)

context = ('CHP Grubu 10/4625’in 20 Ekim birleşiminde ön görüşmeye alınmasını önerdi. '
           'Genel Kurul grup önerisini kabul etmedi.')
limit = ('10/4625 metni 7 Ekim imzalı. TBMM esas kaydında geliş 8 Ekim ve durum Gündemde. '
         '20 Ekim sonucu ön görüşme önerisine ait. Ergun’un beyanı Grup adına destek. '
         'İsimli oy ve araştırma dosyasının sonraki işlemi açık.')
evidence = [
    (inquiry+'id','initiative','document','İmzalı araştırma evrakının esas numarası 10/4625.'),
    (inquiry_register+'filed','initiative','document','Araştırma önergesinin TBMM geliş kaydı 8 Ekim.'),
    (floor+'call','action','document','CHP Grubu 20 Ekim’de araştırma önergesinin ön görüşmesini istedi.'),
    (floor+'role','action','document','Metin Ergun, 10/4625 görüşmesinde İYİ Parti Grubu adına söz aldı.'),
    (floor+'supports','action','document','Ergun gündem önerisine İYİ Parti adına destek açıkladı.'),
    (floor+'decision','result','document','Birleşim Başkanı CHP grup önerisinin kabul edilmediğini açıklayıp DEM gündemine geçti.'),
    (summary+'decision','result','document','Gün özeti görüşmelerden sonra aynı gün ön görüşme taleplerinin reddedildiğini kaydetti.'),
]
eid = event(october,'2026-10-20','10/4625 araştırma önergesinin 20 Ekim’de görüşülmesi',context,evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-5-008-10-4625-gundem',
    occurrence_basis='TBMM önergesi, birleşim tutanağı ve ilgili işlem belgeleri.')
refs = [item[0] for item in evidence]
scope = readings(topic,'event',refs+[inquiry+'models',inquiry_register+'pending',floor+'models',floor+'earlier',summary+'call'])
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


new('person',id='0407-metin-ergun-person',name='Metin Ergun')
contribution(october,eid,'0407-metin-ergun-person','2026-10-20','support',floor+'role',
    'Metin Ergun, 10/4625’in ön görüşmesi için İYİ Parti Grubu adına destek açıkladı.',
    [floor+'supports',floor+'models',floor+'earlier'],limit)

result, explanation, rid = (october+ending for ending in ('-result','-explanation','-relation'))
outcome = context+' TBMM esas dosyası Gündemde.'
comparison = ('2018’de Ergun ve Türkkan borçlanma ve uzun vadeli sigorta başlangıcı için kanun değişikliği önerdi. '
              '2026’da Ergun İYİ Parti Grubu adına aynı sorunu araştıracak önergenin gündeme alınmasını destekledi.')
finding(result,outcome,[floor+'call',floor+'decision',summary+'decision',inquiry_register+'pending'],
        'Ön görüşme oylaması, birleşim özeti ve esas dosyasının aşamaları okundu.')
finding(explanation,comparison+' '+outcome+' '+limit,
        statement_refs+refs+[floor+'models',floor+'earlier'],limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,
    topic_id=topic,scope_id=scope,comparability_reason=comparison,target_finding_id=target,
    result_finding_id=result,explanation_finding_id=explanation,
    temporal_context='17 Eylül 2018 imzalı 2/1019, 7 Ekim 2026 imzalı 10/4625 ve 20 Ekim ön görüşme oylaması.',
    authority_context='Ergun ve Türkkan 2/1019 ilk imza sahipleri. CHP 10/4625 ön görüşme önerisinin sahibi. Ergun İYİ Parti Grubu adına konuştu.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=october+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=comparison,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',comparison+' '+outcome),('practice_relation.target_finding_id',goal),
                   ('practice_relation.result_finding_id',outcome),('practice_relation.explanation_finding_id',comparison)):
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
for name,content in [('ergun-staj-draft.json',package),('ergun-staj-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
