"""Compare the 2/4007 proposal with the earlier archived policy."""

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
aux=read(here/'staj-4007-source-records.json')
party=aux['party_id']
package=read(data/'practices/04-demokrat.json')
review=read(data/'practices/04-demokrat-review.json')
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
        aid=f'staj-4007-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='TBMM’nin kanun teklifi dosyası ve imzalı özgün teklif.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'demokrat'
topic = 'sosyal-guvenlik'
stem = '0412-demokrat-2026-2-4007'
anchor = '0412-staj-4007-'
program = '0412-staj-4007-program'
program_version = '0210-demokrat-program-archive-v1'
program_context = program+'-context'
program_exact = 'sosyal güvenlik uygulamalarından\ntüm vatandaşların eşit ve adil olarak hizmetlere kolay ve sorunsuz\nulaşabilmesi için gerekli düzenlemeler yapacaktır.'
program_section = '4- Sosyal Güvenlik ve İnsanımız'
new('passage',id=program,version_id=program_version,exact=program_exact,prefix=None,suffix=None,
    article=None,section=program_section,pdf_page_index=68,printed_page='75')
passages[program]=entries[-1]['values']
new('passage',id=program_context,version_id=program_version,exact='gençler, ilk defa işe girecekler, uzun\nsüreli işsizler, düşük vasıflı, yaşlı ve özürlüler gibi grupların isti-\nhdamlarının arttırılmasına yönelik vergi ve sosyal güvenlik düzen-\nlemeleri gözden geçirilecektir.',prefix=None,suffix=None,
    article=None,section=program_section,pdf_page_index=68,printed_page='75')
passages[program_context]=entries[-1]['values']
statement,target,quote=(stem+tail for tail in ('-statement','-target','-quote'))
goal = ('Demokrat Parti’nin arşiv programı sosyal güvenlik hizmetlerine eşit ve adil erişim için düzenleme '
        'yapılmasını öngörüyor. Gençler ve ilk kez işe girecekler için sosyal güvenlik düzenlemelerini de anıyor.')
statement_limit = ('Program 29 Aralık 2021’de arşivlendi. Kabul tarihi ve teklif günündeki yürürlük durumu açık. '
                   'İncelenen program bölümü staj ve çıraklık için ayrı bir başlangıç veya borçlanma hükmü belirtmiyor.')
finding(target,goal,[program,program_context],statement_limit)
finding(quote,program_exact,[program],statement_limit,pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at=None,date_precision='unknown',
    version_id=program_version,period_basis='Program nüshası 29 Aralık 2021’de arşivlendi.',
    uncertainty_reason=statement_limit,comparison_row_id='04-03-v3-0313-demokrat-sosyal-guvenlik'))
readings(topic,'statement',[program,program_context])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',program_exact)):
    task(kind,statement,claim,statement_limit)

context = ('Demokrat Parti İzmir Milletvekili Haydar Altıntaş’ın 2/4007 teklifi 3 Kasım 2026’da '
           'TBMM’ye ulaştı. 4 Kasım’da ilgili komisyonlara girdi.')
limit = ('Özgün teklif yazısı 2 Kasım, evrak kaydı 3 Kasım ve komisyon girişleri 4 Kasım tarihli. '
         'Erişilen dosyada durum Komisyonda. Yasalaşma ve fiilî sonuç açık.')
evidence = [
    (anchor+'detail-id','initiative','document','TBMM esas numarasını 2/4007 olarak kaydetti.'),
    (anchor+'detail-filed','initiative','document','Başkanlığa geliş günü 3 Kasım 2026.'),
    (anchor+'detail-membership','initiative','document','İlk imza Haydar Altıntaş, Demokrat Parti İzmir.'),
    (anchor+'signed-signature','initiative','document','İmzalı yazı 2 Kasım tarihli.'),
    (anchor+'signed-stamp','initiative','document','TBMM evrak kaşesi 3 Kasım tarihli.'),
    (anchor+'signed-thresholds','initiative','document','Madde 1 farklı gruplar için net asgari ücretin yüzde 50 ve yüzde 40’ı oranlarında alt sınır öneriyor.'),
    (anchor+'signed-start','initiative','document','Madde 1 uzun vadeli sigorta ve ilk sigortalılık başlangıcına ilişkin hüküm öneriyor.'),
    (anchor+'signed-safety','initiative','document','Madde 2 ilgili işletmelerde yılda en az iki iş güvenliği denetimi öneriyor.'),
    (anchor+'signed-backdate','initiative','document','Madde 3 talep edenlerin geçmiş süreleri borçlanmasını öneriyor.'),
    (anchor+'detail-committee','action','document','Komisyon giriş tarihi 4 Kasım olarak kaydedildi.'),
    (anchor+'detail-pending','action','document','Erişilen komisyon işlemi Komisyonda.'),
]
eid=event(stem,'2026-11-03','Altıntaş’ın 2/4007 mesleki eğitim teklifi',context,evidence,limit)
records['practice_event'][-1]['common_event_key']='tbmm-28-5-2-4007-basvuru'
refs=[row[0] for row in evidence]
scope=readings(topic,'event',refs+[anchor+'signed-file'])
rid,explanation=(stem+tail for tail in ('-relation','-explanation'))
compare = ('Arşiv programı ilk kez iş hayatına girenlerin de yer aldığı gruplar için sosyal güvenlik düzenlemelerini '
           'gözden geçirmeyi öngörüyor. 2/4007 belirli staj ve çıraklık gruplarının sigorta başlangıcına yönelik araçlar öneriyor.')
explanation_text = ('2/4007, kapsamındaki kişilerin ilk sigortalılık başlangıcını ve koşullu geriye dönük borçlanmayı '
                    'düzenlemeyi öneriyor. Ücret ve iş güvenliği maddeleri ayrı. 4 Kasım’da komisyon girişleri kaydedildi. '+limit)
finding(explanation,explanation_text,[program,program_context,*refs],limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=None,
    explanation_finding_id=explanation,temporal_context='2021 arşiv nüshası, 2 Kasım 2026 yazı, 3 Kasım geliş, 4 Kasım komisyon girişi.',
    authority_context='TBMM imza tablosunda Altıntaş ilk imza sahibi. Komisyon girişleri TBMM işlem kaydı.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',explanation_text),('practice_relation.target_finding_id',goal),
                   ('practice_relation.explanation_finding_id',explanation_text)):
    task(kind,rid,claim,limit)

for entry in entries:
    destination=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in destination:
        destination.append(entry['values'])
for table,rows in records.items():
    destination=snapshot.setdefault(table,[])
    destination.extend(row for row in rows if row not in destination)
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
        reason=kind+' hedefinin kaynak, tarih ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('staj-4007-draft.json',package),('staj-4007-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
