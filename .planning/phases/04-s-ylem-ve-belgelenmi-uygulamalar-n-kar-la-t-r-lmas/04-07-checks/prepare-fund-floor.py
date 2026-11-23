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
aux=read(here/'fund-floor-source-records.json')
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
        aid=f'fund-floor-reading-{lane}-{topic}-{vid}'
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
assert party == 'iyi'
topic = 'makroekonomik-politika'
oct7, summary7, oct20, oct22, summary22, law, final = ('0407-fund-'+token+'-' for token in
    ('oct07','oct07-summary','oct20','oct22','oct22-summary','law','law-text'))


def contribution(stem, eid, day, name, authority, references, claim, limit, kind):
    person, actor, cid, fid = (stem+tail for tail in ('-person','-actor','-contribution','-finding'))
    new('person',id=person,name=name)
    new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,
        authorization_passage_id=authority)
    finding(fid,claim,[authority,*references],limit)
    records['practice_contribution'].append(dict(id=cid,event_id=eid,party_id=party,actor_id=actor,
        contribution_kind=kind,finding_id=fid,authority_passage_id=authority,membership_passage_id=None,
        responsibility_limit=limit))
    records['practice_actor_period'].append(dict(contribution_id=cid,valid_from=day,valid_to=day,
        identity_passage_id=authority))
    for k in ('practice_contribution','practice_contribution.finding_id'):
        task(k,cid,claim,limit)


opening = '0407-iyi-2026-fund-1007'
opening_limit = ('7 Ekim’de fon piyasasına ilişkin yürütme açıklaması ve grup görüşmeleri kayda geçti. '
    'Araştırma komisyonunun kurulması, iade ve konuşmacıların iddialarının bağımsız doğrulaması açık.')
opening_context = ('Cumhurbaşkanı Yardımcısı Cevdet Yılmaz fon piyasalarına ilişkin Genel Kurulda açıklama yaptı. '
    'Siyasi parti grupları ve grubu bulunmayan bir milletvekili görüşlerini bildirdi.')
evidence7 = [
    (summary7+'role','action','document','Birleşim özeti Erhan Usta ve Burak Dalgın’ı İYİ Parti Grubunun konuşmacıları arasında kaydediyor.'),
    (oct7+'usta-role','action','document','Usta 7 Ekim’de İYİ Parti Grubu adına söz aldı.'),
    (oct7+'usta-plan','action','document','Usta fonlara ilişkin Mecliste komisyon kurulmasını istedi.'),
    (oct7+'dalgin-role','action','document','Dalgın 7 Ekim’de İYİ Parti Grubu adına söz aldı.'),
    (oct7+'dalgin-plan','action','document','Dalgın araştırma komisyonunda grupların aynı sayıda temsilini önerdi.'),
]
event7 = event(opening,'2026-10-07','TBMM 3. Birleşimde fon piyasası açıklaması ve görüşler',opening_context,evidence7,opening_limit)
records['practice_event'][-1]['common_event_key'] = 'tbmm-28-5-003-fon-piyasasi-bilgilendirme'
refs7 = [row[0] for row in evidence7]
scope = readings(topic,'event',refs7)
reason = ('7 Ekim’deki konuşmalarla aynı kapsamda daha önceki İYİ Parti söylemi araştırılıyor. '
    '14 Ekim komisyonu ve sonraki teklif görüşmeleri ayrı işlemler.')
candidate = opening+'-unmatched'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=event7,relation_id=None,
    state='unmatched',reason=reason,passage_ids=encoded(refs7)))
task('practice_candidate',candidate,reason,opening_limit)
readings(topic,'statement',refs7)
contribution(opening+'-usta',event7,'2026-10-07','ERHAN USTA',oct7+'usta-role',[oct7+'usta-plan'],
    'Erhan Usta, İYİ Parti Grubu adına fon işlemlerini araştırmak üzere Mecliste komisyon kurulmasını istedi.',
    opening_limit,'support')
contribution(opening+'-dalgin',event7,'2026-10-07','BURAK DALGIN',oct7+'dalgin-role',[oct7+'dalgin-plan'],
    'Burak Dalgın, İYİ Parti Grubu adına araştırma komisyonunda grubu bulunan partilerin eşit temsilini istedi.',
    opening_limit,'support')

stem = '0407-iyi-2026-fund-7596'
statement,target,quote = (stem+tail for tail in ('-statement','-target','-quote'))
goal = ('Erhan Usta 20 Ekim’de İYİ Parti Grubu adına konuşurken, suça bulaşmamış olsa da olağanüstü kazanç '
        'sağlayıp fondan çıkan kişilerden emsali aşan getirinin zorunlu geri alınmasını istedi.')
period_limit = ('Görüşülen 294 sıra sayılı teklif 22 Ekim’de kabul edildi. Tutanak elektronik oylama ve kabulü '
    'gösteriyor. İsimli kesin oylar ve tahsilatın uygulamadaki sonucu açık.')
separate = ('Kanunun 4. maddesi bazı olağanüstü getiriler için isteğe bağlı iadeyi öngörüyor. '
    '5. madde kayıp veya zarardan sorumlu olduğu belirlenenler için ayrı tahsil ve takip usulü getiriyor.')
statement_refs=[oct20+'role',oct20+'scope',oct20+'goal']
finding(target,goal,statement_refs,'İYİ grup sıfatı, hedeflenen kişiler ve zorunlu iade çağrısı 8. Birleşimde birlikte okundu.')
finding(quote,passages[oct20+'goal']['exact'],[oct20+'goal'],'Zorunlu iade çağrısından kısa birebir ifade.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-10-20',date_precision='day',
    version_id=passages[oct20+'goal']['version_id'],period_basis='8. Birleşimde İYİ Parti Grubunun 2/3939 konuşması.',
    uncertainty_reason=None,comparison_row_id='04-03-v3-0306-iyi-program-makroekonomik-politika-row'))
readings(topic,'statement',statement_refs)
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[oct20+'goal']['exact'])):
    task(kind,statement,claim,period_limit)

context = ('TBMM 22 Ekim 2026’da 294 sıra sayılı 2/3939 teklifinin tümünü elektronik oylamayla kabul etti. '
    'Teklif 7596 sayılı Kanuna dönüştü.')
evidence22 = [
    (oct22+'sunat-role','action','document','Şenol Sunat 9. madde görüşmesinde İYİ Parti Grubu adına söz aldı.'),
    (oct22+'sunat-objection','action','document','Sunat olağan dışı getiriler için isteğe bağlı iadeye itiraz etti.'),
    (oct22+'electron','action','document','Başkan Divanda ihtilaf üzerine elektronik oylama yapılacağını söyledi.'),
    (oct22+'accept','result','document','Başkan teklifin kabul edildiğini ve kanunlaştığını açıkladı.'),
    (summary22+'accept','result','document','Birleşim özeti 294 sıra sayılı teklifin kabulünü kaydetti.'),
    (law+'date','result','document','TBMM kanun kartı 22 Ekim 2026 kabulünü kaydediyor.'),
    (final+'voluntary','result','document','4. madde 4. fıkra belirli getiriler için isteğe bağlı iade düzenliyor.'),
    (final+'shares','result','document','Aynı fıkra belirli pay getirileri için genel hisse iade hesabını düzenliyor.'),
    (final+'liability','result','document','5. madde 2. fıkra sorumlu olduğu belirlenenlerin sorumluluğunu düzenliyor.'),
    (final+'enforcement','result','document','5. madde 4. fıkra TMSF’ye ayrı takip ve tahsil görevi veriyor.'),
]
eid = event(stem,'2026-10-22','2/3939 teklifinin 10. Birleşimde kabulü',context,evidence22,period_limit)
records['practice_event'][-1]['common_event_key'] = 'tbmm-28-5-010-2-3939-yatirim-fonlari-7596'
ref22 = [row[0] for row in evidence22]
scope = readings(topic,'event',ref22+[law+'pub'])
contribution(stem+'-sunat',eid,'2026-10-22','ŞENOL SUNAT',oct22+'sunat-role',[oct22+'sunat-objection'],
    'Şenol Sunat İYİ Parti Grubu adına olağan dışı getirilerin iadesinin isteğe bağlı tutulmasına itiraz etti.',
    'Konuşma 9. madde önergesi görüşmesinde yapıldı. Son oylamada Sunat’ın kişisel oyu açık.','objection')

result,explanation,rid = (stem+tail for tail in ('-result','-explanation','-relation'))
outcome = context+' '+separate
comparison = ('Usta’nın olağanüstü kazanç için zorunlu iade çağrısı ve 7596’nın 4. maddesi aynı geri ödeme '
    'aracına farklı koşullar getiriyor. 5. maddedeki belirlenmiş sorumlular ayrı.')
explain = goal+' '+separate+' '+period_limit
legal_refs = [final+'voluntary',final+'liability',final+'enforcement']
finding(result,outcome,[oct22+'accept',law+'date',*legal_refs],'Kabul tutanağı, kanun kimliği, 4. ve 5. maddeler ayrı okundu.')
finding(explanation,explain,[*statement_refs,oct22+'sunat-objection',*legal_refs],
    '20 ve 22 Ekim TBMM tutanakları ile kanun maddeleri karşılaştırıldı.')
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=comparison,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=explanation,temporal_context='20 Ekim grup konuşması ve 22 Ekim Genel Kurul kabulü.',
    authority_context='Usta ve Sunat grup adına konuştu. Oylama sonucunu Genel Kurul Başkanı ilan etti.',
    uncertainty_reason=period_limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=comparison,passage_ids=encoded(ref22)))
for kind,claim in (('practice_relation',explain),('practice_relation.target_finding_id',goal),
                   ('practice_relation.result_finding_id',outcome),('practice_relation.explanation_finding_id',explain)):
    task(kind,rid,claim,period_limit)

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
for name,content in [('fund-floor-draft.json',package),('fund-floor-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
