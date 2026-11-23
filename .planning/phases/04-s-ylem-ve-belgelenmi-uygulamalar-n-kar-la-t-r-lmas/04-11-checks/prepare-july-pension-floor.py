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
aux=read(here/'july-pension-floor-source-records.json')
party=aux['party_id']
package=read(here/'private-teacher-meetings-draft.json')
review=read(here/'private-teacher-meetings-review-draft.json')
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
            boundary_reason='Temmuz emekli ödemesinin alt sınırına ilişkin tarihli açıklama ve kanun incelendi.'))
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
        aid=f'july-pension-floor-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='Kanun sicili ve kabul metni birlikte okundu.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='saadet'
topic='sosyal-guvenlik'
stem='0411-saadet-2026-7590-m16'
src='0411-july-pension-'
limitation=('Kanun dosya bazında asgari ödeme tutarını değiştirdi. Kök aylıkların tek tek değişmesi, '
    'hak sahiplerinin banka hesaplarına yatan tutarlar ve Saadet’e ait bir sonuç yetkisi bu kayıtlardan doğrulanamadı.')
evidence=[
    (src+'law-detail-accept','action','document','TBMM, 7590 sayılı Kanunun 24 Temmuz’da kabul edildiğini kaydediyor.'),
    (src+'law-detail-gdate','result','document','Kanun 31 Temmuz 2026 tarihli Resmî Gazete’de yayımlandı.'),
    (src+'law-detail-gno','result','document','Yayım 33326 sayılı Resmî Gazete’de yapıldı.'),
    (src+'law-text-amend','result','document','7590 sayılı Kanunun 16. maddesi asgari dosya ödemesini 20.000 TL’den 23.552 TL’ye çıkardı.'),
    (src+'law-text-effect','result','document','16. madde yayım günü yürürlüğe girdi ve Temmuz 2026 ödeme dönemi için uygulanacağı hükme bağlandı.'),
]
context='TBMM 24 Temmuz’da 7590 sayılı Kanunu kabul etti. 16. maddeyle 5510 sayılı Kanunun ek 19. maddesindeki dosya bazlı aylık alt sınır 23.552 TL oldu.'
eid=event(stem,'2026-07-24','7590 sayılı Kanunun en düşük emekli ödemesine ilişkin hükmü',context,evidence,limitation)
records['practice_event'][-1].update(common_event_key='tbmm-7590-md16-kabul-2026-07-24',
    occurrence_basis='TBMM 7590 sayılı Kanun sicili, tam kanun metninin 16. ve 31. maddeleri.')
event_pids=[row[0] for row in evidence]
wage=[src+'wage-announcement-net',src+'wage-announcement-gross']
scope=readings(topic,'event',event_pids+wage)

statement,target,quote=(stem+suffix for suffix in ('-statement','-target','-quote'))
goal='Saadet Genel Başkanı Mahmut Arıkan, 1 Temmuz’da en düşük emekli aylığının aynı ay içinde asgari ücrete kalıcı bir kanunla eşitlenmesini istedi.'
statement_pids=[src+'aa-day',src+'aa-target']
finding(target,goal,statement_pids,'ANKA kaynaklı konuşma aktarımında konuşmacı ve kalıcı eşitleme talebi açık.')
finding(quote,passages[src+'aa-target']['exact'],[src+'aa-target'],'Arıkan’ın eşitleme çağrısının doğrudan aktarımı.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-07-01',date_precision='day',
    version_id=passages[src+'aa-target']['version_id'],
    period_basis='1 Temmuz 2026 günü yayımlanan Yeni Yol grup toplantısındaki Saadet Genel Başkanı konuşması.',
    uncertainty_reason='Beyanın kapsamı aylık alt sınır. Ayrı formüller ve tüm kök aylıkların hesaplanması bu talep içinde ölçülmedi.',
    comparison_row_id='04-03-v3-0311-saadet-sosyal-guvenlik'))
readings(topic,'statement',statement_pids)
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
    ('practice_statement.quote_finding_id',passages[src+'aa-target']['exact'])):
    task(kind,statement,claim,limitation)

rid,result,explanation=(stem+suffix for suffix in ('-relation','-result','-explanation'))
observed='Kanuni alt sınır temmuz ödeme dönemi için 23.552 TL oldu. Bakanlığın 2026 için duyurduğu net asgari ücret 28.075,50 TL. İki tutar arasındaki fark 4.523,50 TL.'
compare='Arıkan’ın temmuzda asgari ücrete eşitleme hedefi ve aynı ödeme dönemi için kanunla belirlenen alt sınır aynı tutar üzerinden karşılaştırıldı. Kanuni alt sınır net asgari ücretin 4.523,50 TL altında kaldı.'
finding(result,observed,event_pids+wage,'Kanun ve Bakanlığın net asgari ücret duyurusu okundu. İki tutarın farkı hesaplandı.')
finding(explanation,compare+' '+limitation,statement_pids+event_pids+wage,limitation)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,
    topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=explanation,temporal_context='1 Temmuz 2026 çağrısı. 24 Temmuz kabulü ve 31 Temmuz yayımı. Hüküm Temmuz 2026 ödeme dönemi için uygulanır.',
    authority_context='Saadet Genel Başkanı hedefi açıkladı. Alt sınırı TBMM kanunla değiştirdi. 2026 net asgari ücret verisi Çalışma ve Sosyal Güvenlik Bakanlığından.',
    uncertainty_reason=limitation))
candidate=stem+'-candidate'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,
    relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(event_pids+wage)))
for kind,claim in (
    ('practice_relation',compare),('practice_relation.target_finding_id',goal),
    ('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare),
):
    task(kind,rid,claim,limitation)

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
for name,content in [('july-pension-floor-draft.json',package),('july-pension-floor-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
