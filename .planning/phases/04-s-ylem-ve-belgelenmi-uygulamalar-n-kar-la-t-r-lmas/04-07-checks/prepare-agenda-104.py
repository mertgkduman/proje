"""Compare two distinct 104th sitting agenda actions with the archived IYI program."""

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
aux=read(here/'agenda-104-source-records.json')
party=aux['party_id']
package=read(data/'practices/04-iyi.json')
review=read(data/'practices/04-iyi-review.json')
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
            boundary_reason='İki grup gündem işlemi ve İYİ Parti programının ilgili bölümleri okundu.'))
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
        aid=f'agenda-104-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Parti programı, TBMM esas sicili ve ilgili birleşim tutanağı.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,key,day,title,context,basis,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=key,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis=basis))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='iyi'
assert sha256((data/'practices/04-iyi.json').read_bytes()).hexdigest()=='c64ce1c1de05d5f2662ce1ac25f1000cca43f648753f2a735c1979eaa6131fc8'
assert sha256((data/'practices/04-iyi-review.json').read_bytes()).hexdigest()=='15c155ffe954ef0d75bcc73e7cccd4c03e99cdd5e143a600d8662ca45613d0ad'
source='0407-agenda-104-'
program_version='0205-iyi-program-page-v1'
program_limit=('İYİ Parti programının HTML nüshası 11 Kasım 2026 erişimine dayanıyor. '
               'Nüshanın kabul, değişiklik ve 2 Temmuz 2025’te yürürlük durumu açık.')
common_limit=('Gündem talebinin reddi 2 Temmuz 104. Birleşim işlemi. Esas sicili 23 Kasım erişiminde Gündemde. '
              'Kişisel oy, asıl araştırmanın açılışı ve önerilen önlemlerin uygulaması açık.')
events=(
    ('2881','sanayi-politikasi','Yasin Öztürk','10/2881 tekstil araştırmasının ön görüşme talebinin reddi',
     'Yeni Yol Grubu, Mehmet Emin Ekmen ve 21 milletvekilinin tekstil sektörüne ilişkin 10/2881 araştırma önergesinin ön görüşmesinin 2 Temmuz 2025 birleşiminde yapılmasını istedi. Genel Kurul bu gündem talebini reddetti.',
     'uluslararası marka oluşturulmasını ve patent tescilini destekleyeceğiz.',
     'Sanayi Politikaları, uluslararası marka ve patent desteği',
     'İYİ Parti programı sanayinin rekabeti için uluslararası marka oluşturulmasının ve patent tescilinin desteklenmesini öngörüyor.',
     'Yasin Öztürk, 2 Temmuz’da İYİ Parti Grubu adına tekstil, hazır giyim ve Denizli üretimi hakkında konuştu. Tasarım, dijitalleşme ve markalaşmanın desteklenmesini istedi.',
     'Programın markalaşma aracı markalaşma talebiyle karşılaştırıldı. Program nüshasının olay günündeki yürürlüğü ve istenen desteklerin uygulanması açık.',(
        ('register-2881-id','initiative','TBMM esas numarası 10/2881.'),
        ('register-2881-day','initiative','Araştırma önergesinin Başkanlığa geliş tarihi 2 Temmuz 2025.'),
        ('signed-2881-id','initiative','İmzalı dosya esas numarasını taşıyor.'),
        ('signed-2881-scope','initiative','İmzalı gerekçe ihracat kaybı ve istihdam etkilerinin incelenmesini istiyor.'),
        ('floor-agenda-2881','action','İlk grup gündem önerisi aynı gün ön görüşme istedi.'),
        ('floor-authority-2881','action','Başkan İYİ Parti Grubu adına Yasin Öztürk’e söz verdi.'),
        ('floor-branding-2881','action','Öztürk tasarım, dijitalleşme ve markalaşmaya destek istedi.'),
        ('floor-vote-2881','result','Başkan ilk ön görüşme talebinin kabul edilmediğini duyurdu.'),
        ('register-2881-pending','result','TBMM esas sicili erişimde Gündemde görünüyor.'),
        ('papers-2881','result','9 Temmuz gelen kâğıtların 26. sırası 10/2881’i listeliyor.'),
     )),
    ('2882','hayvancilik','Mehmet Akalın','10/2882 şap hastalığı araştırmasının ön görüşme talebinin reddi',
     'İYİ Parti Grubu, Mehmet Akalın’ın şap hastalığı ve hayvan ithalatına ilişkin 10/2882 araştırma önergesinin ön görüşmesinin 2 Temmuz 2025 birleşiminde yapılmasını istedi. Genel Kurul bu gündem talebini reddetti.',
     'Hayvan hastalıkları ile etkin bir şekilde mücadele edilecek',
     'Hayvancılık, hayvan hastalıklarıyla mücadele',
     'İYİ Parti programı hayvan hastalıklarıyla etkin mücadeleyi hayvancılık başlığında öngörüyor.',
     'Mehmet Akalın, 2 Temmuz’da İYİ Parti Grubu adına 10/2882’nin ön görüşme talebini açıkladı. Bakanlığın hayvan hastalıklarıyla mücadele kapasitesi ve ithalat süreçlerini araştırmayı istedi.',
     'Programın hayvan hastalıklarıyla mücadele hedefi, Meclis araştırmasının denetim ve kapasite sorularıyla karşılaştırıldı. Hastalık kaynağı, araştırma ve fiilî önlem sonuçları açık.',(
        ('register-2882-id','initiative','TBMM esas numarası 10/2882.'),
        ('register-2882-day','initiative','Araştırma önergesinin Başkanlığa geliş tarihi 2 Temmuz 2025.'),
        ('signed-2882-id','initiative','İmzalı dosyanın ilk sayfasında 10/2882 kimliği var.'),
        ('signed-2882-scope','initiative','İmzalı gerekçe Bakanlığın mücadele kapasitesinin araştırılmasını istiyor.'),
        ('floor-signers-2882','action','İkinci gündem metni 2 Temmuz ön görüşme talebini ve farklı imzacı sayısını kaydediyor.'),
        ('floor-authority-2882','action','Başkan İYİ Parti Grubu adına Mehmet Akalın’a söz verdi.'),
        ('floor-research-2882','action','Akalın Bakanlık kapasitesi ve ithalat süreçlerinin araştırılmasını istedi.'),
        ('floor-vote-2882','result','Başkan ikinci gündem önerisinin reddini açıkladı.'),
        ('register-2882-pending','result','Esas sicili erişimde Gündemde görünüyor.'),
        ('papers-2882','result','9 Temmuz gelen kâğıtların 27. sırası 10/2882’yi listeliyor.'),
     )),
)
for label,topic,name,title,context,exact,section,goal,contribution_text,compare,evidence in events:
    stem=source+label
    quote_p=stem+'-program'
    new('passage',id=quote_p,version_id=program_version,exact=exact,prefix=None,suffix=None,article=None,section=section,
        pdf_page_index=None,printed_page=None)
    passages[quote_p]=entries[-1]['values']
    statement,target,quote=(stem+tail for tail in ('-statement','-target','-quote'))
    finding(target,goal,[quote_p],program_limit)
    finding(quote,exact,[quote_p],program_limit,pair=target)
    records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
        summary_finding_id=target,quote_finding_id=quote,statement_at=None,date_precision='unknown',version_id=program_version,
        period_basis='Program HTML’si 11 Kasım 2026 tarihinde erişildi.',uncertainty_reason=program_limit,
        comparison_row_id=f'04-03-v3-0306-iyi-program-{topic}-row'))
    readings(topic,'statement',[quote_p])
    for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',exact)):
        task(kind,statement,claim,program_limit)
    refs=[(source+pid,stage,'document',point) for pid,stage,point in evidence]
    key=f'tbmm-28-3-104-10-{label}-gundem'
    basis=f'TBMM 28. Dönem 3. Yasama Yılı 104. Birleşim tam tutanağı, imzalı 10/{label} önergesi ve TBMM esas kaydı.'
    eid=event(stem,key,'2025-07-02',title,context,basis,refs,common_limit)
    pids=[ref[0] for ref in refs]
    count_refs=[source+key for key in ('register-2882-signers','papers-signers','signed-2882-signers')] if label=='2882' else []
    scope=readings(topic,'event',pids+count_refs)
    authority=source+'floor-authority-'+label
    person,actor,contribution,fid=(stem+tail for tail in ('-person','-actor','-contribution','-finding'))
    new('person',id=person,name=name)
    new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,authorization_passage_id=authority)
    finding(fid,contribution_text,pids,common_limit)
    records['practice_contribution'].append(dict(id=contribution,event_id=eid,party_id=party,actor_id=actor,contribution_kind='task',
        finding_id=fid,authority_passage_id=authority,membership_passage_id=None,
        responsibility_limit='Temsil görevi 2 Temmuz 104. Birleşimdeki ilgili grup gündem önerisiyle sınırlı. Kişisel oy açık.'))
    records['practice_actor_period'].append(dict(contribution_id=contribution,valid_from='2025-07-02',valid_to='2025-07-02',identity_passage_id=authority))
    for kind in ('practice_contribution','practice_contribution.finding_id'):
        task(kind,contribution,contribution_text,common_limit)
    rid=stem+'-relation'
    explanation=stem+'-explanation'
    explanation_text=contribution_text+' '+compare
    finding(explanation,explanation_text,[quote_p,*pids],common_limit+' '+program_limit)
    records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,
        comparability_reason=compare,target_finding_id=target,result_finding_id=None,explanation_finding_id=explanation,
        temporal_context='2 Temmuz 2025 Meclis işlemi ve 11 Kasım 2026 erişimli program metni.',
        authority_context='Tutanakta başkan İYİ Parti adına sözcüye söz verdi. Genel Kurul ret sonucunu açıkladı.',
        uncertainty_reason=common_limit+' '+program_limit))
    records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',
        reason=compare,passage_ids=encoded(pids)))
    for kind,claim in (('practice_relation',explanation_text),('practice_relation.target_finding_id',goal),
                       ('practice_relation.explanation_finding_id',explanation_text)):
        task(kind,rid,claim,common_limit+' '+program_limit)
    if label=='2882':
        dispute=stem+'-count-dispute'
        dispute_finding=stem+'-count-finding'
        motion=source+'floor-signers-2882'
        detail=('2 Temmuz gündem önerisi metninde Akalın ve 19 milletvekili yazıyor. 10/2882 esas sicili ve 9 Temmuz '
                'Gelen Kâğıtlar Akalın ve 20 milletvekili kaydediyor. Son tarama sayfasında Akalın’ın kapak imzasına ek 20 satır var.')
        finding(dispute_finding,detail,[motion,*count_refs],common_limit)
        records['practice_dispute'].append(dict(id=dispute,event_id=eid,summary_finding_id=dispute_finding,
            supported_points='İmzalı dosya, esas sicili ve 9 Temmuz listesi 20 ek imzacıya işaret ediyor.',
            disputed_points='2 Temmuz gündem önerisinin metninde 19 ek imzacı yazıyor.',
            unresolved_points='Gündem metnindeki sayım farkının nedeni açık.'))
        task('practice_dispute',dispute,detail,common_limit)
        task('practice_dispute.summary_finding_id',dispute,detail,common_limit)
        for pid,role,point in (
            (motion,'conflict','2 Temmuz grup gündem metninde 19 milletvekili ifadesi.'),
            (count_refs[0],'support','Esas sicili Akalın ve 20 milletvekili gösteriyor.'),
            (count_refs[1],'support','9 Temmuz Gelen Kâğıtlar Akalın ve 20 milletvekili gösteriyor.'),
            (count_refs[2],'support','Son imza sayfasında Akalın’ın kapak imzasına ek 20 satır sayıldı.'),
        ):
            section=passages[pid]['section']
            records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,point=point,source_position=section,role=role))
            task('practice_dispute_evidence','|'.join((dispute,pid,point,role)),point,common_limit)

for entry in entries:
    destination=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in destination:
        destination.append(entry['values'])
for table,rows in records.items():
    destination=snapshot.setdefault(table,[])
    destination.extend(row for row in rows if row not in destination)
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
        reason=kind+' hedefinin kaynak, tarih ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('agenda-104-draft.json',package),('agenda-104-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
