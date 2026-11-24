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
aux=read(here/'election-2023-source-records.json')
party=aux['party_id']
package=read(here/'pension-5000-draft.json')
review=read(here/'pension-5000-review-draft.json')
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
            boundary_reason='Ortak aday duyurusu ve YSK’nın ilgili başvuru, kesin liste ve oy belgeleri incelendi.'))
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
        aid=f'election-2023-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Ortak aday ve YSK işlemlerine ilişkin kaynak.',state='examined',attempt_ids=encoded([aid])))
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
assert sha256((here / 'pension-5000-draft.json').read_bytes()).hexdigest() == '824f4e233da39555a29618317a79274e49eef97f5b6165767c5787c36814b66d'
assert sha256((here / 'pension-5000-review-draft.json').read_bytes()).hexdigest() == 'f855b0e9d1c45d01796f5301b637fd60b55f0c0d0ff2ed99547c68932672c13b'


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


stem = '0412-election-2023'
topic = 'siyasal-ittifaklar'
statement_limit = ('6 Mart metni Demokrat Parti’nin yayımladığı ittifak yol haritası. Ocak açıklamasında ortak adayın seçilmesi '
                   've TBMM’de gerekli anayasa çoğunluğu geçiş koşulları olarak belirtiliyor.')
statement = register_statement(
    stem, topic, '2023-03-06', 'Demokrat Parti, 6 Mart ittifak metni ve 5 Ocak ortak açıklaması.',
    '04-03-v3-0313-demokrat-siyasal-ittifaklar',
    'Millet İttifakı 6 Mart 2023 tarihli ortak yol haritasında Kemal Kılıçdaroğlu’nu ortak cumhurbaşkanı adayı olarak açıkladı.',
    [stem + '-agreement-candidate', stem + '-agreement-transition', stem + '-conditions-criteria'], statement_limit)

cases = (
    ('application', 'ysk-2023-254-cumhurbaskani-adaylik-basvurusu', '2023-03-24',
     'YSK’nın 24 Mart Cumhurbaşkanı adaylık başvurularını kabulü',
     '2023/254 sayılı kararda YSK, adaylık başvuru evrakını inceledi ve Kılıçdaroğlu ile Erdoğan’ın başvurularını kabul etti.',
     '6 Mart’taki ortak aday adı, 24 Mart YSK başvuru kabulünde yer alan aynı adayla karşılaştırıldı.',
     '6 Mart ortak açıklama, 24 Mart başvuru kararı. Seçim takviminde başvuru sonu 23 Mart saat 17.00.',
     'Kılıçdaroğlu’nu başvuruda CHP ve İYİ Parti Meclis grupları aday gösterdi. Demokrat Parti ve diğer ittifak partilerinin 6 Mart açıklamasındaki katkısı ayrı.',
     'YSK burada başvurunun süresi ve evrakını değerlendirdi. Kesin aday listesi 2023/321 dosyasına ait.',
     'YSK, Kemal Kılıçdaroğlu ile Recep Tayyip Erdoğan’ın başvurularını kabul etti.',
     (('id', 'action', '2023/254 sayılı başvuru inceleme kararı.'),
      ('sponsors', 'action', 'Kılıçdaroğlu’nu aday gösteren iki TBMM grubu kayıtlı.'),
      ('day', 'action', 'Karar 24 Mart’ta oybirliğiyle verildi.'),
      ('decision', 'result', 'YSK Kılıçdaroğlu ve Erdoğan başvurularını kabul etti.'))),
    ('definitive', 'ysk-2023-321-cumhurbaskani-kesin-aday-listesi', '2023-03-30',
     'YSK’nın kesin Cumhurbaşkanı aday listesi',
     'YSK 30 Mart 2023 tarihli kararıyla Kılıçdaroğlu dâhil dört adayın kesin listesini belirledi. Liste 31 Mart’ta yayımlandı.',
     '6 Mart ortak aday ilanı, YSK’nın daha sonraki kesin listesindeki aynı adayla karşılaştırıldı.',
     'YSK karar günü 30 Mart ve Resmî Gazete yayımı 31 Mart 2023.',
     'Kesin liste YSK kararıyla oluşturuldu. İttifakın rolü ortak aday açıklaması ve siyasi destek kapsamıyla sınırlı.',
     'Dört adaylı kesin liste 14 Mayıs oylaması için yayımlandı. Bu kayıt adaylığın kesinleşmesini gösteriyor.',
     'Kemal Kılıçdaroğlu, YSK’nın 31 Mart’ta yayımlanan dört adaylı kesin listesinde yer aldı.',
     (('publication', 'action', 'Resmî Gazete’nin 31 Mart 2023 tarihli 32149 sayısı.'),
      ('decision', 'action', 'Karar 30 Mart’ta oybirliğiyle verildi.'),
      ('list', 'result', 'Ek kesin aday listesinde Kılıçdaroğlu yer alıyor.'))),
    ('runoff', 'ysk-cumhurbaskani-ikinci-oylama-2023-05-28-ulke-geneli', '2023-05-28',
     'YSK bülteninde 28 Mayıs ikinci oylama sonucu',
     'YSK bülteni ikinci oylamada 27.834.589 oyla Recep Tayyip Erdoğan’ı, 25.504.724 oyla Kemal Kılıçdaroğlu’nu kaydetti.',
     '6 Mart’ta açıklanan ortak adayın seçilmesi koşulu, 28 Mayıs ikinci oylamasının YSK sonuçlarıyla karşılaştırıldı.',
     'Ortak ilan 6 Mart, ikinci oylama 28 Mayıs 2023. Bültendeki sonuç yurt içi, yurt dışı ve gümrük kapılarını kapsıyor.',
     'Oy sayılarını YSK yayımladı. İttifakın ortak aday açıklaması ile seçmenin oyu ve YSK kaydı kendi yetki alanlarında.',
     'Ülke geneli tabloda 53.339.313 geçerli oy var. Bülten kampanya koşulları, siyasi sonuç yorumları veya anayasa çoğunluğu hakkında sonuç vermiyor.',
     'YSK verilerinde Erdoğan yüzde 52,18, Kılıçdaroğlu yüzde 47,82 oy aldı. İttifakın ortak adayının seçilmesi koşulu gerçekleşmedi.',
     (('scope', 'action', 'Sonuç tablosu yurt içi, yurt dışı ve gümrük sandıklarını kapsıyor.'),
      ('total', 'result', 'Ülke geneli geçerli oy toplamı 53.339.313.'),
      ('votes', 'result', 'Toplamda Erdoğan 27.834.589, Kılıçdaroğlu 25.504.724 oy aldı.'))),
)
for key, common_key, day, title, context, basis, temporal, authority, limit, result, anchors in cases:
    case = stem + '-' + key
    refs = [(case + '-' + name, stage, 'document', point) for name, stage, point in anchors]
    eid = event(case, day, title, context, refs, limit)
    records['practice_event'][-1]['common_event_key'] = common_key
    compare(case, topic, eid, statement, basis, temporal, authority,
            limit + ' ' + statement_limit, result)
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
for name,content in [('election-2023-draft.json',package),('election-2023-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
