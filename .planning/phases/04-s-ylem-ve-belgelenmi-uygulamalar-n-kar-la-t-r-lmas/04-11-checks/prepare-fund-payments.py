"""Follow the earlier statement through the SPK decision and reported payments."""

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
aux=read(here/'fund-payments-source-records.json')
party=aux['party_id']
package=read(data/f'practices/04-{party}.json')
review=read(data/f'practices/04-{party}-review.json')
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
        aid=f'fund-payments-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='TBMM birleşim tutanağı ve ilgili işlem belgeleri.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'saadet'
topic = 'makroekonomik-politika'
earlier = '0411-saadet-2026-fund-7596'
statement, target = earlier+'-statement', earlier+'-target'
statement_refs = ['0411-fund-arikan-'+key for key in ('authority','date','bill','critique')]
goal = next(entry['values']['text'] for entry in entries if entry['kind']=='finding' and entry['values']['id']==target)
decision, guide, press, reply = ('0411-fund-payments-'+key+'-' for key in ('decision','guide','press','reply'))

def record(stem, common_key, day, title, context, basis, evidence, comparison, outcome, limitation):
    eid = event(stem, day, title, context, evidence, limitation)
    records['practice_event'][-1].update(common_event_key=common_key, occurrence_basis=basis)
    refs = [item[0] for item in evidence]
    scope = readings(topic, 'event', refs)
    rid, result, explanation = (stem+tail for tail in ('-relation','-result','-explanation'))
    finding(result, outcome, refs, 'İşlem ve bildirimin kapsamı özgün nüshalarda okundu.')
    detail = comparison+' '+outcome+' '+limitation
    finding(explanation, detail, statement_refs+refs, '21 Ekim açıklaması sonraki işlem belgeleriyle karşılaştırıldı.')
    records['practice_relation'].append(dict(id=rid, statement_id=statement, event_id=eid, party_id=party,
        topic_id=topic, scope_id=scope, comparability_reason=comparison, target_finding_id=target,
        result_finding_id=result, explanation_finding_id=explanation, temporal_context=f'21 Ekim açıklaması ve {day} tarihli işlem.',
        authority_context='Arıkan Saadet Partisi Genel Başkanı olarak konuştu. Sonraki işlem yetkili kurumların kayıtlarında yer alıyor.',
        uncertainty_reason=limitation))
    records['practice_candidate'].append(dict(id=stem+'-candidate', scope_id=scope, event_id=eid, relation_id=rid,
        state='eligible', reason=comparison, passage_ids=encoded(refs)))
    for kind, claim in (('practice_relation', detail), ('practice_relation.target_finding_id', goal),
                        ('practice_relation.result_finding_id', outcome), ('practice_relation.explanation_finding_id', detail)):
        task(kind, rid, claim, limitation)

first = '0411-saadet-2026-spk-761903'
context = 'SPK 27 Ekim 2026 tarihli 76/1903 kararıyla 7596 kapsamındaki üç kurucunun fonlarına ilişkin tasfiye ve ödeme usullerini belirledi.'
limit = ('Bülten, Tera, Pusula ve Atlas’ın kararda belirtilen fonlarını kapsıyor. '
         'Karar tarihli usullerin bireysel uygulaması fon ve hak sahibi düzeyinde araştırılıyor.')
evidence = [
    (decision+'identity','result','document','2026/76 Bülteni 27 Ekim 76/1903 kararını yayımladı.'),
    (decision+'scope','action','document','Pusula ve Atlas fonları Ziraat Bankasına, Tera fonları İş Bankasına verildi.'),
    (decision+'priority','result','document','Karar para piyasası ibareli fonları önceliklendirdi.'),
    (decision+'ceiling','result','document','Karar, endekslenmemiş net yatırım tutarı ve 1 milyon TL sınırlarını belirledi.'),
    (decision+'deduction','result','document','Karar ara ödemenin nihai tasfiye ödemesinden mahsubunu düzenledi.'),
    (guide+'decision','action','document','SPK kararı ve uygulanacak usulleri duyurdu.'),
    (guide+'banks','action','document','Kılavuz iki bankanın görev alanını açıklıyor.'),
]
record(first, 'spk-2026-76-1903-fon-tasfiye-odeme-usulleri','2026-10-27',
    'SPK 76/1903 ile fon tasfiye ve ödeme usullerini belirledi', context,'SPK 2026/76 Bülteni ve kurul duyurusu.',
    evidence,'21 Ekim’de eleştirilen SPK ödeme yetkisi, 27 Ekim kararında belirli kapsam ve koşullarla kullanıldı.',
    context+' Para piyasası fonlarına öncelik verildi. 1 milyon TL ara ödeme tavanı ve nihai ödemeden mahsup öngörüldü.',limit)

second = '0411-saadet-2026-fund-initial-payment'
context = ('İletişim Başkanlığı, olağanüstü tasfiyedeki ilk ara ödemelerin 30 Ekim 2026’da '
           'Atlas, Pusula ve Tera’nın ilgili fonlarında başladığını bildirdi.')
limit = ('29,3 milyar TL olağanüstü tasfiyedeki ilk toplam için kurumsal açıklama tutarıdır. '
         'Fon ve hak sahibi bazında tutarlar ile sonraki nihai ödemeler araştırılıyor.')
evidence = [
    (press+'authority','action','independent_report','AA, kamuya açıklamayı İletişim Başkanlığına atfediyor.'),
    (press+'transfer','action','independent_report','Açıklamada 30 Ekim ilk ara ödeme günü olarak belirtiliyor.'),
    (press+'amount','result','independent_report','AA, İletişim Başkanlığının 29,3 milyar TL beyanını aktarıyor.'),
    (reply+'meeting','action','document','Bakanlık cevabı 3 Kasım Fon Koordinasyon Kurulu toplantısını belirtiyor.'),
    (reply+'amount','result','document','Bakanlık cevabı aynı toplantıdaki 29,3 milyar TL beyanını aktarıyor.'),
]
record(second,'fon-koordinasyon-7596-ilk-ara-odeme-2026-10-30','2026-10-30',
    '7596 kapsamındaki ilk ara ödemelerin başladığı bildirildi',context,
    'İletişim Başkanlığının AA’da aktarılan açıklaması ve Hazine ve Maliye Bakanlığının imzalı TBMM cevabı.',
    evidence,'Arıkan’ın güvence eleştirisinden sonra belirli fonlarda fiilî ara ödeme başlangıcı açıklandı.',
    context+' AA’nın aktardığı 3 Kasım açıklaması ve Bakanlığın 4 Kasım imzalı cevabı 29,3 milyar TL tutarını bildiriyor.',limit)

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
for name,content in [('fund-payments-draft.json',package),('fund-payments-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
