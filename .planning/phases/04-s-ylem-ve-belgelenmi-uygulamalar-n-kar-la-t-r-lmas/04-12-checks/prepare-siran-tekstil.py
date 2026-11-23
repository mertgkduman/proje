"""Connect the Şiran Tekstilkent campaign goal to the reported municipal milestone."""

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
aux=read(here/'siran-tekstil-source-records.json')
party=aux['party_id']
package=read(here/'fund-3965-draft.json')
review=read(here/'fund-3965-review-draft.json')
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
            boundary_reason='Yerel Tekstilkent hedefi ve açıklanan ilk belediye adımı incelendi.'))
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
        aid=f'siran-tekstil-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Tekstilkent hedefi ve Şiran belediye işlemine ilişkin kaynak.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='Tarihli Şiran Belediyesi yer incelemesi duyurusu.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'demokrat'
topic = 'sanayi-politikasi'
stem = '0412-demokrat-siran-tekstilkent'
base_passage = '0412-tekstil-'
statement,target,quote = (stem+suffix for suffix in ('-statement','-target','-quote'))
statement_refs = [base_passage+f'taka-{key}' for key in ('role','goal','first','quote')]
quote_ref = base_passage+'taka-quote'
goal = ('Demokrat Parti’nin Şiran adayı Abdulbaki Kara, Tekstilkent için ilk aşamada yaklaşık 120 kişilik '
        'istihdam ve tam kapasitede yaklaşık 500 kişilik istihdam hedefi açıkladı.')
statement_limit = ('Taka Gazete görüşmeyi 29 Şubat 2024’te yayımladı. Görüşmenin günü ve yatırımcıların '
                   'bağlayıcı yükümlülükleri açık. İki sayı adayın hedefleri.')
finding(target,goal,statement_refs,statement_limit)
finding(quote,passages[quote_ref]['exact'],[quote_ref],statement_limit,pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2024-02-29',date_precision='day',
    version_id=passages[quote_ref]['version_id'],period_basis='Demokrat Parti adayının 29 Şubat’ta yayımlanan görüşmesi.',
    uncertainty_reason=None,comparison_row_id='04-03-v3-0313-demokrat-sanayi-politikasi'))
readings(topic,'statement',statement_refs+[base_passage+'taka-byline'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[quote_ref]['exact'])):
    task(kind,statement,claim,statement_limit)

context = 'Şiran Belediyesi 18 Mayıs 2024 duyurusunda Tekstilkent için yatırımcılarla yer incelemesi yaptıklarını açıkladı.'
limit = ('18 Mayıs duyurunun yazılı tarihi. Yer incelemesinin kesin günü, inşaat, istihdam ve toplam hedefe '
         'erişim araştırmaya açık. Belediye ve işletmelerin yetkileri ayrı.')
evidence = [
    (base_passage+'municipal-date','action','document','Şiran Belediyesi duyuru gününü 18 Mayıs olarak veriyor.'),
    (base_passage+'municipal-site','action','document','Belediye yatırımcılarla Tekstilkent için saha incelemesi yapıldığını duyurdu.'),
]
eid = event(stem,'2024-05-18','Şiran Tekstilkent yer incelemesi duyurusu',context,evidence,limit)
refs = [row[0] for row in evidence]
scope = readings(topic,'event',refs+[base_passage+s for s in ('municipal-plan','handover-date','handover-role')])
for suffix,url in (
    ('tso24','https://www.kelkittso.org.tr/dosyalar/2024-yili-faaliyet-raporu.pdf'),
    ('tso25','https://www.kelkittso.org.tr/dosyalar/2025.pdf'),
):
    aid=stem+'-access-'+suffix
    records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=when,query=url,url=url,
        result='failure',reason='Oda nüshası için özgün PDF alımı HTTP 403 döndürdü. Web metni yalnız açık araştırma ipucu.',
        source_version_id=None))
    records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,
        relevance_reason='Tekstilkent kapsamında işletme açılışı ve görünür istihdam kapsamı.',state='blocked',attempt_ids=encoded([aid])))
rid = stem+'-relation'
explanation = stem+'-explanation'
compare = 'Adayın istihdam hedefi ile belediyenin yatırımcılarla yer incelemesi aynı Şiran Tekstilkent projesine ilişkin.'
explanation_text = ('Aday yaklaşık 120 kişilik ilk aşama ve 500 kişilik tam kapasite hedefi açıkladı. '
                   '3 Nisan’da belediye başkanlığı görevini devraldı. Şiran Belediyesi 18 Mayıs’ta yatırımcılarla '
                   'saha incelemesi yapıldığını duyurdu. Hedefe erişim ve çalışan sayısı için kaynak araştırması açık.')
finding(explanation,explanation_text,[*statement_refs,*refs,base_passage+'handover-role'],limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=None,
    explanation_finding_id=explanation,temporal_context='29 Şubat aday görüşmesinin yayımı, 3 Nisan göreve başlama, 18 Mayıs duyuru.',
    authority_context='Kara’nın adaylık sözü, belediye başkanlığı işlemi ve özel yatırımcıların yetki alanları ayrı.',uncertainty_reason=limit))
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
for name,content in [('siran-tekstil-draft.json',package),('siran-tekstil-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
