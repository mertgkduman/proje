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
aux=read(here/'january-visits-source-records.json')
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
            boundary_reason='Partiler arası temas duyurusu ve iki görüşmenin tarihli açıklamaları okundu.'))
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
        aid=f'jan-visits-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Ocak 2026 partiler arası temas duyurusu veya tarihli görüşme kaydı.',state='examined',attempt_ids=encoded([aid])))
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
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='7562311c3900a059cdb70ca42a9283ff63acdde72059672db17824747625bc97'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='fc30cbd8d1121c7137b62a28b2cc9de1dbbc761ec1601e7498d801bb334a3b7c'
topic='siyasal-ittifaklar'
stem='0411-jan-visits'
src=stem+'-'
statement,target,quote=(stem+label for label in ('-statement','-target','-quote'))
goal='Mahmut Arıkan 28 Ocak 2026’da partiler arası görüşmelerin süreceğini söyledi. Ertesi gün DEM Parti heyetini ağırlayacaklarını ve İYİ Parti ile de görüşeceklerini duyurdu.'
statement_limit='İYİ Parti görüşmesi için 28 Ocak aktarımında gelecek hafta ifadesi kullanıldı. Açıklama, dönemsel parti temaslarını ve ittifak arayışını ele alıyor. Resmî ittifak kurulduğuna dair belge açık.'
statement_pids=[src+'dha-28-dem',src+'dha-28-iyi',src+'dha-28-quote']
finding(target,goal,statement_pids,'DHA’nın 28 Ocak tarihli TBMM basın buluşması aktarımı.')
finding(quote,passages[src+'dha-28-quote']['exact'],[src+'dha-28-quote'],'Arıkan’ın açıklamasındaki kısa özgün ifade.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-01-28',date_precision='day',
    version_id=passages[src+'dha-28-dem']['version_id'],period_basis='28 Ocak 2026 tarihli DHA basın buluşması kaydı.',
    uncertainty_reason=statement_limit,comparison_row_id='04-03-v3-0311-saadet-scope-siyasal-ittifaklar-row'))
readings(topic,'statement',statement_pids)
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
    ('practice_statement.quote_finding_id',passages[src+'dha-28-quote']['exact'])):
    task(kind,statement,claim,statement_limit)

events=(
    ('dem','saadet-dem-2026-01-29-suriye-gorusmesi','2026-01-29','DEM Parti heyetinin Saadet Partisi ziyareti',
     '29 Ocak 2026’da DEM Parti heyeti Saadet Partisi Genel Merkezinde Mahmut Arıkan ve heyetiyle görüştü. Görüşmenin ardından ortak basın açıklaması yapıldı.',
     'Independent Türkçe’nin 29 Ocak tarihli görüşme ve ortak basın açıklaması aktarımı.',
     '28 Ocak duyurusunu 29 Ocak ziyareti izledi.',
     'Mahmut Arıkan Saadet, Tuncer Bakırhan ve Tülay Hatimoğulları DEM Parti adına görüşmeye katıldı. TBMM heyeti önerisinin kararı Meclise bağlı.',
     'Meclis heyetinin kurulması, ziyaret yapması ve rapor yayımlaması açık.',
     'DEM Parti heyeti Saadet Partisi’ni ziyaret etti. Tuncer Bakırhan, Mahmut Arıkan’ın Suriye’ye ilişkin Meclis heyeti önerisini desteklediğini açıkladı.',
     'Duyurulan DEM Parti temasının ertesi gün gerçekleştiği ziyaret ve basın açıklaması kayıtlarıyla görüldü.',
     (
         ('independent-29-place','action','Independent Türkçe, DEM Parti heyetinin Saadet Partisi Genel Merkezindeki görüşmesini aktardı.'),
         ('independent-29-press','result','Taraflar görüşmeden sonra basına açıklama yaptı.'),
         ('independent-29-support','result','Bakırhan kamuya açık açıklamasında Arıkan’ın Meclis heyeti önerisini destekledi.'),
     )),
    ('iyi','saadet-iyi-2026-01-30-gorusmesi','2026-01-30','Saadet Partisi’nin İYİ Parti ziyareti',
     '30 Ocak 2026’da Mahmut Arıkan ve Saadet Partisi heyeti, İYİ Parti Genel Başkanı Müsavat Dervişoğlu’nu ziyaret etti.',
     '30 Ocak tarihli Nefes sayfasındaki ANKA Haber Ajansı görüşme aktarımı.',
     'İYİ Parti teması 28 Ocak’ta duyuruldu. Belirlenen görüşme yayına göre 30 Ocak’ta gerçekleşti.',
     'Arıkan Saadet Partisi ve Dervişoğlu İYİ Parti genel başkanı olarak konuştu.',
     'Arıkan görüşmeyi kurultay sonrası nezaket ziyareti olarak tanımladı. Sonraki temaslara ve resmî bir ittifak kararına ilişkin kayıt açık.',
     'Arıkan İYİ Parti’nin 4. Olağan Kurultayı sonrasında bir ziyarette bulunduklarını ve iki parti arasındaki görüşmelerin sürmesi konusunda mutabakat sağlandığını söyledi.',
     'Duyurulan İYİ Parti temasıyla aynı dönemde gerçekleşen görüşme karşılaştırıldı. Haberdeki tarih, 28 Ocak’ta bildirilen haftadan önce.',
     (
         ('nefes-30-visit','action','Arıkan kurultay sonrası ziyareti açıkladı.'),
         ('nefes-30-contact','result','Arıkan iki parti arasındaki görüşmelerin sürmesi konusunda mutabakat bildirildiğini söyledi.'),
     )),
)
for label,key,day,title,context,basis,time,specific_authority,detail,observed,compare,anchors in events:
    event_stem=stem+'-'+label
    limit=detail+' '+statement_limit
    evidence=[(src+pid,stage,'independent_report',claim) for pid,stage,claim in anchors]
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
for name,content in [('january-visits-draft.json',package),('january-visits-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
