from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from uygulamalar import practice_review_targets, validate_practice_source_review, validate_practices

here=Path(sys.argv[1])
data=Path('data')
def read(path):
    return json.loads(path.read_bytes())
def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)
aux=read(here/'inquiry-856-source-records.json')
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
        aid=f'inquiry-856-reading-{lane}-{topic}-{vid}'
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
assert party == 'saadet'
topic = 'sosyal-guvenlik'
stem = '0411-saadet-2024-10-856'
root = '0411-inquiry-'
file = root+'kaya-10856-'
signed = file+'signed-'
session = root+'pension-2024-session-'
summary = root+'pension-2024-summary-'
st = stem+'-statement'
target = stem+'-target'
limit = ('17 Ocak 2024 gündeme alma önerisi kabul edilmedi. Erişilen 10/856 dosya durumu Gündemde. '
         'Araştırma açılması veya araştırma sonucu için ayrı kayıt gerekiyor.')
date_limit = ('TBMM kayıt ve tutanağında geliş 16 Ocak 2024. PDF ilk sayfanın üst tarih alanı 16.01.2023 görünüyor. '
              'Metin 2024 başına değiniyor. İmza ve belge düzenleme gününün farkı açık.')
goal = '10/856, emekli aylıklarının yetersizliği ile aylık bağlama ve güncelleme farklarının araştırılmasını istiyor.'
finding(target,goal,[signed+'quote',session+'author',session+'scope'],'İmzalı gerekçenin görüntüsü ve grup önergesinin kapsamı okundu.')
finding(stem+'-quote',passages[signed+'quote']['exact'],[signed+'quote'],
    'İmzalı gerekçenin son satırındaki birebir pasaj.',pair=target)
records['practice_statement'].append(dict(id=st,party_id=party,topic_id=topic,taxonomy_version=4,
   summary_finding_id=target,quote_finding_id=stem+'-quote',statement_at=None,date_precision='unknown',
   version_id=passages[signed+'quote']['version_id'],
   period_basis='Aynı 10/856 numarası imzalı dosyada ve resmî geliş kaydında. 16 Ocak 2024’te TBMM kaydına girdiği tutanakta tekrarlandı.',
   uncertainty_reason=date_limit,comparison_row_id='04-03-v3-0311-saadet-sosyal-guvenlik'))
readings(topic,'statement',[signed+'quote',signed+'id',file+'submitted',session+'author',session+'scope'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[signed+'quote']['exact'])):
    task(kind,st,claim,date_limit)
evidence = [
    (file+'id','initiative','document','10/856 esas numarası TBMM dosyasında.'),
    (file+'submitted','initiative','document','TBMM araştırma önergesinin gelişini 16 Ocak 2024 olarak kaydetti.'),
    (file+'owner','initiative','document','TBMM dosyası önerge sahibi olarak Saadet Partisini gösteriyor.'),
    (signed+'id','initiative','document','İmzalı PDF ilk sayfası 10/856. Üst alandaki el yazılı yıl farkı ayrıca kaydedildi.'),
    (summary+'saadet','action','document','Birleşim özeti Saadet Partisi Grubunun 10/856’nın aynı gün görüşülmesi isteğini kaydetti.'),
    (session+'role','action','document','Mahmut Arıkan Saadet Partisi Grubu adına söz aldı.'),
    (session+'iyi-stance','action','document','İYİ Parti adına Ömer Karakaş asgari ücret eşiği ve kademeli artış önerisini dile getirdi.'),
    (session+'saadet-result','result','document','Başkan, Saadet Grubunun gündeme alma önerisinin kabul edilmediğini açıkladı.'),
    (summary+'result','result','document','Birleşim özeti gündeme alma önerilerinin kabul edilmediğini kaydetti.'),
]
eid = event(stem,'2024-01-17','10/856 emeklilik araştırmasının gündeme alınması önerisi',
    'Saadet Partisi Grubu 10/856’nın 17 Ocak’ta görüşülmesini istedi. Genel Kurul bu gündem önerisini kabul etmedi.',evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-2-050-10-856-gundem',
    occurrence_basis='TBMM 10/856 kayıt sayfası, 17 Ocak 2024 50. Birleşim tam tutanağı ve işlem özeti.')
refs = [row[0] for row in evidence]
scope = readings(topic,'event',refs+[file+'status',session+'iyi-role'])
rid = stem+'-relation'
result = stem+'-result'
expl = stem+'-explanation'
compare = 'Emeklilik sorunları araştırması ve 17 Ocak gündeme alma önerisi aynı 10/856’ya ilişkin.'
reported = 'Genel Kurul 17 Ocak 2024’te 10/856’nın o gün görüşülmesi önerisini kabul etmedi.'
explanation = 'Saadet Partisi Grubu emeklilik sorunlarının araştırılmasını ve 17 Ocak’ta görüşülmesini istedi. Gündeme alma önerisi kabul edilmedi. Erişilen 10/856 dosyası Gündemde.'
finding(result,reported,[session+'saadet-result',summary+'saadet',summary+'result'],
    'Saadet’e ait sonucun tutanaktaki oturum sırası ve özetle eşleşmesi kontrol edildi.')
finding(expl,explanation,[signed+'quote',session+'scope',file+'status',session+'saadet-result'],
    'Araştırma talebi, gündem sonucu ve erişimdeki dosya durumu kendi belgelerinden okundu.')
records['practice_relation'].append(dict(id=rid,statement_id=st,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=expl,temporal_context='16 Ocak 2024 TBMM geliş kaydı ve 17 Ocak gündem oylaması ayrı. İmzalı PDF üst yazısının yılı açık.',
    authority_context='Bülent Kaya grup başkanvekili olarak önergeyi verdi. Mahmut Arıkan Saadet Grubu adına gerekçeyi anlattı.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',explanation),('practice_relation.target_finding_id',goal),
                   ('practice_relation.result_finding_id',reported),('practice_relation.explanation_finding_id',explanation)):
    task(kind,rid,claim,limit)
person = '0411-saadet-2026-mekke-arikan-person'
actor = stem+'-arikan-group'
cid = stem+'-arikan-contribution'
auth = session+'role'
cf = stem+'-arikan-finding'
cbody = 'Mahmut Arıkan, Saadet Partisi Grubu adına 10/856’nın araştırma gerekçesini anlattı.'
climit = 'Tutanak grup adına sözü belgeliyor. Grup veya milletvekillerine ait isimli oy kaydı ayrı.'
new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,authorization_passage_id=auth)
finding(cf,cbody,[auth,session+'scope'],'Konuşmacı başlığı ve gerekçe aynı birleşim tutanağında.')
records['practice_contribution'].append(dict(id=cid,event_id=eid,party_id=party,actor_id=actor,
    contribution_kind='support',finding_id=cf,authority_passage_id=auth,membership_passage_id=None,responsibility_limit=climit))
records['practice_actor_period'].append(dict(contribution_id=cid,valid_from='2024-01-17',valid_to='2024-01-17',
    identity_passage_id=auth))
task('practice_contribution',cid,cbody,climit)
task('practice_contribution.finding_id',cid,cbody,climit)

dispute = stem+'-source-date'
df = dispute+'-finding'
finding(df,date_limit,[file+'submitted',summary+'saadet',signed+'id'],
    'Resmî tarih alanı ve birleşim özeti metinde, grup üst yazısının tarihi PDF ilk sayfada görüntüden okundu.')
records['practice_dispute'].append(dict(id=dispute,event_id=eid,summary_finding_id=df,
    supported_points='10/856’nın TBMM’ye geliş günü 16 Ocak 2024, gündem oylaması 17 Ocak 2024.',
    disputed_points='İmzalı PDF’nin üst yazı alanı el yazısıyla 16.01.2023 görünüyor.',
    unresolved_points='Belge düzenleme gününün ve yazılı yıl farkının nedeni açık.'))
task('practice_dispute',dispute,date_limit,'Gündeme alma oylamasının tarihi tutanaktan ayrıca doğrulandı.')
task('practice_dispute.summary_finding_id',dispute,date_limit,'PDF ilk sayfanın metin katmanı yalnız 10/856 kimliğini içeriyor.')
for passage,role,point,position in (
    (file+'submitted','support','TBMM 16 Ocak 2024 gelişini gösteriyor.','TBMM teklif dosyasının tarih alanı.'),
    (summary+'saadet','support','Birleşim özeti aynı 16 Ocak 2024 gelişini bildiriyor.','17 Ocak özetindeki Saadet önergesi bölümü.'),
    (signed+'id','conflict','PDF üst yazısının el yazılı tarih alanı 16.01.2023 görünüyor.','10/856 kimliğinin bulunduğu ilk sayfa görüntüsü.'),
):
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=passage,point=point,source_position=position,role=role))
    task('practice_dispute_evidence','|'.join((dispute,passage,point,role)),point,position)
for entry in entries:
    dest=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in dest: dest.append(entry['values'])
for table,rows in records.items():
    dest=snapshot.setdefault(table,[])
    dest.extend(row for row in rows if row not in dest)
validate_practices(snapshot)
targets=practice_review_targets(snapshot,records)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limitation,result='reviewed',
        reason=kind+' hedefinin asıl kaynakları, tarihi ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,selection=records,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('inquiry-856-draft.json',package),('inquiry-856-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
