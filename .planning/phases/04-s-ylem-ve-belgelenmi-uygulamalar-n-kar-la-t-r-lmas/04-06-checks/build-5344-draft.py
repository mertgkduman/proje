"""2/3464 komisyon görüşmesindeki doğrudan DEM konuşmasını ayrı olay olarak ekle."""
import datetime,hashlib,json
from pathlib import Path
from arsiv import pdf_page_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks');d=Path('data/practices'); sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(d/'04-dem.json').read_bytes();rr=(d/'04-dem-review.json').read_bytes()
assert sha(raw)=='567774b152bc0931d195521cce07255d07f6c9db70dd965ef023370f9068e626' and sha(rr)=='23f8762e0e77b5c1533900545e1623ef9c3221f4eda032572b416d6b0c2a9570'
pkg,review=json.loads(raw),json.loads(rr); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
entries=json.loads((p/'2026-5344-direct-source-records.json').read_text())['entries']; ver=next(e['values'] for e in entries if e['kind']=='document_version'); source=d/'sources/dem'/ver['original_path']; assert sha(source.read_bytes())==ver['sha256']
passages={e['values']['id']:e['values'] for e in entries if e['kind']=='passage'}
for v in passages.values():assert v['exact'] in pdf_page_text(source,v['pdf_page_index'])
qs=list(passages);event='0406-2026-23464-commission';finding='0406-2026-23464-commission-f';contribution='0406-2026-23464-commission-contribution';candidate='0406-2026-23464-commission-unmatched';scope='practice-5a881b0a216826a2360edc436182d8f5270ed950adef9e13b3f8072eed6e9365'
def add(k,**v):entries.append(dict(kind=k,values=v))
add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='Hakkı Saruhan Oluç, 2/3464 teklifinin komisyondaki görüşmesinde 20 bin TL alt emekli aylığını ve emeklilik sistemini eleştirerek kamusal sosyal güvenlik ve yapısal reform istedi; başka bir maddede işveren desteğinin İşsizlik Sigortası Fonundan ödenmesine itiraz etti.',provenance='summary',epistemic_type='claim')
for q in qs:
 add('finding_evidence',finding_id=finding,passage_id=q,role='support');add('verification',finding_id=finding,passage_id=q,checked_at=now,result='confirmed',reason='15 Ocak tutanağının özgün PDF sayfasında konuşmacı ve konu okundu.')
add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Emekli aylığı ve altıncı maddede fon hakkındaki ayrı konuşmalar ayırt edildi.')
points=[(q,'action',passages[q]['section'],'Komisyon tutanağındaki Oluç konuşması.') for q in qs]
rec={
'practice_event':[dict(id=event,common_event_key='tbmm-pbk-2026-01-15-2-3464',event_at='2026-01-15',date_precision='day',date_unknown_reason=None,scope_context='TBMM Plan ve Bütçe Komisyonunun 26. toplantısında 2/3464 sayılı teklifin görüşülmesi',title='2/3464 komisyon görüşmesinde emeklilik ve işsizlik fonu',occurrence_basis='TBMM Plan ve Bütçe Komisyonunun 15 Ocak tarihli özgün tutanağı.')],
'practice_event_evidence':[dict(event_id=event,passage_id=q,supported_point=point,stage=stage,concrete_basis=basis,limitation='Komisyondaki sözler; ayrı madde oyu, çıkarılan kanunun sonucu veya sosyal güvenlikte fiilî değişim değildir.',epistemic_type='claim') for q,stage,point,basis in points],
'practice_evidence_assessment':[dict(event_id=event,passage_id=q,stage=stage,basis_kind='document') for q,stage,_,_ in points],
'practice_contribution':[dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='objection',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='Oluç’un komisyon konuşması; grup adına isimli oy veya kanun sonucunun tek başına kanıtı değildir.')],
'practice_attempt_v2':[dict(id='0406-5344-commission-reading',scope_id=scope,attempted_at=now,query='TBMM 15 Ocak 2026 2/3464 emekli aylığı Hakkı Saruhan Oluç işsizlik fonu',url=ver['original_url'],result='examined',reason='Kapak ve PDF 8, 9, 58; emekli aylığı ve ayrı fon konuşmaları okundu.',source_version_id=ver['id'])],
'practice_scope_source':[dict(scope_id=scope,version_id=ver['id'],inspected_sections=json.dumps([v['section'] for v in passages.values()],ensure_ascii=False),inspected_at=now)],
'practice_candidate':[dict(id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Seçili Faz 3 sosyal hizmet söyleminde emeklilik sistemine özgü doğrudan bir önceki hedef gösterilmedi; bağımsız parti programı ve diğer söylemler araştırması açık.',passage_ids=json.dumps(qs,ensure_ascii=False))]}
pkg['entries']+=entries
for k,v in rec.items():pkg['practice_records'].setdefault(k,[]).extend(v)
items=[('practice_event_evidence',event+'|'+q+'|'+stage,[q],point) for q,stage,point,_ in points]
items += [('practice_event',event,qs,'15 Ocak komisyon görüşmesi.'),('practice_contribution',contribution,qs,'Oluç emeklilik ve fon konularında ayrı eleştiriler dile getirdi.'),('practice_contribution.finding_id',contribution,qs,'Konuşmalar ayrı sayfalarda desteklenir.'),('practice_candidate',candidate,qs,'Önceki emeklilik söylemi eşlemesi açık.')]
for kind,ident,ps,claim in items:
 review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps([ver['id']]),passage_ids=json.dumps(ps),inspected_sections=json.dumps([passages[q]['section'] for q in ps],ensure_ascii=False),supported_claim=claim,limitations='Konuşma komisyon görüşmesidir; ayrı madde oyu veya fiilî sonuç değildir.',result='reviewed',reason='TBMM özgün tutanağı ilgili sayfalarda okundu: '+claim))
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
for name,obj in [('5344-combined-draft.json',pkg),('5344-combined-review-draft.json',review)]:
 path=p/name;path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(path.read_bytes()))
