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
aux=read(here/'pension-age-source-records.json')
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
        aid=f'pension-age-reading-{lane}-{topic}-{vid}'
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
assert party == 'saadet'
topic = 'sosyal-guvenlik'
stem = '0411-saadet-2024-2-1998'
st = stem+'-statement'
target = stem+'-target'
charter = '0311-saadet-p2-071-sosyal-guvenlik-p'
bill = '0411-pension-arikan-1998-'
pdf = bill+'signed-'
target_text = ('Saadet’in 2019 kapaklı programı emeklilikte prim günü ve yaş çelişkisinin giderilmesini, '
               'farklı emeklilik seçenekleri kurulmasını öngörüyor.')
limit = ('2/1998 belirli sigortalı gruplarını ve 8 Eylül 1999–30 Nisan 2008 giriş aralığını kapsıyor. '
         'Erişilen kayıtta Komisyonda yazıyor. Teklifin yasama sonucu ve fiilî uygulaması açık.')
finding(target,target_text,[charter],'2019 kapaklı programın sosyal güvenlik bölümü okundu.')
finding(stem+'-quote',passages[charter]['exact'],[charter],
    'Programın prim günü ve yaş koşullarına ilişkin birebir pasajı.',pair=target)
records['practice_statement'].append(dict(id=st,party_id=party,topic_id=topic,taxonomy_version=4,
   summary_finding_id=target,quote_finding_id=stem+'-quote',statement_at='2019-11-03',date_precision='day',
   version_id=passages[charter]['version_id'],
   period_basis='Arşivli program nüshasının kapağında 3 Kasım 2019 yazıyor.',
   uncertainty_reason='Programın başlangıç ve bitiş yürürlük günleri ayrı doğrulama gerektirir.',
   comparison_row_id='04-03-v3-0311-saadet-sosyal-guvenlik'))
readings(topic,'statement',[charter])
for kind,claim in (('practice_statement',target_text),
                   ('practice_statement.summary_finding_id',target_text),
                   ('practice_statement.quote_finding_id',passages[charter]['exact'])):
    task(kind,st,claim,'Kaynak genel program hedefi içeriyor. Teklifin kapsam ve prim koşulları ayrı kaynakta.')
evidence = [
    (pdf+'signature','initiative','document','Teklifin imzalı üst yazısı 30 Ocak 2024 tarihli.'),
    (bill+'submitted','initiative','document','TBMM Başkanlığına geliş 7 Şubat 2024.'),
    (bill+'id','initiative','document','TBMM kaydında esas numarası 2/1998.'),
    (pdf+'period','initiative','document','1. madde belli gruplar için 8 Eylül 1999–30 Nisan 2008 dönemini kapsıyor.'),
    (pdf+'age','initiative','document','Teklif belirli gruplarda 45 yaş ve 9.000 prim günü seçeneği öngörüyor.'),
    (pdf+'partial','initiative','document','Kısmi yaşlılık aylığı için bazı gruplarda 15 tam yıl prim öngörülüyor.'),
    (pdf+'coefficient','initiative','document','2. madde güncelleme katsayısının hesaplanmasını ayrıca değiştiriyor.'),
    (bill+'referred','action','document','TBMM kaydında 8 Şubat 2024’te esas ve tali komisyona giriş var.'),
]
eid = event(stem,'2024-02-08','2/1998 emeklilik koşulları teklifinin komisyona sevki',
    'Saadet milletvekili Mahmut Arıkan’ın belirli sigortalılık gruplarına ilişkin teklifi komisyona sevk edildi.',evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-2-2-1998-komisyona-sevk',
    occurrence_basis='İmzalı teklif, geliş günü ve iki komisyona girişin bulunduğu TBMM kaydı.')
refs = [row[0] for row in evidence]
scope = readings(topic,'event',[*refs,bill+'status',bill+'initial',pdf+'receipt'])
rid = stem+'-relation'
expl = stem+'-explanation'
compare = 'Program ve teklif yaş ile prim günü koşullarını birlikte ele alıyor.'
connection = ('Saadet programı yaş ve prim günü koşullarının yeniden düzenlenmesini öngörüyor. '
              '2/1998 belirli dönem sigortalıları için yeni yaş ve prim seçenekleri önerdi. '
              'Komisyon kararının ve yasalaşmanın belgesi araştırılıyor.')
finding(expl,connection,[charter,pdf+'period',pdf+'age',pdf+'partial',bill+'referred',bill+'status'],
    'Program hükmü, teklifin kapsamı ve Meclis işlem aşaması ayrı okundu.')
records['practice_relation'].append(dict(id=rid,statement_id=st,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=None,explanation_finding_id=expl,
    temporal_context='2019 kapaklı programın ardından Şubat 2024 geliş ve sevk kaydı.',
    authority_context='Mahmut Arıkan ilk imza sahibi. Meclis kaydı teklifin komisyona sevkini gösteriyor.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',connection),('practice_relation.target_finding_id',target_text),
                   ('practice_relation.explanation_finding_id',connection)):
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
for name,content in [('pension-age-draft.json',package),('pension-age-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
