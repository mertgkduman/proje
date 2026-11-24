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
aux=read(here/'law-7418-source-draft.json')
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
            boundary_reason='2/4471 parti açıklaması, görüşme tutanağı ve 7418 ile ilgili özgün belgeler okundu. Kapsam açık.'))
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
        aid=f'law-7418-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='2/4471, 7418 veya 217/A ile ilgili özgün kaynak.',state='examined',attempt_ids=encoded([aid])))
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
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (52, 43, 0)
assert sha256((data/'practices/04-demokrat.json').read_bytes()).hexdigest() == '8d713724de98c6184da3b82c5e3c93a5df624a43dbdce7c74d0220e055043bc7'
assert sha256((data/'practices/04-demokrat-review.json').read_bytes()).hexdigest() == '21c9887190fe1f515caff264f9058b522e9af63d9f5fc342f2caa0ceaed06ef2'


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


def compare(stem, topic, eid, statement, compare_text, temporal, authority, limit,
            outcome=None, context='', context_refs=()):
    sid, target, short, statement_refs = statement
    event_refs = [row['passage_id'] for row in records['practice_event_evidence'] if row['event_id'] == eid]
    scope = readings(topic, 'event', event_refs)
    rid = stem + '-relation'
    explanation = stem + '-explanation'
    finding(explanation, ' '.join(part for part in (compare_text, context, limit) if part),
            statement_refs + event_refs + list(context_refs), limit)
    if context_refs:
        readings(topic, 'statement', context_refs)
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
                        ('practice_relation.explanation_finding_id', (compare_text + ' ' + context).strip())):
        task(kind, rid, claim, limit)
    return scope


stem = '0412-law-7418'
topic = 'ifade-basin-ozgurlugu'
statement_limit = ('Parti sayfası 6 Ekim, metindeki parti basın merkezi tarihi 5 Ekim. '
                   'Sunuş ilk iki, konuşmacı gövdesi ilk maddenin önceki gün kabulünü anıyor.')
statement = register_statement(
    stem, topic, '2022-10-05', 'Parti açıklamasındaki 5 Ekim 2022 tarihi. Arşiv sayfasında 6 Ekim.',
    '04-03-v3-0313-demokrat-ifade-basin-ozgurlugu',
    'Demokrat Parti sözcüsü Neslihan Çevik, 2/4471 teklifinin 29. maddesini eleştirdi ve teklifin karşısında durulmasını istedi.',
    [stem + '-party-' + key + '-p' for key in ('request', 'article29', 'headline', 'body')],
    statement_limit,
)
authority = ('Parti sözcüsü kamuya açık açıklama yaptı. Genel Kurul kararını birleşim başkanı ilan etti. '
             'Pasaj kesin kişisel oy kaydı veya partiye yasama yetkisi vermez.')
coverage = 'İncelenen kaynaklar bir kişiye 217/A kapsamında işlem yapılması veya sonuçlanmış yargılama hakkında bilgi vermiyor.'
article_refs = [
    (stem + '-floor-article29-p', 'action', 'document', '13 Ekim 7. birleşimde 29. madde ayrı oylanarak kabul edildi.'),
    (stem + '-law-article29-p', 'result', 'document', '18 Ekim özgün kanun metninin 29. maddesi TCK 217/A hükmünü ekliyor.'),
]
eid = event(stem + '-article29', '2022-10-13', '2/4471 teklifinin 29. maddesinin kabulü',
            'TBMM 27. dönem 6. yasama yılı 7. birleşim, 340 sıra sayısı.', article_refs, coverage)
records['practice_event'][-1]['common_event_key'] = 'tbmm-27-6-07-2-4471-article-29'
compare(stem + '-article29', topic, eid, statement,
        'Çevik’in itiraz ettiği 29. madde 13 Ekim’de Genel Kurulda kabul edildi.',
        'Açıklama 5 Ekim tarihli ve parti sayfası 6 Ekim. Madde 13 Ekim’de kabul edildi.', authority, coverage,
        'Kabul edilen metin, halkı yanıltıcı bilgiyi alenen yayma başlıklı 217/A’yı Türk Ceza Kanununa ekledi.')
bill_refs = [
    (stem + '-floor-bill-p', 'action', 'document', '13 Ekim Genel Kurulunda teklifin tümü ayrı oya sunulup kabul edildi.'),
    (stem + '-law-publication-p', 'result', 'document', '7418 sayılı Kanun 18 Ekim 2022 tarihli Resmî Gazete’de yayımlandı.'),
    (stem + '-law-commencement-p', 'result', 'document', '39(b) uyarınca 29. madde yayım tarihinde yürürlüğe giren hükümlerden.'),
]
eid = event(stem + '-bill', '2022-10-13', '2/4471 teklifinin 7418 sayılı kanun olarak kabulü',
            'TBMM 7. birleşimde teklifin tümünün oylaması ve 18 Ekim 31987 sayılı Resmî Gazete.', bill_refs, coverage)
records['practice_event'][-1]['common_event_key'] = 'tbmm-27-6-07-2-4471-law-final'
compare(stem + '-bill', topic, eid, statement,
        'Parti açıklamasında karşı çıkılan teklifin tümü Genel Kurulda kabul edildi.',
        'Teklifin tamamı 13 Ekim’de kabul edildi. Kanun 18 Ekim’de yayımlandı ve 29. madde aynı gün yürürlüğe girdi.',
        authority, coverage, '2/4471, 7418 sayılı Kanun olarak 18 Ekim’de yayımlandı. 29. madde için yayım günü yürürlük tarihi.',
        context='Enginyurt 22 Haziran’da Genel Kurulda aleyhte oy verme niyetini açıkladı. Altı parti genel başkanının 3 Temmuz ortak metni teklifin ertelenmesinden söz ediyor.',
        context_refs=(stem + '-early-floor-intent-p', stem + '-joint-delay-p'))
court_refs = [
    (stem + '-court-index-docket-p', 'action', 'document', 'Fihrist 8 Kasım 2023, E.2022/129 ve K.2023/189 künyesini veriyor.'),
    (stem + '-court-review-p', 'action', 'document', 'AYM esastan iptal istemini altı karşıoyla oyçokluğuyla reddetti.'),
    (stem + '-court-stay-p', 'action', 'document', 'AYM yürürlüğün durdurulması istemini oybirliğiyle reddetti.'),
    (stem + '-court-header-p', 'result', 'document', 'Karar 23 Şubat 2024 tarihli 32469 sayılı Resmî Gazete’de yayımlandı.'),
]
court_limit = ('İptal davası TCK 217/A ile sınırlı. Çevik’in karşı çıkma çağrısı bir dava başvurusu, '
               'partinin davadaki rolü veya bireysel bir ceza yargılamasının kanıtı olarak kullanılamaz.')
eid = event(stem + '-court', '2023-11-08', 'AYM’nin TCK 217/A iptal istemini reddi',
            'E.2022/129 K.2023/189 kararının IV. bölümü ve hükmü.', court_refs, court_limit)
records['practice_event'][-1]['common_event_key'] = 'aym-2022-129-2023-189-tck-217a'
pids = [row[0] for row in court_refs]
scope = readings(topic, 'event', pids)
cid = stem + '-court-candidate'
records['practice_candidate'].append(dict(
    id=cid, scope_id=scope, event_id=eid, relation_id=None, state='unmatched',
    reason='Karar 217/A iptal davasına ilişkin. Parti açıklamasında dava talebi veya dava işlemi bulunmuyor.',
    passage_ids=encoded(pids)))
task('practice_candidate', cid, 'AYM 217/A iptal istemini reddetti, özgün karar 23 Şubat 2024’te yayımlandı.', court_limit)

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
for name,content in [('law-7418-draft.json',package),('law-7418-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
