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
aux=read(here/'tuik-3998-group-source-records.json')
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
        aid=f'tuik-3998-group-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='TBMM esas dosyası, 79. Birleşim tam tutanağı ve işlem özeti.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'iyi'
stem = '0407-iyi-2026-10-3998'
topic = 'makroekonomik-politika'
base = '0407-tuik-3998'
file, session, summary = (base + suffix for suffix in ('-', '-session-', '-summary-'))
authority = session + 'dalgin-role'
limit = ('Dalgın’ın grup adına konuşması tutanakta. 10/3998 Yeni Yol milletvekillerinin araştırma önergesi. '
         'Oylanan işlem aynı gün görüşmeydi. İsimli oylar, araştırmanın açılması ve TÜİK’in uygulama sonucu açık.')
evidence = [
    (file+'id','initiative','document','TBMM dosyasının esas numarası 10/3998.'),
    (session+'motion','action','document','Ön görüşmenin 8 Nisan birleşiminde yapılması istendi.'),
    (authority,'action','document','Burak Dalgın İYİ Parti Grubu adına söz aldı.'),
    (session+'dalgin-call','action','document','Dalgın TÜİK’ten fiyat ve ürün sepetinin açıklanmasını istedi.'),
    (session+'audit','action','document','Dalgın akademik bir kurulla şeffaf denetim istedi.'),
    (session+'commission','action','document','Dalgın TÜİK Başkanının Plan ve Bütçe Komisyonunda dinlenmesini istedi.'),
    (session+'decision','result','document','Başkan elektronik oylamadan sonra aynı gün görüşme önerisinin kabul edilmediğini ilan etti.'),
    (summary+'result','result','document','TBMM birleşim özeti aynı gün gündeme alma girişiminin kabul edilmediğini kaydediyor.'),
]
context = ('Yeni Yol’un 10/3998 TÜİK araştırma önergesinin gündem görüşmesinde Burak Dalgın İYİ Parti Grubu adına '
           'fiyat ve ürün sepetinin açıklanmasını, akademik denetimi ve TÜİK Başkanının komisyonda dinlenmesini istedi. '
           'Genel Kurul aynı gün görüşme önerisini kabul etmedi.')
eid = event(stem,'2026-04-08','10/3998 görüşmesinde İYİ Parti Grubunun TÜİK çağrısı',context,evidence,limit)
records['practice_event'][-1]['common_event_key'] = 'tbmm-28-4-079-10-3998-gundem'
refs = [item[0] for item in evidence]
scope = readings(topic,'event',refs+[file+'filed',file+'status',summary+'motion'])
person = stem+'-dalgin-person'
actor = stem+'-dalgin-group'
contribution = stem+'-dalgin-contribution'
contribution_finding = stem+'-dalgin-finding'
contribution_text = ('Burak Dalgın İYİ Parti Grubu adına TÜİK’ten fiyat ve ürün sepetini açıklamasını '
                     've akademik bir kurul önünde denetim istedi.')
contribution_limit = ('Konuşma 10/3998’in gündem tartışmasında kayda geçti. '
                      'Aynı gün görüşme önerisine ve isimli oya ilişkin Dalgın’ın tutumu açık.')
new('person',id=person,name='BURAK DALGIN')
new('actor',id=actor,kind='authorized_representative',party_id=party,person_id=person,
    authorization_passage_id=authority)
finding(contribution_finding,contribution_text,[authority,session+'dalgin-call',session+'audit'],
    'Konuşmacı başlığı ve fiyat sepeti ile denetim çağrısı özgün tutanakta aynı konuşmada okundu.')
records['practice_contribution'].append(dict(id=contribution,event_id=eid,party_id=party,actor_id=actor,
    contribution_kind='unknown',finding_id=contribution_finding,authority_passage_id=authority,
    membership_passage_id=None,responsibility_limit=contribution_limit))
records['practice_actor_period'].append(dict(contribution_id=contribution,valid_from='2026-04-08',
    valid_to='2026-04-08',identity_passage_id=authority))
task('practice_contribution',contribution,contribution_text,contribution_limit)
task('practice_contribution.finding_id',contribution,contribution_text,contribution_limit)

reason = ('Dalgın’ın fiyat sepeti ve denetim çağrısı 10/3998 görüşmesinde İYİ Parti Grubu adına kayda geçti. '
          'Bu araçları önceleyen, İYİ Parti kimliğiyle doğrulanabilen tarihli söylem araştırılıyor.')
cid = stem+'-candidate'
records['practice_candidate'].append(dict(id=cid,scope_id=scope,event_id=eid,relation_id=None,
    state='unmatched',reason=reason,passage_ids=encoded(refs)))
task('practice_candidate',cid,reason,limit)
statement_scope = scope_for(topic,'statement')
records['practice_attempt_v2'].append(dict(id=stem+'-statement-search',scope_id=statement_scope,
    attempted_at=when,query='Burak Dalgın İYİ Parti TÜİK fiyat sepeti açıklama akademik denetim 8 Nisan 2026 öncesi; TBMM 7/13417 ve 7/14221',
    url=None,result='results',source_version_id=None,
    reason='2024 yazılı soruları Dalgın’ın DEVA dönemi kaydı. 20 Ocak 2026’da İYİ Parti Grubu adına kırmızı et fiyatı konuşması farklı araç ve kapsamda. İlgili önceki İYİ Parti söylemi açık.'))

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
for name,content in [('tuik-3998-group-draft.json',package),('tuik-3998-group-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
