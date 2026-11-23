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
aux=read(here/'pension-floor-yeni-yol-source-records.json')
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
        aid=f'yy-7573-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='TBMM teklifi, komisyon ve Genel Kurul tutanakları, kesin cetvel ve kanun metni.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'yeni-yol'
stem = '0408-yeni-yol-2026-7573'
topic = 'sosyal-guvenlik'
base = '0408-floor-'
early, floor, committee, final, ballot, bill, law = [base+suffix+'-' for suffix in (
    'yy-2026-46','yy-2026-48','iyi-7573-commission','iyi-7573-50','iyi-7573-ballot',
    'pension-bill-23464','pension-text-7573')]
statement, target, quote = (stem+tail for tail in ('-statement','-target','-quote'))
goal = 'Selçuk Özdağ, 13 Ocak 2026’da Yeni Yol Grubu adına en düşük emekli aylığının asgari ücret düzeyine çıkarılmasını savundu.'
limit = ('Komisyon önerisi brüt asgari ücret olarak açıklandı. 23 Ocak kesin oyları 248 sıra sayılı teklifin tümü üzerindeydi. '
         'Komisyondaki önergeye ilişkin isimli oy, grup kararı ve fiilî emekli ödemeleri açık.')
finding(target,goal,[early+'role',early+'goal',early+'agenda'],
    '46. Birleşim ham tutanağında temsil sıfatı, genel görüşmenin konusu ve aylık çağrısı birlikte okundu.')
finding(quote,passages[early+'goal']['exact'],[early+'goal'],
    'Özdağ’ın aylık çağrısından kısa birebir ifade.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-01-13',date_precision='day',
    version_id=passages[early+'goal']['version_id'],
    period_basis='46. Birleşimde Yeni Yol Grubu konuşması. Tutanaktaki gündem ayrı genel görüşme önergesi.',
    uncertainty_reason=None,comparison_row_id='04-03-v3-0307-yeni-yol-sosyal-guvenlik-program'))
readings(topic,'statement',[early+'role',early+'goal',early+'agenda'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[early+'goal']['exact'])):
    task(kind,statement,claim,'13 Ocak konuşması öncül siyasi hedef. 15 Ocak imzalı değişiklik önergesi ve 23 Ocak son oylaması ayrı.')

evidence = [
    (bill+'id','initiative','document','Teklifin esas numarası 2/3464.'),
    (committee+'kisacik','initiative','document','15 Ocak’ta Kısacık 5. madde için asgari ücret önergesi verdi. Konuşmasında brüt ücreti esas aldı. Komisyon önergeyi kabul etmedi.'),
    (floor+'role','initiative','document','20 Ocak’ta Kısacık teklifin tümü için Yeni Yol Grubu adına konuştu.'),
    (floor+'objection','initiative','document','Kısacık, teklifin 20.000 TL tutarına itiraz etti.'),
    (ballot+'kisacik','action','document','Sadullah Kısacık için kesin cetvel 23 Ocak saat 00.52.29 elektronik ret kaydediyor.'),
    (ballot+'bulent','action','document','Bülent Kaya için kesin cetvel 23 Ocak saat 00.52.28 elektronik ret kaydediyor.'),
    (final+'accept','result','document','Başkan 248 sıra sayılı teklifin kabul edildiğini açıkladı.'),
    (final+'tally','result','document','Birleşim tutanağında 247 kabul ve 179 ret açıklandı.'),
    (ballot+'tally','result','document','Ayrı kesin cetvel 245 kabul ve 179 ret gösteriyor.'),
    (ballot+'duplicates','result','document','Kesin cetvelde 426 toplam ve iki mükerrer oy var.'),
    (law+'floor','result','document','7573 sayılı Kanunun 7. maddesi 16.881 TL yerine 20.000 TL getirdi.'),
    (law+'effect','result','document','Kanun 7. maddeyi Ocak 2026 ödeme döneminden itibaren geçerli kıldı.'),
]
context = ('Yeni Yol adına 20.000 TL tabanı eleştirildi. Sadullah Kısacık’ın komisyon önergesi reddedildi. '
           '2/3464’ün tümü 23 Ocak 2026’da kabul edildi ve 7573 sayılı Kanunda en düşük aylık 20.000 TL olarak düzenlendi.')
eid = event(stem,'2026-01-23','2/3464 teklifinin kabulü ve 7573’teki emekli aylığı tabanı',context,evidence,limit)
records['practice_event'][-1]['common_event_key'] = 'tbmm-28-4-050-2-3464-7573'
refs = [row[0] for row in evidence]
scope = readings(topic,'event',refs+[bill+'law',base+'pension-law-7573-day',committee+'cover'])
rid,result,expl = (stem+tail for tail in ('-relation','-result','-explanation'))
compare = 'Özdağ 13 Ocak’ta aylık tabanı için asgari ücreti savundu. Açıklanan komisyon önergesi ve kabul edilen 7. madde aynı aylık tabanına farklı tutarlar öneriyor.'
outcome = '2/3464, 23 Ocak’ta kabul edildi. 7573 sayılı Kanun, Ocak ödeme döneminden geçerli olmak üzere tutarı 20.000 TL’ye yükseltti.'
explanation = ('13 Ocak Yeni Yol Grup konuşmasında en düşük aylık için asgari ücret savunuldu. '
               'Kısacık’ın 15 Ocak komisyon önergesi reddedildi. 23 Ocak kesin cetvelinde Yeni Yol Partisi etiketli 20 satırda '
               '16 ret ve dört katılmadı var. Kısacık ve Bülent Kaya teklifin tümüne ret verdi. '
               'Tutanakta 247 kabul ve 179 ret ilan edildi. Kesin cetvel 245 kabul, 179 ret ve iki mükerrer oy kaydediyor. '
               'Kabul edilen 7. madde 20.000 TL düzenliyor.')
finding(result,outcome,[final+'accept',law+'floor',law+'effect'],
    'Genel Kurul kabulü, kanun metnindeki tutar ve geçerli ödeme dönemi özgün kaynakta ayrı okundu.')
finding(expl,explanation,[early+'goal',committee+'kisacik',floor+'objection',ballot+'kisacik',ballot+'bulent',
    final+'tally',ballot+'tally',ballot+'duplicates',law+'floor'],
    'Kesin cetvelde Yeni Yol Partisi etiketli 20 satır tek tek kontrol edildi. Tutanak ve kesin cetvelin sayım farkı korundu.')
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=expl,temporal_context='13 Ocak konuşması, 15 Ocak komisyon önergesi, 20 Ocak Genel Kurul konuşması ve 23 Ocak kabulü.',
    authority_context='Özdağ ve Kısacık grup adına konuştu. Kısacık komisyon önergesini verdi. Kesin cetveldeki oylar kişi bazında.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',explanation),('practice_relation.target_finding_id',goal),
                   ('practice_relation.result_finding_id',outcome),('practice_relation.explanation_finding_id',explanation)):
    task(kind,rid,claim,limit)

dispute = stem+'-vote-dispute'
dispute_finding = dispute+'-finding'
dispute_text = ('50. Birleşim tutanağı 247 kabul ve 179 ret duyurusunu kaydediyor. TBMM kesin açık oy cetvelinde '
                '245 kabul, 179 ret ve iki mükerrer oy görünüyor. Her iki kayıt da teklifin kabul edildiğini gösteriyor.')
finding(dispute_finding,dispute_text,[final+'tally',ballot+'tally',ballot+'duplicates'],
    'Oturumda açıklanan ve kesin cetvelde görünen sayılar ayrı kayıtlar. Kabul sonucu ortak.')
records['practice_dispute'].append(dict(id=dispute,event_id=eid,summary_finding_id=dispute_finding,
    supported_points='426 toplam, 179 ret ve teklifin kabulü iki kayıtta da aynı.',
    disputed_points='Oturumda 247 kabul açıklandı. Kesin cetvel 245 kabul ve iki mükerrer oy gösteriyor.',
    unresolved_points='Tutanaktaki ilan ve kesin cetvelin kabul sayıları ayrı kayıtlarda korunuyor.'))
task('practice_dispute',dispute,dispute_text,'Kesin cetvelde iki pusula mükerrer olarak işaretli.')
task('practice_dispute.summary_finding_id',dispute,dispute_text,'Tutanak ilanı ve kesin cetvel birlikte okunuyor.')
for pid,point,role in (
    (final+'tally','Birleşim duyurusunda 247 kabul ve 179 ret.','conflict'),
    (ballot+'tally','Kesin cetvelde 245 kabul ve 179 ret.','support'),
    (ballot+'duplicates','Cetvel iki mükerrer ve 426 toplam gösteriyor.','support'),
):
    position=passages[pid]['section']
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,point=point,
        source_position=position,role=role))
    task('practice_dispute_evidence','|'.join((dispute,pid,point,role)),point,position)
for entry in entries:
    dest=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in dest: dest.append(entry['values'])
for table,rows in records.items():
    dest=snapshot.setdefault(table,[])
    dest.extend(row for row in rows if row not in dest)
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
        reason=kind+' hedefinin asıl kaynakları, tarihi ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('pension-floor-yeni-yol-draft.json',package),('pension-floor-yeni-yol-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
