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
aux=read(here/'private-teacher-meetings-source-records.json')
party=aux['party_id']
package=read(data/'practices/04-saadet.json')
review=read(data/'practices/04-saadet-review.json')
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
            boundary_reason='Özel sektör öğretmenlerinin çalışma şartlarına ilişkin tarihli açıklama ve toplantılar incelendi.'))
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
        aid=f'private-teacher-meetings-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='Birden fazla yayımlanmış açıklamada toplantı ve tarih doğrulandı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='saadet'
topic='guvencesiz-istihdam'
first='0411-private-teachers-2026-07-30'
second='0411-private-teachers-2026-08-12'
src='0411-teacher-'
first_limit=('Bakanlığın davet yazısının ve toplantı tutanağının özgün nüshaları açık. '
    'Saadet’in çalıştaya katıldığı, çalıştayı sağladığı veya görüşmenin sonunda ücret ve sözleşme düzenlemesinin yürürlüğe girdiği doğrulanamadı.')
second_limit=('Üçüncü toplantı için bir plan açıklandı. Üçüncü toplantının gerçekleşmesi, imzalı karar ve yürürlüğe giren bir taban ücret açık.')
first_evidence=[
    (src+'talk-june-call','initiative','independent_report','Arıkan 24 Haziran grup toplantısında öğretmenlerle görüşmenin yapılması çağrısında bulundu.'),
    (src+'tes-day','action','independent_report','Türk Eğitim-Sen Bakanlığın 30 Temmuz çalıştayına ev sahipliği yaptığını kaydetti.'),
    (src+'tes-attend','action','independent_report','Türk Eğitim-Sen toplantıya İrfan Kılınçer’in sendikayı temsilen katıldığını kaydetti.'),
    (src+'tes-contract','action','independent_report','Türk Eğitim-Sen en az dört yıllık sözleşme önerisini açıkladı.'),
    (src+'sendika-duration','action','independent_report','Hüseyin Aksoy kendi sendikasının belirsiz süreli sözleşme talebini anlattı.'),
    (src+'sendika-technical','result','independent_report','Hüseyin Aksoy talepleri ele alacak teknik çalışma gruplarının kurulacağını söyledi.'),
]
first_context='Çalışma ve Sosyal Güvenlik Bakanlığı 30 Temmuz’da özel okul öğretmenlerinin çalışma şartları üzerine bir çalıştay düzenledi.'
first_event=event(first,'2026-07-30','Özel okul öğretmenlerinin çalışma hayatı çalıştayı',first_context,first_evidence,first_limit)
records['practice_event'][-1].update(common_event_key='csgb-ozel-okul-ogretmenleri-calistayi-2026-07-30',
    occurrence_basis='Türk Eğitim-Sen Basın Bürosu duyurusu ve ANKA kaynaklı Sendika Bülteni toplantı haberi.')
first_pids=[row[0] for row in first_evidence]
scope=readings(topic,'event',first_pids)

statement,target,quote=(first+suffix for suffix in ('-statement','-target','-quote'))
goal='Arıkan 29 Temmuz’da ertesi gün yapılacağını söylediği toplantıdan özel sektör öğretmenlerinin özlük hakları için kalıcı kararlar çıkmasını istedi.'
statement_pids=[src+'talk-july-schedule',src+'talk-july-target']
finding(target,goal,statement_pids,'29 Temmuz tarihli kaynakta Arıkan’ın talebi ve toplantı tarihi okundu.')
finding(quote,passages[src+'talk-july-target']['exact'],[src+'talk-july-target'],'Arıkan’ın açıklamasındaki talebin aktarımı.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-07-29',date_precision='day',
    version_id=passages[src+'talk-july-target']['version_id'],
    period_basis='29 Temmuz günü yayımlanan TBMM grup toplantısı aktarımı.',
    uncertainty_reason='Toplantı tarihine ilişkin Bakanlık yazısı açıklamada anılıyor. Bakanlık yazısının özgün nüshası açık.',
    comparison_row_id='04-03-v3-0311-saadet-guvencesiz-istihdam'))
readings(topic,'statement',statement_pids+[src+'talk-june-call'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
    ('practice_statement.quote_finding_id',passages[src+'talk-july-target']['exact'])):
    task(kind,statement,claim,first_limit)

rid,result,explanation=(first+suffix for suffix in ('-relation','-result','-explanation'))
observed='30 Temmuz çalıştayı yapıldı. Katılımcı sendikalar farklı sözleşme önerileri sundu. Özel Sektör Öğretmenleri Sendikası teknik çalışma gruplarının kurulacağını duyurdu.'
compare='Arıkan’ın 29 Temmuz’daki çağrısı 30 Temmuz çalıştayına yönelikti. Çalıştayın yapıldığı ve teknik çalışma planı kaynaklandı. Talep edilen kalıcı düzenlemenin yürürlüğe girdiği doğrulanamadı.'
finding(result,observed,first_pids[1:],'Katılımcı sendika açıklaması ve toplantı haberi birlikte okundu.')
finding(explanation,compare+' '+first_limit,statement_pids+first_pids,first_limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=first_event,party_id=party,
    topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=explanation,temporal_context='24 Haziran toplantı çağrısı, 29 Temmuz beklentisi ve 30 Temmuz çalıştayı ayrı zaman kayıtları.',
    authority_context='Çalıştayı Bakanlık düzenledi. Sendikalar kendi katılımı ve talepleri hakkında açıklama yaptı. Arıkan’ın beyanı parti tutumunu gösteriyor.',
    uncertainty_reason=first_limit))
candidate=first+'-candidate'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=first_event,
    relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(first_pids)))
for kind,claim in (
    ('practice_relation',compare),('practice_relation.target_finding_id',goal),
    ('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare),
):
    task(kind,rid,claim,first_limit)

second_evidence=[
    (src+'anka-aug-day','action','independent_report','12 Ağustos tarihli ANKA haberi ikinci toplantının gerçekleştiğini aktardı.'),
    (src+'patika-aug-roles','action','independent_report','Gazete Patika sendika, işveren ve bakanlık temsilcilerinin katılımını aktardı.'),
    (src+'patika-aug-agenda','action','independent_report','Gazete Patika Sendika.Org haberine dayanarak taban ücret formüllerinin ele alındığını aktardı.'),
    (src+'anka-aug-result','result','independent_report','Eren Edebali toplantıda taban ücret düzenlemesi çıkmadığını söyledi.'),
    (src+'anka-aug-next','result','independent_report','Eren Edebali üç tarafın ele alacağı konular için yeni toplantı planlandığını açıkladı.'),
]
second_context='12 Ağustos’ta Bakanlık, sendika ve işveren temsilcileri ikinci toplantıda özel okul öğretmenlerinin taban ücret önerilerini görüştü.'
second_event=event(second,'2026-08-12','Özel okul öğretmenleri için ikinci Bakanlık toplantısı',second_context,second_evidence,second_limit)
records['practice_event'][-1].update(common_event_key='csgb-ozel-okul-ogretmenleri-ikinci-toplanti-2026-08-12',
    occurrence_basis='GazeteKalem’deki ANKA haberi ve Gazete Patika’nın Sendika.Org atıflı toplantı aktarımı.')
second_pids=[row[0] for row in second_evidence]
sid=readings(topic,'event',second_pids)
reason='İkinci toplantı ve üçüncü görüşme planı kaynaklandı. Saadet’in 12 Ağustos görüşmesine ilişkin doğrudan beyanı veya katılımı bulunamadı.'
records['practice_candidate'].append(dict(id=second+'-unmatched',scope_id=sid,event_id=second_event,
    relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(second_pids)))
task('practice_candidate',second+'-unmatched',reason,second_limit)

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
for name,content in [('private-teacher-meetings-draft.json',package),('private-teacher-meetings-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
