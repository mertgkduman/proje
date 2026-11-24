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
aux=read(here/'izmir-tis-source-records.json')
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
            boundary_reason='İzmir toplu iş görüşmeleriyle ilgili parti açıklaması ve belediye duyuruları okundu.'))
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
        aid=f'izmir-tis-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Haziran 2025 İzmir grevi veya sonrasındaki toplu iş sözleşmesi kaydı.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='İzmir Büyükşehir Belediyesi tarihli duyurularında imzayı bildirdi.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='demokrat'
assert sha256((data/'practices/04-demokrat.json').read_bytes()).hexdigest()=='53d65b9d18651e55c91dfc7477517e984e5c1666efb445711d33568895d62700'
assert sha256((data/'practices/04-demokrat-review.json').read_bytes()).hexdigest()=='c63786406af1d4d83d98f7177c42c316efc40ff96c8df741f9950ab2abfd8845'
topic='sendika-grev'
stem='0412-izmir-tis'
src=stem+'-'
statement,target,quote=(stem+label for label in ('-statement','-target','-quote'))
goal='Haydar Altıntaş, 3 Haziran 2025’te İzmir grevi üzerine belediye ile sendikanın toplu iş görüşmelerini yeniden başlatmasını istedi.'
statement_limit='Parti sitesindeki çağrının belediye veya sendikanın görüşme kararına etkisi açık.'
statement_pids=[src+'party-statement-target',src+'party-statement-quote']
finding(target,goal,statement_pids,'Demokrat Parti sayfasında yayımlanan tarihli açıklama.')
finding(quote,passages[src+'party-statement-quote']['exact'],[src+'party-statement-quote'],
        'Açıklamadaki kısa özgün ifade.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2025-06-03',date_precision='day',
    version_id=passages[src+'party-statement-target']['version_id'],period_basis='3 Haziran 2025 Demokrat Parti açıklaması.',
    uncertainty_reason=statement_limit,comparison_row_id='04-03-v3-0313-demokrat-sendika-grev'))
readings(topic,'statement',statement_pids)
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
    ('practice_statement.quote_finding_id',passages[src+'party-statement-quote']['exact'])):
    task(kind,statement,claim,statement_limit)

events=(
    ('izelman','izmir-2025-06-04-izelman-toplu-sozlesme-imza','2025-06-04','İZELMAN toplu iş sözleşmesi imza duyurusu',
     'İzmir Büyükşehir Belediyesi, 4 Haziran 2025’te İZELMAN toplu iş sözleşmesini sendika temsilcileriyle imzaladığını duyurdu.',
     'İzmir Büyükşehir Belediyesinin 4 Haziran imza duyurusu ve 19 Haziran tarihli önceki imzalara atfı.',
     'Altıntaş’ın açıklaması 3 Haziran, belediyenin imza duyurusu 4 Haziran tarihli.',
     'İzmir Büyükşehir Belediye Başkanı Cemil Tugay ile DİSK Genel-İş İzmir 1 ve 3 numaralı şube başkanları imza duyurusunda yer aldı.',
     'İmzalı sözleşmenin tam metni ve kişisel bordrolar açık.',
     'İzmir Büyükşehir Belediyesi, 4 Haziran’da İZELMAN için 1 ve 3 numaralı sendika şubeleriyle imza atıldığını bildirdi.',
     'Görüşmeleri yeniden başlatma çağrısı, aynı uyuşmazlıktaki İZELMAN imza duyurusuyla tarih sırasına göre karşılaştırıldı.',
     (
         ('municipal-izelman-union','action','İmza duyurusu DİSK Genel-İş’in iki şubesini kaydediyor.'),
         ('municipal-izelman-signature','result','Belediye açıklaması sendika temsilcileriyle imza atıldığını duyurdu.'),
         ('municipal-later-date','result','Belediye 19 Haziran’da 4 Haziran imzasına tekrar atıf yaptı.'),
     )),
    ('izenerji','izmir-2025-06-04-izenerji-toplu-sozlesme-imza','2025-06-04','İZENERJİ toplu iş sözleşmesine belediye atfı',
     'İzmir Büyükşehir Belediyesi 19 Haziran’da İZENERJİ ile DİSK Genel-İş arasındaki sözleşmenin 4 Haziran 2025’te imzalandığını aktardı.',
     '4 Haziran gün içi görüşme durumu ve 19 Haziran tarihli belediye duyurusundaki geriye dönük imza kaydı.',
     '4 Haziran’daki İZELMAN imza duyurusu İZENERJİ görüşmelerinin sonuna gelindiğini belirtiyor. 19 Haziran açıklaması imza gününü 4 Haziran olarak veriyor.',
     'İZENERJİ ve DİSK Genel-İş sözleşmenin tarafları olarak anıldı. Kaydı İzmir Büyükşehir Belediyesi yayımladı.',
     'İmzalı sözleşme nüshası, ayrı imza saati, işçi kapsamı ve ödeme kayıtları açık.',
     'Belediye, İZENERJİ sözleşmesinin 4 Haziran’da imzalandığını ve 2025 için yüzde 30 artış oranının kabul edildiğini 19 Haziran’da bildirdi.',
     'Altıntaş’ın 3 Haziran çağrısı, aynı grevdeki İZENERJİ sözleşmesine dair tarihli belediye açıklamasıyla karşılaştırıldı.',
     (
         ('municipal-izelman-izenerji','initiative','4 Haziran ilk duyuruda İZENERJİ görüşmelerinin sonuna gelindiği belirtildi.'),
         ('municipal-later-date','result','Sonraki duyuru 4 Haziran İZENERJİ imzasına atıf yaptı.'),
         ('municipal-later-rate','result','Belediye başkanı yüzde 30 artış oranının kabul edildiğini aktardı.'),
     )),
)
for label,key,day,title,context,basis,time,specific_authority,detail,observed,compare,anchors in events:
    event_stem=stem+'-'+label
    limit=detail+' '+statement_limit
    evidence=[(src+pid,stage,'document',claim) for pid,stage,claim in anchors]
    event_id=event(event_stem,day,title,context,evidence,limit)
    records['practice_event'][-1].update(common_event_key=key,occurrence_basis=basis)
    pids=[row[0] for row in evidence]
    scope=readings(topic,'event',pids)
    rid,result,explanation=(event_stem+suffix for suffix in ('-relation','-result','-explanation'))
    finding(result,observed,pids,basis)
    finding(explanation,compare+' '+limit,statement_pids+pids,limit)
    records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=event_id,party_id=party,
        topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,
        result_finding_id=result,explanation_finding_id=explanation,temporal_context=time,
        authority_context=specific_authority,uncertainty_reason=limit))
    candidate=event_stem+'-candidate'
    records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=event_id,
        relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(pids)))
    for kind,claim in (
        ('practice_relation',compare),('practice_relation.target_finding_id',goal),
        ('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare),
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
for name,content in [('izmir-tis-draft.json',package),('izmir-tis-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
