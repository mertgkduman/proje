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
aux=read(here/'pension-5000-source-records.json')
party=aux['party_id']
package=read(here/'divan-atalay-draft.json')
review=read(here/'divan-atalay-review-draft.json')
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
            boundary_reason='Emekli ödemesi hakkında tarihli açıklama, kanun ve SGK raporu incelendi.'))
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
        aid=f'pension-5000-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Emekli ödemesinin kapsam veya uygulama kaynağı.',state='examined',attempt_ids=encoded([aid])))
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
assert party=='demokrat'
assert sha256((here / 'divan-atalay-draft.json').read_bytes()).hexdigest() == '7f8623bd0a4c8f82b26d40853c29092912950e53042902dd3cbfa6efc3fe80dc'
assert sha256((here / 'divan-atalay-review-draft.json').read_bytes()).hexdigest() == 'f5de309aee943bb68d9344cbaa1c15f0ce5219c6fe9280ed7f1b0dd70b609dcd'


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


stem = '0412-pension-5000'
topic = 'sosyal-guvenlik'
statement_limit = ('Açıklama Demokrat Parti sitesinde AA imzasıyla yayımlandı. Konuşmanın dakikası ve '
                   'açıklamanın sonraki yasama işlemlerine etkisi açık.')
statement = register_statement(
    stem, topic, '2023-11-14', 'Demokrat Parti sitesinin 14 Kasım 2023 tarihli AA aktarımı.',
    '04-03-v3-0313-demokrat-sosyal-guvenlik',
    'Haydar Altıntaş, çalışan çiftçi ile esnaf ve sanatkâr emeklilerinin bir defalık 5.000 TL kapsamı dışında tutulmasına itiraz etti.',
    [stem + '-statement-critique', stem + '-statement-farmers'], statement_limit)

initial_limit = ('İlk hüküm 2023 Ekim ödeme dönemini esas alıyor. Çalışma istisnasının ilk metinde ölüm geliri '
                 've aylığı alanlara uygulanmayacağı yazıyor. 14 Kasım açıklamasından önceki özgül parti tutumu açık.')
initial_refs = [
    (stem + '-7464-register-adopted', 'initiative', 'document', 'TBMM sicili 25 Ekim kabul günü ve 12. Birleşimi gösteriyor.'),
    (stem + '-7464-register-published', 'action', 'document', 'TBMM sicili Resmî Gazete yayımını 2 Kasım 2023 olarak kaydediyor.'),
    (stem + '-7464-law-amount', 'result', 'document', 'Geçici 98’in birinci fıkrası dosya bazında bir defalık 5.000 TL’yi düzenliyor.'),
    (stem + '-7464-law-exclusion', 'result', 'document', 'Dördüncü fıkra belirli çalışan gruplarına ilişkin kapsam dışı hükmü getiriyor.'),
    (stem + '-7464-law-eligibility', 'result', 'document', 'Dördüncü fıkrada Ekim dönemindeki çalışma ölçütü yer alıyor.'),
]
initial = event(
    stem + '-initial', '2023-11-02', '7464 ile tek seferlik 5.000 TL ödemesinin ilk kapsamı',
    '7464 sayılı Kanun’un 20. maddesi, belirli çalışma durumları için istisna içeren geçici 98. maddeyi ekledi.',
    initial_refs, initial_limit)
records['practice_event'][-1]['common_event_key'] = 'kanun-7464-m20-gecici98-2023-11-02'
passage_ids = [ref[0] for ref in initial_refs]
scope = readings(topic, 'event', passage_ids)
identity = stem + '-initial-candidate'
records['practice_candidate'].append(dict(
    id=identity, scope_id=scope, event_id=initial, relation_id=None, state='unmatched',
    reason=initial_limit, passage_ids=encoded(passage_ids)))
task('practice_candidate', identity, 'İlk kanun hükmü 14 Kasım tarihli parti yayınından önce yürürlüğe girdi.', initial_limit)

change_limit = ('Yayım günü yürürlüğe giren değişiklik, geçici 98’in dördüncü fıkrasını kaldırdı. '
                'Birinci fıkradaki ödeme dönemi, dosya esası ve diğer fıkralardaki oranlar kaynakta ayrı.')
change = event(
    stem + '-eligibility', '2023-12-28', '7491 ile çalışan emeklilere ilişkin kapsam dışı hükmün kaldırılması',
    '7491 sayılı Kanun, geçici 98’in çalışmaya dayalı kapsam dışı hükmünü kaldırdı.',
    [(stem + '-csgb-nov27-intent', 'initiative', 'document', '27 Kasım Bakanlık açıklaması kapsamı genişletme niyetini kayda aldı.'),
     (stem + '-csgb-nov27-forecast', 'initiative', 'document', 'Bakan 27 Kasım’da 4 milyon 600 bin kişi öngörüsünü verdi.'),
     (stem + '-csgb-dec22-readiness', 'initiative', 'document', '22 Aralık açıklaması yayımı izleyen iki gün için hazırlık yapıldığını bildirdi.'),
     (stem + '-7491-register-adopted', 'initiative', 'document', 'TBMM sicili 27 Aralık kabulünü ve 48. Birleşimi kaydediyor.'),
     (stem + '-7491-register-published', 'action', 'document', '28 Aralık Resmî Gazete yayımı kayıtlı.'),
     (stem + '-7491-law-effective', 'action', 'document', 'Yürürlük maddesi 54. madde için yayım gününü uyguluyor.'),
     (stem + '-7491-law-repeal', 'result', 'document', '54. madde, 5510 geçici 98’in dördüncü fıkrasını yürürlükten kaldırıyor.')],
    change_limit)
records['practice_event'][-1]['common_event_key'] = 'kanun-7491-m54-gecici98-2023-12-28'
compare(stem + '-eligibility', topic, change, statement,
        'Altıntaş’ın çiftçi ve esnaf emeklilerine ilişkin kapsam itirazı, çalışma ölçütünü kaldıran sonraki kanunla karşılaştırıldı.',
        '14 Kasım parti yayını, 27 Kasım Bakanlık açıklaması, 22 Aralık ödeme hazırlığı, 27 Aralık kabul ve 28 Aralık yayımı ayrı tarihler.',
        'TBMM kapsam değişikliğini kabul etti. Bakanlık hazırlık ve kapsam bildirdi. Altıntaş’ın yasama işlemindeki katkısı açık.',
        change_limit + ' ' + statement_limit,
        '28 Aralık 2023’te 7491’in 54. maddesiyle geçici 98’deki çalışma nedeniyle dışarıda bırakma hükmü kaldırıldı.')

payment_limit = ('SGK’nın 2023 raporu kişi ve toplam tutarı toplu olarak bildiriyor. Kişi başına banka hareketleri '
                 've çiftçi ile esnaf ayrımı açık. 2024 raporundaki Ocak aktarımı Kurumun muhasebe kaydı.')
payment = event(
    stem + '-payment', None, 'SGK’nın Aralık 2023 ek ödeme için bildirdiği gerçekleşme',
    'SGK, kapsam genişlemesinden sonra yaklaşık 4,7 milyon kişiye 23,4 milyar TL tutarında ödeme yapıldığını bildirdi.',
    [(stem + '-sgk2024-month', 'action', 'document', '2024 raporu hak sahiplerine ödemeyi Aralık 2023’e tarihlendiriyor.'),
     (stem + '-sgk2023-initial-total', 'initiative', 'document', 'İlk grup için açıklanan yaklaşık kişi ve tutar, sonraki gruptan ayrı.'),
     (stem + '-sgk2023-additional-a', 'result', 'document', 'SGK 4/1(a) ve 4/1(b) için ayrı kişi sayılarını veriyor.'),
     (stem + '-sgk2023-additional-c', 'result', 'document', 'SGK 4/1(c) için ayrı kişi sayısı veriyor.'),
     (stem + '-sgk2023-additional-total', 'result', 'document', 'SGK yaklaşık 4,7 milyon kişi ve 23,4 milyar TL gerçekleşme bildiriyor.'),
     (stem + '-sgk2024-transfer', 'result', 'document', '2024 raporu Kuruma Ocak ayındaki ayrı aktarımı bildiriyor.')],
    payment_limit, unknown_reason='SGK faaliyet raporları ödeme ayını Aralık 2023 olarak veriyor. Tam ödeme günü kaynakta açık.')
records['practice_event'][-1]['common_event_key'] = 'sgk-gecici98-calisan-emekli-ek-odeme-2023-aralik'
assert 3_209_542 + 1_076_734 + 402_669 == 4_688_945
compare(stem + '-payment', topic, payment, statement,
        'Altıntaş’ın çalışan emeklilerin kapsamı hakkındaki itirazı, SGK’nın daha sonra çalışma nedeniyle kapsam dışında kalanlara ilişkin bildirdiği toplu ödeme ile karşılaştırıldı.',
        'Kanun 28 Aralık’ta yayımlandı. SGK ödemeyi Aralık 2023, Kuruma aktarımı Ocak 2024 olarak kaydediyor.',
        'Gerçekleşme Sosyal Güvenlik Kurumunun faaliyet raporlarına dayanıyor. 27 Kasım Bakan açıklamasındaki 4,6 milyon kişi bir öngörüydü.',
        payment_limit + ' ' + statement_limit,
        'SGK 23,4 milyar TL ve yaklaşık 4,7 milyon kişi bildirdi. Üç sigortalılık grubunun rapordaki sayıları toplam 4.688.945 kişi ediyor.')
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
for name,content in [('pension-5000-draft.json',package),('pension-5000-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
