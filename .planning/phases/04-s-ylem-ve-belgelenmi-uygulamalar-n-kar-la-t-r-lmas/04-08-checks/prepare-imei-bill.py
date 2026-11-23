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
aux=read(here/'imei-bill-source-records.json')
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
        occurrence_basis='TBMM imzalı teklif, alındı damgası, Gelen Kâğıtlar ve işlem dosyası.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'yeni-yol'
stem = '0408-yeni-yol-2026-3940'
topic = 'maliye-vergi'
signed, file, papers, speech = ['0408-imei-'+key+'-' for key in ('signed','detail','papers','speech')]
date_limit = ('İşlem portalı Başkanlığa geliş için 7 Ekim diyor. İmzalı yazı, alındı damgası ve '
              'Gelen Kâğıtlar 8 Ekim’i gösteriyor. Komisyona sevk tarihi 9 Ekim. Geliş tarihi farkının kaynağı açık.')
limit = ('Teklif kullanımdan önce alınan harcı kaldırmayı öngörüyor. Cihaz kayıt ve denetim sistemi '
         'hükümleri teklif kapsamı dışında. Esas komisyonun kabul veya ret kararı ve yürürlüğe giriş açık.')
context = ('2/3940 esas numaralı teklif 9 Ekim 2026’da Plan ve Bütçe Komisyonuna sevk edildi. '
           'İmzalı teklif yolcu beraberinde getirilen telefonun kullanım izin harcının kaldırılmasını öneriyor.')
evidence = [
    (signed+'identity','initiative','document','Selçuk Özdağ imzalı üst yazıda Grup Başkanvekili olarak yer alıyor.'),
    (signed+'signed-day','initiative','document','İmzalı üst yazı 8 Ekim 2026 tarihli.'),
    (signed+'stamp','initiative','document','TBMM alındı damgası 8 Ekim 2026 tarihli.'),
    (file+'date','initiative','document','TBMM işlem portalındaki Başkanlığa geliş alanı 7 Ekim 2026.'),
    (papers+'receipt','action','document','Gelen Kâğıtlar 2/3940’ı 8 Ekim geliş tarihiyle Plan ve Bütçe Komisyonu altında kaydediyor.'),
    (file+'sent','action','document','TBMM işlem dosyası komisyon girişini 9 Ekim olarak kaydediyor.'),
    (signed+'scope','initiative','document','Genel gerekçe cihaz kaydı ile harç yükünün kaldırılmasını birbirinden ayırıyor.'),
    (signed+'article','initiative','document','1. maddeye göre teklif telefon kullanım izin harcını kaldırıyor.'),
]
eid = event(stem,'2026-10-09','2/3940 telefon kullanım izin harcı teklifinin komisyona sevki',context,evidence,limit+' '+date_limit)
refs = [row[0] for row in evidence]
scope = readings(topic,'event',refs+[signed+'sent',signed+'amount',signed+'entry',file+'id',file+'status'])
readings(topic,'statement',[speech+'date',speech+'claim',speech+'criticism'])
candidate_reason = ('21 Ekim Genel Kurul açıklaması 9 Ekim sevkinden sonra yapıldı. Nisan ayındaki yurt dışı telefon '
                    'konuşması başka bir milletvekiline ait. Aynı kapsamda daha önceki Yeni Yol söyleminin araştırması açık.')
candidate = stem+'-unmatched'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,relation_id=None,
    state='unmatched',reason=candidate_reason,passage_ids=encoded(refs)))
task('practice_candidate',candidate,candidate_reason,limit)

person, actor = (stem+suffix for suffix in ('-person','-actor'))
authority = signed+'identity'
new('person',id=person,name='Selçuk Özdağ')
new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,authorization_passage_id=authority)
contribution = stem+'-contribution'
fid = stem+'-finding'
claim = ('Selçuk Özdağ, Yeni Yol Grup Başkanvekili olarak imzaladığı 2/3940 ile yolcu beraberinde getirilen '
         'telefon kullanım izin harcının kaldırılmasını teklif etti.')
finding(fid,claim,[authority,signed+'scope',signed+'article',papers+'receipt'],limit)
records['practice_contribution'].append(dict(id=contribution,event_id=eid,party_id=party,actor_id=actor,
    contribution_kind='support',finding_id=fid,authority_passage_id=authority,membership_passage_id=None,
    responsibility_limit='Özdağ tek imzacı. Bu belge grup oylamasına veya teklifin kabulüne ilişkin kayıt içermiyor.'))
records['practice_actor_period'].append(dict(contribution_id=contribution,valid_from='2026-10-08',
    valid_to='2026-10-09',identity_passage_id=authority))
task('practice_contribution',contribution,claim,limit)
task('practice_contribution.finding_id',contribution,claim,limit)

dispute = stem+'-filing-dispute'
dispute_finding = dispute+'-finding'
date_refs = [file+'date',signed+'signed-day',signed+'stamp',papers+'receipt',file+'sent']
finding(dispute_finding,date_limit,date_refs,'İki tarih ve ortak komisyon tarihi özgün nüshalarda ayrı okundu.')
records['practice_dispute'].append(dict(id=dispute,event_id=eid,summary_finding_id=dispute_finding,
    supported_points='Dosya esas numarası 2/3940 ve komisyona sevk 9 Ekim 2026.',
    disputed_points='Başkanlığa geliş portalda 7 Ekim, Gelen Kâğıtlar ve alındı damgasında 8 Ekim 2026.',
    unresolved_points='Portal tarih farkının idari açıklaması açık.'))
task('practice_dispute',dispute,date_limit,limit)
task('practice_dispute.summary_finding_id',dispute,date_limit,limit)
for pid,point,role in [
    (file+'date','İşlem portalı Başkanlığa geliş için 7 Ekim 2026 gösteriyor.','conflict'),
    (signed+'stamp','TBMM alındı damgası 8 Ekim 2026 gösteriyor.','support'),
    (papers+'receipt','Gelen Kâğıtlar Başkanlığa geliş için 8 Ekim 2026 gösteriyor.','support'),
]:
    section = passages[pid]['section']
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,
        point=point,source_position=section,role=role))
    task('practice_dispute_evidence','|'.join((dispute,pid,point,role)),point,section)

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
for name,content in [('imei-bill-draft.json',package),('imei-bill-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
