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
aux=read(here/'khk-102925-source-records.json')
party=aux['party_id']
package=read(data/'practices/04-saadet.json')
review=read(data/'practices/04-saadet-review.json')
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
            boundary_reason='Partiler arası temas duyurusu ve iki görüşmenin tarihli açıklamaları okundu.'))
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
        aid=f'khk-102925-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Ocak 2026 partiler arası temas duyurusu veya tarihli görüşme kaydı.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='Birden fazla yayımlanmış açıklamada toplantı ve tarih doğrulandı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='saadet'
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='c16516e8092ab9a7f7aa93e21036d9e3edd8a6389295b459e83096c8844cb2a0'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='59b049428337950c2fe746e53156363ed459b31714a318d25fbbb93073ce9352'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(28,24,0)
topic='yargi-bagimsizligi'; stem='0411-saadet-khk-102925'; src='0411-khk-102925-'
statement,target,quote=(stem+s for s in ('-statement','-target','-quote'))
goal='Mahmut Arıkan 12 Mart 2025 konuşmasında KHK ile ihraçlardan beraat edenler ve takipsizlik alanların görevlerine iadesini istedi.'
limit='İdris Şahin ilk imza sahibi; 22 imzacı arasında Mesut Doğan ve Bülent Kaya da vardır. Doğan 21 Mart tarihli kendi TBMM belgesinde Saadet milletvekili sıfatını kullanmıştır. Önerge Yeni Yol grubundan ortak bireysel imzalarla sunuldu; Meclis araştırması isteği iade kararı veya yasal düzenleme değildir. Önerge ayrıca soruşturma açılmayanları da kapsar.'
sp=[src+'speech-demand']; finding(target,goal,sp,'Parti açıklamasındaki söz haberin özgün gövdesiyle karşılaştırıldı.')
finding(quote,passages[sp[0]]['exact'],sp,'Doğrudan konuşma aktarımı.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2025-03-12',date_precision='day',version_id=passages[sp[0]]['version_id'],period_basis='Saadet API zaman etiketi ve 12 Mart tarihli haber.',uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-yargi-bagimsizligi'))
readings(topic,'statement',sp)
for kind,claim in [('practice_statement',goal),('practice_statement.summary_finding_id',goal),('practice_statement.quote_finding_id',passages[sp[0]]['exact'])]: task(kind,statement,claim,limit)
ep=[(src+'motion-subject','initiative','document','İmzalı gerekçe, KHK ihracı sonrası beraat veya takipsizlik verilenlerin göreve iade edilmemesini ele alıyor.'),(src+'motion-signatures','action','document','22 isimli imza çizelgesinde Mesut Doğan yer alıyor.'),(src+'motion-kaya','action','document','Aynı imza çizelgesinde Bülent Kaya yer alıyor.'),(src+'registry-number','result','document','TBMM araştırma önergesini 10/2925 numarasıyla kaydetti.'),(src+'registry-status','result','document','Erişim sırasında sicilde dosya gündemde görünüyor.')]
eid=event(stem,'2025-07-09','10/2925 KHK mağduriyetleri araştırma önergesi','İdris Şahin ve 21 milletvekili 9 Temmuz 2025 tarihinde KHK sonrası iadeye ilişkin araştırma açılmasını istedi.',ep,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-3-10-2925-khk-research',occurrence_basis='TBMM imzalı özgün önerge ve sicil.')
eids=[r[0] for r in ep]; scope=readings(topic,'event',eids); rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
observed='9 Temmuz 2025 tarihli 10/2925 önergesinde 22 milletvekili, KHK ihracı ve beraat veya takipsizlik sonrası görevine iade edilmeyenler dahil mağduriyetlerin araştırılmasını istedi. TBMM sicilinde erişimde gündemde.'
compare='Arıkanın iade talebi ile sonraki araştırma önergesi aynı iki hukuki grubu ele alır; araştırma istemi fiilen göreve iade değildir.'
finding(result,observed,eids,'İmzalı önerge ve sicilin gösterdiği işlem.')
finding(explanation,compare+' '+limit,sp+eids+[src+'role-mesut'],limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='12 Mart konuşması 9 Temmuz önergesinden öncedir; nedensellik iddia edilmez.',authority_context='Arıkan Saadet Genel Başkanıdır. İdris Şahin ilk imzacı, Doğan ve Kaya diğer imzacılardır; önerge 22 milletvekilinin ortak işlemidir.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(eids)))
for kind,claim in [('practice_relation',compare),('practice_relation.target_finding_id',goal),('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare)]: task(kind,rid,claim,limit)
for entry in entries:
 destination=snapshot.setdefault(entry['kind'],[])
 if entry['values'] not in destination: destination.append(entry['values'])
for table,rows in records.items():
 destination=snapshot.setdefault(table,[]); destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot,records,[entry['values']['id'] for entry in entries if entry['kind']=='passage'],party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
 pids,owners=targets[(kind,identity)]; assert party in owners
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),supported_claim=claim,limitations=limitation,result='reviewed',reason=kind+' için kaynak ve sınırlar incelendi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]; package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('khk-102925-draft.json',package),('khk-102925-review-draft.json',review)]:
 path=here/name
 with path.open('x') as output: output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
 print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
