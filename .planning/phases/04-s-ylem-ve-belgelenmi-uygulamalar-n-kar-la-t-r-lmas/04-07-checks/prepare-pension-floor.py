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
aux=read(here/'pension-floor-source-records.json')
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
        aid=f'pension-floor-reading-{lane}-{topic}-{vid}'
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
topic = 'sosyal-guvenlik'
stem = '0407-iyi-2026-7573'
p = '0407-floor-'
before = p+'iyi-7573-49-'
vote = p+'iyi-7573-50-'
bill = p+'pension-bill-23464-'
law = p+'pension-law-7573-'
text = p+'pension-text-7573-'
st = stem+'-statement'
target = stem+'-target'
quote = stem+'-quote'
goal = ('Erhan Usta, İYİ Parti Grubu adına en düşük emekli aylığının asgari ücret düzeyinde olmasını parti politikası olarak açıkladı.')
limit = ('49. Birleşimdeki 25.000 TL önergesi ve 50. Birleşimdeki teklifin tümü üzerindeki açık oy ayrı. '
         'Kesin isimli oy tablosu ve fiilî ödeme kayıtları açık.')
finding(target,goal,[before+'usta',before+'quote'],'49. Birleşimde temsil sıfatı ve alt aylık eşiği aynı konuşmada kontrol edildi.')
finding(quote,passages[before+'quote']['exact'],[before+'quote'],
    'Tutanakta yer alan kısa birebir politika ifadesi.',pair=target)
records['practice_statement'].append(dict(id=st,party_id=party,topic_id=topic,taxonomy_version=4,
   summary_finding_id=target,quote_finding_id=quote,statement_at='2026-01-21',date_precision='day',
   version_id=passages[before+'quote']['version_id'],period_basis='21 Ocak tarihli 49. Birleşimde İYİ Parti Grubu adına konuşma.',
   uncertainty_reason=None,comparison_row_id='04-03-v3-0306-iyi-program-sosyal-guvenlik-row'))
readings(topic,'statement',[before+'usta',before+'quote',before+'committee'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[before+'quote']['exact'])):
    task(kind,st,claim,'Genel Kurul konuşması, komisyon işlemini Usta’nın anlattığı kapsamla gösteriyor.')
evidence = [
    (bill+'id','initiative','document','2/3464 esas numaralı teklif TBMM kaydında.'),
    (before+'amendment','initiative','document','49. Birleşimde 20.000 TL yerine 25.000 TL yazılması önerildi.'),
    (before+'signers','initiative','document','Bu Genel Kurul önergesinde altı milletvekilinin adı var.'),
    (vote+'accept','action','document','50. Birleşim Başkanı teklifin tümü üzerinde kabulü açıkladı.'),
    (vote+'tally','result','document','Tutanakta 426 oyun 247’si kabul ve 179’u ret olarak açıklandı.'),
    (law+'day','result','document','TBMM kanun kaydında kabul günü 23 Ocak 2026.'),
    (bill+'law','result','document','2/3464 yasama kaydı 7573 sayılı kanuna bağlı.'),
    (text+'floor','result','document','7573 sayılı kanunun 7. maddesi 16.881 TL yerine 20.000 TL belirliyor.'),
    (text+'effect','result','document','7. madde Ocak 2026 ödeme döneminden itibaren uygulanmak üzere düzenlendi.'),
]
eid = event(stem,'2026-01-23','2/3464’ten çıkan 7573 sayılı kanunda en düşük emekli aylığı',
    'TBMM 2/3464 teklifini kabul etti. 7573 sayılı kanunun 7. maddesinde 20.000 TL tutarı yer aldı.',evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-4-050-2-3464-7573',
    occurrence_basis='50. Birleşim tutanağı, 2/3464 yasama kaydı ve 7573 sayılı kanun metni.')
refs = [row[0] for row in evidence]
scope = readings(topic,'event',[*refs,before+'defense',before+'rejection',vote+'close',law+'session'])
rid = stem+'-relation'
result = stem+'-result'
exp = stem+'-explanation'
compare = 'İYİ Parti beyanı, 25.000 TL değişiklik önerisi ve 7573 sayılı kanunun 7. maddesi aynı aylık ödeme alt sınırına ilişkin.'
outcome = ('TBMM 23 Ocak 2026’da teklifi 247 kabul ve 179 ret ile kabul etti. 7. madde, 20.000 TL tutarını '
           'Ocak 2026 ödeme döneminden itibaren geçerli olacak şekilde düzenledi.')
explanation = ('Erhan Usta asgari ücret eşiğini parti politikası olarak açıkladı. Genel Kurul 25.000 TL değişiklik '
               'önergesini kabul etmedi. 2/3464’ten çıkan 7573 sayılı kanunda 20.000 TL uygulanması öngörüldü.')
finding(result,outcome,[vote+'tally',vote+'accept',law+'day',text+'floor',text+'effect'],
    'Açıklanan oy sayısı, kanun kimliği ve yürürlük hükmü ilgili özgün kayıtlarda okundu.')
finding(exp,explanation,[before+'quote',before+'amendment',before+'signers',before+'rejection',text+'floor'],
    'Parti politikasının tutanağı, ayrı değişiklik önergesi ve kabul edilen hüküm birlikte karşılaştırıldı.')
records['practice_relation'].append(dict(id=rid,statement_id=st,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,
    comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=exp,
    temporal_context='49. Birleşim asgari ücret açıklaması ve 25.000 TL önergesini içeriyor. TBMM kabulü 23 Ocak olarak kaydetti.',
    authority_context='Usta İYİ Parti Grubu adına konuştu. Genel Kurul önergesinde altı imza var. TBMM teklifin tümünü oyladı.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',explanation),('practice_relation.target_finding_id',goal),
                   ('practice_relation.result_finding_id',outcome),('practice_relation.explanation_finding_id',explanation)):
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
for name,content in [('pension-floor-draft.json',package),('pension-floor-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
