import copy,datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
P=Path(__file__).parent; read=lambda p:json.loads(Path(p).read_text()); sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
live=Path('data/practices/04-tip.json'); prev=Path('data/practices/04-tip-review.json')
assert sha(live)=='48969df867c4562088ef11217e605bce7e1457dd5e7babe80b7093f70f5ae7e5' and sha(prev)=='a390e74fc8a671791eb93762d95e2799d3098f6841a51d21e99a801bb4d74323'
pkg=read(live); old=read(prev); base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json'); src=read(P/'fatura-3864-source-draft.json'); now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
entries=pkg['entries']; records=pkg['practice_records']; entries.extend(copy.deepcopy(src['entries']))
def add(table,**v):entries.append(dict(kind=table,values=v))
prefix='0405-tip-fatura-3864'; event=prefix+'-event'; fid=prefix+'-finding'; candidate=prefix+'-unmatched'; con=prefix+'-contribution'; scope=next(x['id'] for x in records['practice_scope_v2'] if x['topic_id']=='tuketici-haklari' and x['research_kind']=='event')
measure=prefix+'-measure-p'; authority=prefix+'-authority-p'; number=prefix+'-detail-number-p'; date=prefix+'-detail-date-p'; status=prefix+'-hukumsuz-p'; refs=[authority,measure,number,date,status]
add('finding',id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Baş ve üç milletvekilinin 8 Ekim 2021’de sunduğu 2/3864 teklifi, belirli gelir ve tüketim koşullarında elektrik faturalarına kademeli Hazine desteği önerdi. Teklif dönem sonunda hükümsüz sayıldı.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Teklif ve dönem sonu listesinin ayrı pasajları okundu; teklifin uygulanması çıkarılmadı.')
for pid in refs:
 add('finding_evidence',finding_id=fid,passage_id=pid,role='support');add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün imzalı tarama, TBMM kayıt ekranı veya tarihsel liste incelendi.')
records['practice_event'].append(dict(id=event,common_event_key='tbmm-27-5-2-3864-fatura-destegi',event_at='2021-10-08',date_precision='day',date_unknown_reason=None,scope_context='27. dönem 2/3864 kanun teklifi',title='Fatura desteği kanun teklifi',occurrence_basis='TBMM imzalı teklif ve teklif kayıt ekranı.'))
for pid,stage,point in [(authority,'initiative','Baş’ın TİP Genel Başkanı sıfatıyla imzası'),(measure,'initiative','Gelir ve tüketim koşullarında elektrik faturasının karşılanması önerisi'),(number,'initiative','2/3864 teklif numarası'),(date,'initiative','8 Ekim 2021 geliş tarihi'),(status,'result','Dönem sonunda hükümsüz sayılan teklifler listesi')]:
 records['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,supported_point=point,stage=stage,concrete_basis='TBMM özgün teklif, kayıt ekranı veya dönem sonu listesi.',limitation='Teklif ve hükümsüzlük, uygulama etkisini veya diğer enerji desteği mevzuatını göstermez.',epistemic_type='claim'))
 records['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage=stage,basis_kind='document'))
add('actor',id=prefix+'-bas-actor',kind='authorized_representative',party_id='tip',person_id='0405-tip-erkan-bas',authorization_passage_id=authority)
records['practice_contribution'].append(dict(id=con,event_id=event,party_id='tip',actor_id=prefix+'-bas-actor',contribution_kind='task',finding_id=fid,authority_passage_id=authority,membership_passage_id=None,responsibility_limit='Baş dört imzacıdan biridir; kabul yetkisi TBMM’dedir.'))
records['practice_actor_period'].append(dict(contribution_id=con,valid_from='2021-10-08',valid_to='2021-10-08',identity_passage_id=authority))
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='2022 açıklaması ve 2022 yazılı soru bu 2021 teklifinden sonradır; önceki doğrudan karşılaştırılabilir söylem ayrıca araştırılmaktadır.',passage_ids=json.dumps(refs)))
vids=['0405-tip-fatura-3864-v1','0405-tip-fatura-3864-detail-v1','0405-tip-sendika-hukumsuz-v1']
for index,vid in enumerate(vids):
 version=next(x['values'] for x in entries if x['kind']=='document_version' and x['values']['id']==vid); url=version['original_url']; sections=sorted({x['values']['section'] for x in src['entries'] if x['kind']=='passage' and x['values']['version_id']==vid}); aid=prefix+'-attempt-'+str(index)
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason='Teklif veya dönem sonu kaydı',state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason='İlgili teklif ve sonuç pasajları okundu; kapsam açık.',source_version_id=vid))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():
 if table in ('practice_contract','practice_coverage_contract','practice_variant_contract','practice_evidence_contract'):data[table]=copy.deepcopy(rows)
 else:data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{r['passage_id'] for r in records['practice_event_evidence']},party_id='tip'); passages={p['id']:p for p in data['passage']}; oldmap={(r['subject_kind'],r['subject_id']):r for r in old['practice_source_review']}; reviews=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
 if (kind,identity) in oldmap:reviews.append(oldmap[(kind,identity)]);continue
 rows=[passages[x] for x in sorted(ids)];reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({x['version_id'] for x in rows})),passage_ids=json.dumps([x['id'] for x in rows]),inspected_sections=json.dumps(sorted({x['section'] for x in rows}),ensure_ascii=False),supported_claim='İmzalı teklif ve dönem sonu hükümsüzlük kaydı okundu.',limitations='Teklif uygulama anlamına gelmez; hükümsüzlük günü ayrıca kesinleştirilmedi.',result='reviewed',reason=kind+' / '+identity+' özgün kaynakları incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='tip',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];pkg['source_review_refs']=refs
for name,obj in [('fatura-3864-append-draft.json',pkg),('fatura-3864-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (P/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('3864_SEMANTIC_PASS',len(reviews),event,candidate)
