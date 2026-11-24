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
aux=read(here/'siber-7545-source-records.json')
party=aux['party_id']
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
            boundary_reason='TBMM’nin geçici madde önergesi, kesin oy cetveli ve kanun kaydı okundu.'))
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
        aid=f'siber-7545-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='12 Mart 2025 tarihli 2/2860 Genel Kurul işlemi veya bağlantılı yasama sicili.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='TBMM 65. Birleşim basılı tutanağı ve oylama kaydı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='demokrat'
assert sha256((data/'practices/04-demokrat.json').read_bytes()).hexdigest()=='eef53c468b7991faea8f26084307192ab849a59a034d6e8a2cc0a033a6842937'
assert sha256((data/'practices/04-demokrat-review.json').read_bytes()).hexdigest()=='9ff446ff497391537367ab3f9868fd0fb66be896cd4ec88c89ef5ac0e903d0a5'
topic='siber-guvenlik'
stem='0412-siber-7545'
printed=stem+'-printed-'
registry=stem+'-act-'
identity=printed+'speech'
membership=stem+'-party-report-membership'
actor='0412-framework-7595-actor'
day='2025-03-12'
assert any(e['kind']=='actor' and e['values']['id']==actor for e in entries)
open_policy='Olaydan önce doğrudan aynı düzenlemeye bağlanan Demokrat Parti söylemi araştırılıyor.'

events=(
    ('motion','tbmm-28-3-065-2-2860-gecici-1-cikarma',
     '2/2860 geçici 1. madde çıkarma önergelerinin reddi',
     '12 Mart 2025’te 2/2860 Siber Güvenlik Kanunu Teklifinin geçici 1. maddesini çıkarmaya yönelik iki aynı mahiyette önerge Genel Kurulda birlikte oylanıp reddedildi.',
     'Basılı tutanak 113–115. sayfalarda önerge, iki imza listesi, konuşmalar ve başkanın sonuç açıklaması.',
     'Haydar Altıntaş ilk önergenin yedi imzacısından biri ve aynı mahiyetteki iki önerge üzerine söz alan ilk konuşmacı.',
     'Başkan iki önergenin reddini bildirdi. Önerge oylamasına ilişkin isimli cetvel açık.',
     (
         (printed+'motion','initiative','İlk önerge geçici 1. maddenin tekliften çıkarılmasını istiyor.'),
         (printed+'signer','initiative','Altıntaş İzmir milletvekili olarak ilk önergenin imza tablosunda.'),
         (printed+'speech','action','Başkan altıncı oturumda iki önerge üzerine ilk sözü Altıntaş’a verdi.'),
         (printed+'motion-vote','result','Başkan iki aynı mahiyetteki önergenin reddini açıkladı.'),
     )),
    ('final','tbmm-28-3-065-2-2860-siber-guvenlik-kanunu',
     '2/2860 Siber Güvenlik Kanunu Teklifinin tümünün kabulü',
     '2/2860 teklifinin tümü 12 Mart 2025’te açık oylamayla kabul edildi. 7545 sayılı kanun 19 Mart 2025’te 32846 sayılı Resmî Gazete’de yayımlandı.',
     '65. Birleşim basılı tutanağı, kesin açık oy cetveli ve TBMM kanun sicili.',
     'Teklifin tümü için kesin cetvelde İzmir milletvekili Haydar Altıntaş’ın DP ve Katılmadı kaydı yer alıyor.',
     'Başkanın ilk ilanı ve kesin cetvel ayrı. Bu kayıt, teklifin tümündeki kişisel katılım durumunu gösteriyor.',
     (
         (printed+'announced','action','Başkan 348 oy içinde 246 kabul ve 102 ret açıkladı.'),
         (printed+'footnote','action','6. dipnot kesin cetvelin tutanağa eklendiğini belirtiyor.'),
         (printed+'final-count','result','Kesin cetvel 245 kabul ve 101 ret gösteriyor.'),
         (printed+'duplicate-count','result','Kesin cetvel iki mükerrerle toplam 348 kaydı gösteriyor.'),
         (printed+'named-vote','result','Kesin cetvelde Altıntaş’ın kişisel kaydı Katılmadı.'),
         (printed+'passed','result','Genel Kurul teklifin tümünü kabul etti.'),
         (registry+'number','result','Kanun sicil numarası 7545.'),
         (registry+'acceptance-day','result','TBMM sicili kabul gününü 12 Mart olarak veriyor.'),
         (registry+'gazette-day','result','TBMM sicili yayım gününü 19 Mart olarak veriyor.'),
         (registry+'gazette-number','result','TBMM sicilinde Resmî Gazete sayısı 32846.'),
     )),
)
for label,key,title,context,basis,contribution,detail,anchors in events:
    event_stem=f'{stem}-{label}'
    limit=detail+' '+open_policy
    evidence=[(pid,stage,'document',claim) for pid,stage,claim in anchors]
    event_id=event(event_stem,day,title,context,evidence,limit)
    records['practice_event'][-1].update(common_event_key=key,occurrence_basis=basis)
    pids=[row[0] for row in evidence]
    scope=readings(topic,'event',pids+[identity,membership])
    candidate = event_stem+'-candidate'
    records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=event_id,
        relation_id=None,state='unmatched',reason=open_policy,passage_ids=encoded(pids)))
    task('practice_candidate',candidate,context,limit)
    contribution_id=event_stem+'-contribution'
    contribution_finding=event_stem+'-contribution-finding'
    finding(contribution_finding,contribution,pids+[membership,identity],detail)
    records['practice_contribution'].append(dict(id=contribution_id,event_id=event_id,party_id=party,actor_id=actor,
        contribution_kind='task' if label=='motion' else 'unknown',finding_id=contribution_finding,
        authority_passage_id=None,membership_passage_id=membership,responsibility_limit=detail))
    records['practice_actor_period'].append(dict(contribution_id=contribution_id,valid_from=day,valid_to=day,
        identity_passage_id=identity))
    task('practice_contribution',contribution_id,contribution,detail)
    task('practice_contribution.finding_id',contribution_id,contribution,detail)

dispute=stem+'-vote-count-dispute'
dispute_finding=dispute+'-finding'
dispute_text='Tutanakta 246 kabul ve 102 ret ilan edildi. Kesin cetvel 245 kabul, 101 ret ve iki mükerrer oy gösteriyor.'
dispute_limit='İlk ilan ve kesin cetvel teklifin kabulünde uyuşuyor. İki sayım arasındaki aritmetik fark bir kabul ve bir ret mükerrer işaretine karşılık geliyor. Ayrı düzeltme işleminin belgesi açık.'
dispute_pids=(printed+'announced',printed+'final-count',printed+'duplicate-count',printed+'footnote')
finding(dispute_finding,dispute_text+' '+dispute_limit,dispute_pids,dispute_limit)
records['practice_dispute'].append(dict(id=dispute,event_id=stem+'-final-event',summary_finding_id=dispute_finding,
    supported_points='Her iki kayıt da teklifin kabul edildiğini belirtiyor.',
    disputed_points=dispute_text,unresolved_points=dispute_limit))
task('practice_dispute',dispute,dispute_text,dispute_limit)
task('practice_dispute.summary_finding_id',dispute,dispute_text,dispute_limit)
for pid,point,role in (
    (printed+'announced','Başkan 246 kabul ve 102 ret açıkladı.','conflict'),
    (printed+'final-count','Kesin cetvelde 245 kabul ve 101 ret yer alıyor.','support'),
    (printed+'duplicate-count','Kesin cetvel iki mükerrer dahil toplam 348 gösteriyor.','support'),
    (printed+'footnote','Dipnot tutanağa ekli kesin cetveli belirtiyor.','support'),
):
    position=passages[pid]['section']
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,point=point,
        source_position=position,role=role))
    task('practice_dispute_evidence','|'.join((dispute,pid,point,role)),point,position)

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
for name,content in [('siber-7545-draft.json',package),('siber-7545-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
