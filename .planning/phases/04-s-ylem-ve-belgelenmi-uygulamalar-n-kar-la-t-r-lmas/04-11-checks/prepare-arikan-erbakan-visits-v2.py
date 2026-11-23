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
aux=read(here/'arikan-erbakan-visits-v2-source-records.json')
party=aux['party_id']
package=read(here/'kocasinan-provenance-draft.json')
review=read(here/'kocasinan-provenance-review-draft.json')
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
        aid=f'arikan-erbakan-visits-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='Yayında bildirilen tarih, görüşme ve basın açıklaması.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='saadet'
topic='siyasal-ittifaklar'
jan='0411-arikan-erbakan-2026-01-28'
aug='0411-arikan-erbakan-2026-08-11'
src='0411-arikan-erbakan-'
jan_limit=('DHA kapalı görüşme ve sonraki açıklamayı yayımladı. '
    'Görüşmenin imzalı tutanağı ve ittifak kararı doğrulanamadı.')
aug_limit=('Kamuya açıklanan görüşme ve temasları sürdürme beyanı kaynaklandı. '
    'İmzalı ittifak protokolü, ortak aday kararı ve yetkili organ tutanakları açık.')
jan_evidence=[
    (src+'indy-plan','initiative','independent_report','Arıkan 28 Ocak basın buluşmasında aynı gün Yeniden Refah’ı ziyaret edeceğini söyledi.'),
    (src+'dha-date','action','independent_report','DHA görüşmeyi aynı günün akşamı yayımladı.'),
    (src+'dha-place','action','independent_report','DHA, Yeniden Refah Genel Merkezi’ndeki kapalı görüşmenin yaklaşık bir saat sürdüğünü aktardı.'),
    (src+'dha-press','result','independent_report','DHA haberine göre görüşmenin ardından Arıkan ve Erbakan basın açıklaması yaptı.'),
]
jan_context='Saadet Genel Başkanı Mahmut Arıkan ve beraberindeki heyet, 28 Ocak’ta Yeniden Refah Genel Merkezi’nde Fatih Erbakan’ı ziyaret etti.'
jan_event=event(jan,'2026-01-28','Arıkan’ın Yeniden Refah Genel Merkezi ziyareti',jan_context,jan_evidence,jan_limit)
records['practice_event'][-1].update(common_event_key='saadet-arikan-yeniden-refah-ziyareti-2026-01-28',
    occurrence_basis='Arıkan’ın aynı günkü plan açıklaması ve DHA’nın akşam görüşme haberi.')
jan_pids=[row[0] for row in jan_evidence]
sid=readings(topic,'event',jan_pids+[src+'indy-date'])
reason='Ziyaret ve sonrasındaki açıklama kaynaklandı. Önceki günlerden aynı ziyareti belirleyen tarihli bir beyan ve imzalı toplantı tutanağı açık.'
records['practice_candidate'].append(dict(id=jan+'-unmatched',scope_id=sid,event_id=jan_event,
    relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(jan_pids)))
task('practice_candidate',jan+'-unmatched',reason,jan_limit)

statement,target,quote=(jan+label for label in ('-statement','-target','-quote'))
goal='Arıkan, Yeniden Refah Partisi ile karşılıklı ziyaret takvimi yürüttüklerini söyledi ve iş birliğine açık olduğunu belirtti.'
statement_pids=[src+'indy-date',src+'indy-target',src+'indy-position']
finding(target,goal,statement_pids,'28 Ocak tarihli kaynakta konuşmacı ve ziyaret açıklaması birlikte okundu.')
finding(quote,passages[src+'indy-target']['exact'],[src+'indy-target'],'Arıkan’ın ziyarete ilişkin doğrudan aktarımı.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-01-28',date_precision='day',
    version_id=passages[src+'indy-target']['version_id'],
    period_basis='28 Ocak 2026 günü yayımlanan basın buluşması metni.',
    uncertainty_reason='Karşılıklı ziyaret takvimi Arıkan’ın beyanı. Ortak protokol veya geçerli resmî ittifak açık.',
    comparison_row_id='04-03-v3-0311-saadet-scope-siyasal-ittifaklar-row'))
readings(topic,'statement',statement_pids)
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
    ('practice_statement.quote_finding_id',passages[src+'indy-target']['exact'])):
    task(kind,statement,claim,jan_limit)

aug_evidence=[
    (src+'bun-occurred','action','independent_report','11 Ağustos’ta iki lider bu kez Saadet Genel Merkezi’nde görüştü.'),
    (src+'milligazete-place','action','independent_report','Millî Gazete görüşmeyi ve Arıkan’ın ev sahipliğini aktardı.'),
    (src+'bun-press','action','independent_report','Görüşme ardından iki lider ortak basın açıklaması yaptı.'),
    (src+'bun-followup','result','independent_report','BUN, liderlerin daha sık görüşme niyetinde anlaştıklarını söylediklerini aktardı.'),
    (src+'milligazete-election','result','independent_report','Erbakan milletvekili seçimine yönelik bir ittifak ihtimalinin görüşüldüğünü söyledi.'),
    (src+'milligazete-president','result','independent_report','Erbakan o güne kadar ortak cumhurbaşkanı adayı görüşmesi yapılmadığını söyledi.'),
]
aug_context='Fatih Erbakan ve Mahmut Arıkan, 11 Ağustos’ta Saadet Genel Merkezi’nde görüştü. İki lider daha sık görüşme yönünde açıklama yaptı.'
aug_event=event(aug,'2026-08-11','Erbakan’ın Saadet Genel Merkezi ziyareti',aug_context,aug_evidence,aug_limit)
records['practice_event'][-1].update(common_event_key='yeniden-refah-erbakan-saadet-ziyareti-2026-08-11',
    occurrence_basis='11 Ağustos tarihli BUN ve Millî Gazete toplantı ve ortak basın açıklaması haberleri.')
aug_pids=[row[0] for row in aug_evidence]
scope=readings(topic,'event',aug_pids+[src+'milligazete-date'])
rid,result,explanation=(aug+label for label in ('-relation','-result','-explanation'))
observed='11 Ağustos görüşmesi bu kez Saadet Genel Merkezi’nde yapıldı. İki lider temasları sürdürmek istediklerini açıkladı.'
compare='Ocak ayında Arıkan, karşılıklı ziyaret takvimi yürüttüklerini söyledi. Ağustosta diğer parti liderinin Saadet genel merkezine ziyareti, bu temas biçiminin belgelenen bir örneği.'
finding(result,observed,aug_pids,'İki yayın görüşmeyi ve sonrasındaki açıklamaları aktarıyor.')
finding(explanation,compare+' '+aug_limit,statement_pids+aug_pids,aug_limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=aug_event,party_id=party,
    topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=explanation,temporal_context='28 Ocak duyurusu ve ziyareti ile 11 Ağustos karşı ziyaret kaydı.',
    authority_context='Görüşmeye katılan iki genel başkan ve kendi basın açıklamaları kaynaklı. İmzalı parti organı kararı araştırılıyor.',
    uncertainty_reason=aug_limit))
candidate=aug+'-candidate'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=aug_event,
    relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(aug_pids)))
for kind,claim in (
    ('practice_relation',compare),('practice_relation.target_finding_id',goal),
    ('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare),
):
    task(kind,rid,claim,aug_limit)

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
for name,content in [('arikan-erbakan-visits-v2-draft.json',package),('arikan-erbakan-visits-v2-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
