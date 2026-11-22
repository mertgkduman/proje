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
aux=read(here/'inquiry-3998-source-records.json')
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
        aid=f'tuik-3998-reading-{lane}-{topic}-{vid}'
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
assert party == 'yeni-yol'
stem = '0408-yeni-yol-2026-10-3998'
topic = 'makroekonomik-politika'
base = '0408-stats-yy-3998'
file, signed, earlier, session, abridged = [base+tail for tail in ('-','-signed-','-february-','-session-','-summary-')]
st = stem+'-statement'
target = stem+'-target'
quote = stem+'-quote'
goal = 'Selçuk Özdağ, 3 Şubat 2026’da Yeni Yol Grubu adına TÜİK enflasyon sepetinin açıklanmamasını Meclisin araştırmasını istedi.'
limit = ('8 Nisan 2026’da oylanan işlem 10/3998’in ön görüşmesini aynı güne alma önerisi. '
         'Erişilen esas dosyası Gündemde. Elektronik sayımın rakamları ve milletvekillerinin isimli oy kayıtları ile TÜİK’in fiilî veri yayımlama sonucu açık.')
finding(target,goal,[earlier+'role',earlier+'quote'],
        '3 Şubat konuşmasında temsil ve TÜİK’e ilişkin araştırma çağrısı birlikte okundu.')
finding(quote,passages[earlier+'quote']['exact'],[earlier+'quote'],
        '3 Şubat beyanının kısa birebir pasajı.',pair=target)
records['practice_statement'].append(dict(id=st,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-02-03',date_precision='day',
    version_id=passages[earlier+'quote']['version_id'],period_basis='3 Şubat 55. Birleşimde Yeni Yol Grubu adına söz.',
    uncertainty_reason=None,comparison_row_id='04-03-v3-0307-yeni-yol-makroekonomik-politika-program'))
readings(topic,'statement',[earlier+'role',earlier+'quote'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[earlier+'quote']['exact'])):
    task(kind,st,claim,'Grup adına konuşmanın TÜİK bölümü, daha sonra tartıştığı 3 Şubat personel önergesinden ayrı.')

evidence = [
    (file+'id','initiative','document','10/3998 esas numarası.'),
    (file+'filed','initiative','document','TBMM Başkanlığına 8 Nisan 2026’da geldi.'),
    (signed+'id','initiative','document','İmzalı taramada 10/3998 dosya kimliği.'),
    (signed+'terms','initiative','document','Gerekçe, enflasyon sepetinin açıklanması ve hukuki dayanakların araştırılması isteklerini içeriyor.'),
    (session+'motion','action','document','Grup, ön görüşmenin 8 Nisan birleşiminde yapılmasını istedi.'),
    (session+'decision','result','document','Başkan elektronik oylamadan sonra aynı gün görüşme önerisinin kabul edilmediğini ilan etti.'),
    (abridged+'result','result','document','TBMM birleşim özeti 8 Nisan görüşmesine alma önerilerinin kabul edilmediğini kaydediyor.'),
]
context = 'Yeni Yol Grubu 10/3998 TÜİK araştırma önergesinin ön görüşmesini aynı güne almak istedi. Genel Kurul kabul etmedi.'
eid = event(stem,'2026-04-08','10/3998 TÜİK araştırma önergesinin gündeme alınması',context,evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-4-079-10-3998-gundem',
    occurrence_basis='10/3998 TBMM dosyası, imza taraması ve 79. Birleşim tutanağı.')
refs = [r[0] for r in evidence]
scope = readings(topic,'event',refs+[file+'status',signed+'commission',signed+'signer',session+'role',session+'support',
    session+'debate',session+'dalgin-role',session+'dalgin-call',session+'kamaç-role',abridged+'motion'])
rid, result, explanation = (stem+'-relation',stem+'-result',stem+'-explanation')
compare = '3 Şubat grup çağrısı ve 10/3998 enflasyon sepetinin şeffaflığının Meclisçe araştırılmasına ilişkin.'
outcome = ('8 Nisan’da aynı gün görüşme önerisi işaretle oylamaya itirazın ardından elektronik oylamaya sunuldu '
           've kabul edilmedi. TBMM dosyasında 10/3998 için Gündemde yazıyor.')
connection = ('3 Şubat’ta Selçuk Özdağ Yeni Yol Grubu adına TÜİK enflasyon sepetinin araştırılmasını istedi. '
              '8 Nisan’da Özdağ ve 19 milletvekili 10/3998’i sundu. Grup, ön görüşmeyi aynı güne almayı önerdi.')
finding(result,outcome,[session+'decision',session+'debate',abridged+'result',file+'status'],
        'Elektronik oylama, resmî özet ve esas dosyanın durumu birlikte kontrol edildi.')
finding(explanation,connection,[earlier+'role',earlier+'quote',file+'filed',signed+'terms',session+'motion',abridged+'motion'],
        'İki ayrı birleşim ve TBMM dosyasında araştırma konuları ve tarihler kontrol edildi.')
records['practice_relation'].append(dict(id=rid,statement_id=st,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,
    comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,
    temporal_context='3 Şubat öncül çağrı, 8 Nisan teklif dosyasının gelişi ve ön görüşmeyi öne alma oylaması.',
    authority_context='Özdağ iki birleşimde de Yeni Yol Grubu adına konuştu. Sonuç Genel Kurul Başkanı tarafından ilan edildi.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',connection),('practice_relation.target_finding_id',goal),
                   ('practice_relation.result_finding_id',outcome),('practice_relation.explanation_finding_id',connection)):
    task(kind,rid,claim,limit)

dispute=stem+'-vote-dispute'
dispute_finding=dispute+'-finding'
detail = ('İşaretle oylama sırasında Gülüstan Kılıç Koçyiğit önerinin kabul edilmiş göründüğünü söyledi. '
          'Başkan ihtilaf olduğunu bildirdi ve elektronik oylama sonrasında önerinin kabul edilmediğini ilan etti.')
finding(dispute_finding,detail,[session+'debate',session+'decision',abridged+'result'],
        'Üyenin işaretle oya itirazı ve başkanın elektronik oylama sonrası ilanı ayrı okundu.')
records['practice_dispute'].append(dict(id=dispute,event_id=eid,summary_finding_id=dispute_finding,
    supported_points='Başkan elektronik oylama sonrası aynı gün gündeme alma önerisinin reddini ilan etti.',
    disputed_points='İşaretle oylama sırasında bazı üyeler kabul çoğunluğu bulunduğunu savundu.',
    unresolved_points='İşaretle oylamada ve elektronik oylamada kişi sayısı veya isimli cetvel bu kaynaklarda açık değil.'))
task('practice_dispute',dispute,detail,limit)
task('practice_dispute.summary_finding_id',dispute,detail,limit)
for pid,role,point in (
    (session+'debate','conflict','İşaretle oylamada kabul çoğunluğu olduğuna ilişkin üye itirazı.'),
    (session+'decision','support','Başkan elektronik oylama sonrası kabul edilmediğini açıkladı.'),
    (abridged+'result','support','Birleşim özeti aynı gün gündem önerilerinin kabul edilmediğini kaydediyor.'),
):
    pos=passages[pid]['section']
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,point=point,source_position=pos,role=role))
    task('practice_dispute_evidence','|'.join((dispute,pid,point,role)),point,pos)
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
for name,content in [('inquiry-3998-draft.json',package),('inquiry-3998-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
