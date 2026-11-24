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
aux=read(here/'fuel-4496-source-draft.json')
party='demokrat'
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
            boundary_reason='2/4496 teklifinin imzalı nüshası, parti açıklaması ve hükümsüz teklifler listesi okundu. Kapsam açık.'))
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
        aid=f'fuel-4496-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='2/4496, fiyat düzenleme teklifi ve dönem sonu işlemi.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit,unknown_reason=None):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day' if day else 'unknown',
        date_unknown_reason=unknown_reason,title=title,scope_context=context,
        occurrence_basis='Tarihli özgün kurum veya parti kaydı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (55, 45, 0)
assert sha256((data/'practices/04-demokrat.json').read_bytes()).hexdigest() == '31c4f448bb266479944f0ac87856d8cc3d069663f579e8fea7e7aa1dbde9aad2'
assert sha256((data/'practices/04-demokrat-review.json').read_bytes()).hexdigest() == '4853218634d3d3b80c292f4baecc16f7d45f98c9180b2f62c6e347a87e728178'


def register_statement(stem, topic, day, read_basis, comparison_row, short, references, limit):
    sid, target, quote = (stem + suffix for suffix in ('-statement', '-target', '-quote'))
    finding(target, short, references, read_basis)
    excerpt = passages[references[0]]['exact']
    finding(quote, excerpt, references[:1], read_basis, pair=target)
    records['practice_statement'].append(dict(
        id=sid, party_id=party, topic_id=topic, taxonomy_version=4, summary_finding_id=target,
        quote_finding_id=quote, statement_at=day, date_precision='day' if day else 'unknown',
        version_id=passages[references[0]]['version_id'], period_basis=read_basis,
        uncertainty_reason=limit, comparison_row_id=comparison_row))
    readings(topic, 'statement', references)
    for kind, claim in (('practice_statement', short), ('practice_statement.summary_finding_id', short),
                        ('practice_statement.quote_finding_id', excerpt)):
        task(kind, sid, claim, limit)
    return sid, target, short, references


def compare(stem, topic, eid, statement, compare_text, temporal, authority, limit, outcome=None):
    sid, target, short, statement_refs = statement
    event_refs = [row['passage_id'] for row in records['practice_event_evidence'] if row['event_id'] == eid]
    scope = readings(topic, 'event', event_refs)
    rid = stem + '-relation'
    explanation = stem + '-explanation'
    finding(explanation, compare_text + ' ' + limit, statement_refs + event_refs, limit)
    result = None
    if outcome:
        result = stem + '-result'
        result_refs = [row['passage_id'] for row in records['practice_event_evidence']
                       if row['event_id'] == eid and row['stage'] == 'result']
        finding(result, outcome, result_refs, limit)
        task('practice_relation.result_finding_id', rid, outcome, limit)
    records['practice_relation'].append(dict(
        id=rid, statement_id=sid, event_id=eid, party_id=party, topic_id=topic, scope_id=scope,
        comparability_reason=compare_text, target_finding_id=target, result_finding_id=result,
        explanation_finding_id=explanation, temporal_context=temporal, authority_context=authority,
        uncertainty_reason=limit))
    records['practice_candidate'].append(dict(
        id=stem + '-candidate', scope_id=scope, event_id=eid, relation_id=rid,
        state='eligible', reason=compare_text, passage_ids=encoded(event_refs)))
    for kind, claim in (('practice_relation', compare_text), ('practice_relation.target_finding_id', short),
                        ('practice_relation.explanation_finding_id', compare_text)):
        task(kind, rid, claim, limit)
    return scope


stem = '0412-fuel-4496'
topic = 'makroekonomik-politika'
statement_limit = ('Parti açıklamasındaki petrol ve kur karşılaştırmaları konuşmacının hesabı. '
                   'İncelenen talep 5015 değişikliğinin geçirilmesi ve iki aylık fiyat düzenlemesi.')
statement = register_statement(
    stem, topic, '2022-06-22', 'Demokrat Parti, 22 Haziran 2022 tarihli Çevik açıklaması.',
    '04-03-v3-0313-demokrat-makroekonomik-politika',
    'Neslihan Çevik, EPDK’nın akaryakıt fiyatını iki aylık dönemle düzenlemesini ve Demokrat Partili milletvekillerinin sunduğu teklifin ivedilikle kabul edilmesini istedi.',
    [stem + '-party-' + key + '-p' for key in ('request', 'passage-request', 'prior-filing')],
    statement_limit,
)
filing_refs = [
    (stem + '-signed-cover-p', 'action', 'document', 'Gültekin Uysal ve Cemal Enginyurt’un imzaları 16 Haziran tarihli özgün teklif üzerinde.'),
    (stem + '-arrival-arrival-p', 'action', 'document', 'TBMM gelen kâğıtlar kaydında Başkanlığa geliş günü 16 Haziran 2022.'),
    (stem + '-signed-assignment-p', 'result', 'document', 'Kapak kaşesi komisyon sevkinin 17 Haziran 2022 ve esas numarasının 2/4496 olduğunu gösteriyor.'),
    (stem + '-signed-term-p', 'action', 'document', 'Teklif 5015 madde 10’da her seferinde iki ayı aşmayan düzenleme yetkisi öneriyor.'),
    (stem + '-signed-transition-p', 'action', 'document', 'Taslak geçici madde 8, teklif kanunlaşırsa ilk iki aylık süre için tavan fiyat uygulaması öngörüyor.'),
]
filing_limit = ('Teklif sunuşu, komisyona sevk ve kanunlaşma farklı işlemler. '
                '22 Haziran açıklaması 16 Haziran işlemini geçmiş zamanda anlatıyor.')
eid = event(stem + '-filing', '2022-06-16', '2/4496 akaryakıt teklifinin TBMM’ye gelişi',
            'TBMM 27. dönem 5. yasama yılı, imzalı teklif, gelen kâğıt ve 17 Haziran sevk kaşesi.',
            filing_refs, filing_limit)
records['practice_event'][-1]['common_event_key'] = 'tbmm-27-5-2-4496-filing'
pids = [r[0] for r in filing_refs]
scope = readings(topic, 'event', pids + [stem + '-registry-registry-p'])
cid = stem + '-filing-candidate'
records['practice_candidate'].append(dict(
    id=cid, scope_id=scope, event_id=eid, relation_id=None, state='unmatched',
    reason='22 Haziran parti açıklamasından önceki teklif gelişi, özgün imza ve kayıtla belgeleniyor.',
    passage_ids=encoded(pids)))
task('practice_candidate', cid, '2/4496 teklifinin geliş ve sevk günleri ayrı belgeleniyor.', filing_limit)

lapse_refs = [
    (stem + '-term-cover-opening-p', 'action', 'document', '28. dönemin ilk birleşimi 2 Haziran 2023 tarihlidir.'),
    (stem + '-term-leaf-heading-p', 'action', 'document', 'Basılı 203. sayfa hükümsüz sayılan milletvekili teklifleri tablosu.'),
    (stem + '-term-leaf-lapse-p', 'result', 'document', 'Hükümsüz teklifler tablosunda 2/4496 sıra 4213’te listeleniyor.'),
]
lapse_limit = ('2 Haziran, sonucun tutanak ekinde belgelenme günü. 2023 tarihli 2/1525 ve 2024 gündeme alma işlemi ayrı dosyadır. '
               'Listede akaryakıt fiyatına ilişkin fiilî bir uygulama ölçümü yok.')
eid = event(stem + '-lapse', '2023-06-02', '2/4496’nın hükümsüz teklifler listesinde yer alması',
            'TBMM 28. dönem birinci birleşimi, hükümsüz sayılan milletvekili teklifleri p203 sıra 4213.',
            lapse_refs, lapse_limit)
records['practice_event'][-1]['common_event_key'] = 'tbmm-28-1-1-2-4496-lapsed-list'
compare(stem + '-lapse', topic, eid, statement,
        'Çevik’in Meclisten geçmesini istediği iki aylık düzenlemeyi içeren 2/4496, yeni dönem başında hükümsüz teklifler arasında kaydedildi.',
        '2/4496 16 Haziran’da geldi, 22 Haziran açıklaması daha sonra yayımlandı. Hükümsüz teklifler listesi 2 Haziran 2023 tarihli tutanakta.',
        'Teklifi iki Demokrat Parti milletvekili imzaladı. Son durum TBMM sicili ve tutanak ekine dayanıyor.',
        lapse_limit,
        'TBMM’nin hükümsüz teklifler listesinde 2/4496 sıra 4213’te kayıtlıdır.')

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
        reason=f'{kind} kaydındaki {identity} hedefinin kaynakları okundu. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('fuel-4496-draft.json',package),('fuel-4496-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
