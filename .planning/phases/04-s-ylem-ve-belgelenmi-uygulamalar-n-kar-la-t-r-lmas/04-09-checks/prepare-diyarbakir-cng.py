"""Prepare an unmatched DBP practice and its documented local party contribution."""

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
aux=read(here/'diyarbakir-cng-source-records.json')
party=aux['party_id']
package=read(here/'baglar-cemr-draft.json')
review=read(here/'baglar-cemr-review-draft.json')
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
            boundary_reason='Diyarbakır belediye ulaşımı ve DBP’nin belgelenen katkısı dar kapsamda incelendi.'))
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
        aid=f'cng-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='2015 tanıtımı ve belediye ulaşımının ilgili kaynak bağlamı.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='27 Mayıs 2015 tarihli Temsilci haberi ve ayrı belediye ulaşımı kaynakları.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'dbp'
topic = 'ulasim-iletisim'
stem = '0409-diyarbakir-2015-cng'
source = '0409-diyarbakir-cng-'
day = '2015-05-27'
limit = ('Haber 27 Mayıs’taki tanıtımı ve şehir turunu aktarıyor. Haberin gövdesi düzenli seferi ertesi güne bırakıyor. '
         'İlk düzenli sefer tarihi, tüm araçların teslimi ve ölçülmüş çevre etkisi araştırmaya açık. '
         'Satın alma ve işletme belediyeye ait. Parti katkısı tanıtımda dile getirilen destekle sınırlı.')
context = ('Diyarbakır Büyükşehir Belediyesi 27 Mayıs 2015’te doğalgazlı otobüslerin ilk 22’sini tanıttı. '
           'Partinin il eş başkanı törende belediyeye teşekkür etti.')
authority = source+'may27-simsek-role'
support = source+'may27-simsek-words'
evidence = [
    (source+'may27-launch','action','independent_report','Habere göre satın alınan 48 otobüsten ilk 22’si tanıtıldı.'),
    (source+'may27-tour','action','independent_report','Tanıtım kapsamında otobüslerle şehir turu yapıldı.'),
    (source+'may27-later','action','independent_report','Haberin gövdesi düzenli yolcu seferini ertesi gün için duyuruyor.'),
    (authority,'action','independent_report','Haber Ali Şimşek’i DBP İl Eş Başkanı olarak tanıtıyor.'),
    (support,'action','independent_report','Şimşek belediyeye teşekkür etti.'),
]
eid = event(stem,day,'Diyarbakır’da ilk 22 doğalgazlı otobüsün tanıtımı',context,evidence,limit)
refs = [row[0] for row in evidence]
additional = [source+key for key in ('may06-role','may06-goal','may06-plan','may06-agency',
    'dbp-report-author','dbp-report-claimed-route','city-report-cover','city-report-annual','city-report-station')]
scope = readings(topic,'event',refs+additional)
reason = ('6 Mayıs hedefini Gültan Kışanak belediye başkanı sıfatıyla açıkladı. '
          'Tanıtım öncesindeki DBP parti söylemi için araştırma açık.')
candidate = stem+'-unmatched'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,relation_id=None,
    state='unmatched',reason=reason,passage_ids=encoded(refs)))
task('practice_candidate',candidate,reason,limit)
person,actor,cid,fid = (stem+suffix for suffix in ('-person','-actor','-contribution','-finding'))
new('person',id=person,name='Ali Şimşek')
new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,authorization_passage_id=authority)
claim = ('27 Mayıs tarihli habere göre DBP Diyarbakır İl Eş Başkanı Ali Şimşek, '
         'doğalgazlı otobüslerin tanıtımında belediyenin çalışmasını destekledi ve belediyeye teşekkür etti.')
contribution_limit = 'Belgelendirilen katkı törendeki sözlerle sınırlı. Alım ve düzenli hizmet belediyenin yetkisinde.'
finding(fid,claim,[authority,support],contribution_limit)
records['practice_contribution'].append(dict(id=cid,event_id=eid,party_id=party,actor_id=actor,
    contribution_kind='support',finding_id=fid,authority_passage_id=authority,membership_passage_id=None,
    responsibility_limit=contribution_limit))
records['practice_actor_period'].append(dict(contribution_id=cid,valid_from=day,valid_to=day,identity_passage_id=authority))
for kind in ('practice_contribution','practice_contribution.finding_id'):
    task(kind,cid,claim,contribution_limit)

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
for name,content in [('diyarbakir-cng-draft.json',package),('diyarbakir-cng-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
