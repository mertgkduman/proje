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
aux=read(here/'pension-separate-source-records.json')
party=aux['party_id']
package=read(data/f'practices/04-{party}.json')
review=read(data/f'practices/04-{party}-review.json')
snapshot=read(data/'releases'/package['base_release']/'records.json')
inventory=read(data/'practices/04-inventory.json')
entries=package['entries']
for entry in aux['entries']:
    row=entry['values']
    source_key=row.get('version_id',row.get('id',''))
    if source_key.startswith(('0412-floor-','0412-retire-file1597','0412-retire-signed1597')):
        entries.append(entry)
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
        aid=f'retirement-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='İmzalı teklif veya önerge, TBMM kayıt sayfası ve tutanak.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'demokrat'
topic = 'sosyal-guvenlik'
stem = '0412-demokrat-2026-7573'
old_file, old_signed = '0412-retire-file1597-', '0412-retire-signed1597-'
final, ballot, law, registry = ('0412-floor-'+suffix+'-' for suffix in (
    'iyi-7573-50','iyi-7573-ballot','pension-text-7573','pension-law-7573'))
statement, target, quote = (stem+tail for tail in ('-statement','-target','-quote'))
goal = ('Eylül 2023’te Demokrat Parti milletvekilleri Cemal Enginyurt, Haydar Altıntaş ve Mehmet Salih Uzun, '
        '2/1597 sayılı teklifte en düşük emekli aylığının net asgari ücretten az olmamasını önerdi.')
limit = ('2/1597 ve 2/3464 ayrı teklif. 7573 sayılı Kanunun 7. maddesi 2/3464’ten geldi. '
         'Haydar Altıntaş’ın kesin cetvel satırı KATILMADI. Bu kayıttan oylama tercihi veya fiilî ödeme sonucu çıkarılamıyor.')
finding(target,goal,[old_signed+'signature',old_signed+'goal',old_file+'filed'],
    'İmzalı teklifin kapağı, 3. madde ve TBMM geliş tarihi okundu.')
finding(quote,passages[old_signed+'goal']['exact'],[old_signed+'goal'],
    'İmzalı teklifin 3. maddesinden birebir ifade.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2023-09-28',date_precision='day',
    version_id=passages[old_signed+'goal']['version_id'],
    period_basis='2/1597 imzalı kapak ve TBMM başvuru kaydı 28 Eylül 2023.',
    uncertainty_reason=None,comparison_row_id='04-03-v3-0313-demokrat-sosyal-guvenlik'))
readings(topic,'statement',[old_signed+'signature',old_signed+'goal',old_signed+'index',
                            old_file+'filed',old_file+'sent',old_file+'status'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[old_signed+'goal']['exact'])):
    task(kind,statement,claim,'2/1597’nin 3. maddesi tabanı, ilk iki maddesi 15.965 göstergeyle ek ödemeyi ayrı düzenliyor.')

evidence = [
    (final+'accept','result','document','Başkan 248 sıra sayılı teklifin kabul edildiğini duyurdu.'),
    (final+'tally','result','document','Oturumda 247 kabul ve 179 ret açıklandı.'),
    (ballot+'tally','result','document','Kesin cetvel 245 kabul ve 179 ret kaydediyor.'),
    (ballot+'duplicates','result','document','Kesin cetvelde iki mükerrer oy ve 426 toplam var.'),
    (ballot+'altintas','action','document','Kesin cetvelde Demokrat Parti etiketli Haydar Altıntaş KATILMADI olarak görünüyor.'),
    (registry+'day','result','document','Kanun kabul tarihi 23 Ocak 2026.'),
    (law+'floor','result','document','7573 sayılı Kanunun 7. maddesi alt tutarı 20.000 TL olarak belirledi.'),
    (law+'effect','result','document','Tutar Ocak 2026 ödeme döneminden itibaren geçerli düzenlendi.'),
]
context = ('2/3464 teklifinin tümü 23 Ocak 2026’da kabul edildi. 7573 sayılı Kanunda en düşük emekli aylığı 20.000 TL oldu. '
           'Kesin cetvelde Haydar Altıntaş için KATILMADI yazıyor.')
eid = event(stem,'2026-01-23','2/3464’ün kabulü ve 7573 sayılı Kanundaki emekli aylığı tabanı',context,evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-4-050-2-3464-7573',
    occurrence_basis='50. Birleşim tutanağı, kesin açık oy cetveli ve TBMM kanun metni.')
refs = [row[0] for row in evidence]
scope = readings(topic,'event',refs+[registry+'session',old_file+'status'])
rid,result,explanation = (stem+tail for tail in ('-relation','-result','-explanation'))
compare = '2/1597’nin 3. maddesi ve 7573’ün 7. maddesi aynı 5510 Ek 19 ödeme tabanını düzenliyor.'
outcome = '2/3464 kabul edildi. 7573 sayılı Kanunun 7. maddesi Ocak 2026 ödeme döneminden itibaren 20.000 TL belirledi.'
connection = ('Demokrat Parti milletvekillerinin 2/1597 teklifi aynı ödeme tabanı için net asgari ücret istedi. '
              '2/3464’ten çıkan 7573 sayılı Kanun 20.000 TL belirledi. Erişilen 2/1597 TBMM dosyası Komisyonda görünüyor. '
              'Haydar Altıntaş 7573’e dönüşen teklifin tümü için kesin cetvelde KATILMADI.')
finding(result,outcome,[final+'accept',law+'floor',law+'effect'],
    'Meclis kabulü, kanun tutarı ve ödeme dönemi ayrı pasajlarda doğrulandı.')
finding(explanation,connection,[old_signed+'goal',old_file+'status',law+'floor',ballot+'altintas'],
    'İki esas numarası, aynı norm, farklı araç, güncel işlem durumu ve kişi satırı ayrı kaydedildi.')
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=explanation,temporal_context='28 Eylül 2023 teklif ile 23 Ocak 2026’da kabul edilen ayrı teklif.',
    authority_context='2/1597 üç Demokrat Parti milletvekilinin teklifi. 7573’ün kabulü Genel Kurul kararı.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',connection),('practice_relation.target_finding_id',goal),
                   ('practice_relation.result_finding_id',outcome),('practice_relation.explanation_finding_id',connection)):
    task(kind,rid,claim,limit)

dispute = stem+'-vote-dispute'
summary = dispute+'-finding'
dispute_text = ('Birleşim tutanağında 247 kabul, kesin cetvelde 245 kabul ve iki mükerrer oy yazıyor. '
                'Her iki kayıtta 179 ret, toplam 426 ve teklifin kabulü aynı.')
finding(summary,dispute_text,[final+'tally',ballot+'tally',ballot+'duplicates'],
    'İlk ilan ve kesin cetvel ayrı kaynaklardan doğrulandı.')
records['practice_dispute'].append(dict(id=dispute,event_id=eid,summary_finding_id=summary,
    supported_points='179 ret, 426 toplam ve kabul sonucu ortak.',
    disputed_points='247 kabul ilanı ve 245 kesin kabul ile iki mükerrer satır.',
    unresolved_points='Tutanak ile kesin cetvelin kabul toplamları ayrı kaynak atfıyla korunuyor.'))
task('practice_dispute',dispute,dispute_text,'İki mükerrer satır kesin cetvelde var.')
task('practice_dispute.summary_finding_id',dispute,dispute_text,'İki kaynak ayrı.')
for pid,point,role in (
    (final+'tally','Oturumda 247 kabul açıklandı.','conflict'),
    (ballot+'tally','Kesin cetvelde 245 kabul var.','support'),
    (ballot+'duplicates','Kesin cetvelde iki mükerrer var.','support'),
):
    position=passages[pid]['section']
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,point=point,source_position=position,role=role))
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
for name,content in [('pension-separate-draft.json',package),('pension-separate-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
