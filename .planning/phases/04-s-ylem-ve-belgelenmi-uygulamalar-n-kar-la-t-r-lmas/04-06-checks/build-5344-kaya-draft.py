"""Aynı toplantıda Kaya'nın ayrı, açık parti konuşmasını eklemeli aday yap."""
import datetime,hashlib,json
from pathlib import Path
from arsiv import pdf_page_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks');d=Path('data/practices');sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(d/'04-dem.json').read_bytes();rr=(d/'04-dem-review.json').read_bytes()
assert sha(raw)=='051d079bee95465cd535b7a409954efb72e042b14388c205e642b6344da2600d' and sha(rr)=='277dbaf2b240144f4e820586cbdd2c7f99bc425485daa0f57c256f51b4f87b7b'
pkg,review=json.loads(raw),json.loads(rr);now=datetime.datetime.now(datetime.timezone.utc).isoformat()
src=json.loads((p/'2026-5344-kaya-source-records.json').read_text())['entries'];ver=next(e['values'] for e in src if e['kind']=='document_version');path=d/'sources/dem'/ver['original_path'];assert sha(path.read_bytes())==ver['sha256']
entries=[e for e in src if e['kind']=='passage'];entries += [e for e in json.loads((p/'2026-5344-amendment-source-records.json').read_text())['entries'] if e['kind']=='passage'];passages={e['values']['id']:e['values'] for e in entries};qs=list(passages)
for v in passages.values():assert v['exact'] in pdf_page_text(path,v['pdf_page_index'])
event='0406-2026-23464-commission';finding='0406-2026-23464-kaya-f';contribution='0406-2026-23464-kaya-contribution';candidate='0406-2026-23464-kaya-unmatched';scope='practice-dc586aedd6823cc75eed15c27730c61cb76b7188c1144547f739f0c8edb96f4d'
def add(k,**v):entries.append(dict(kind=k,values=v))
add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='Adalet Kaya komisyonda 20 bin liralık alt emekli aylığı teklifini eleştirip DEM PARTİ adına 50 bin lira ve belirli yaşın üzerindeki kadınlara temel yurttaşlık geliri talep etti. Kaya, Tanhan ve Oluç’un yoksulluk sınırının yarısından az olmayan alt aylık önergesi komisyonda kabul edilmedi.',provenance='summary',epistemic_type='claim')
for q in qs:
 add('finding_evidence',finding_id=finding,passage_id=q,role='support');add('verification',finding_id=finding,passage_id=q,checked_at=now,result='confirmed',reason='Konuşmacı ve DEM adına dile getirilen talep TBMM özgün tutanağında okundu.')
add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Talep, oylama ve gerçekleşme ayrı değerlendirildi.')
points=[(q,'action',passages[q]['section'],'Komisyon tutanağında Kaya konuşması.') for q in qs[:2]]+[(qs[2],'initiative','Üç milletvekilinin yeni madde önergesi','İmzalı önerge yoksulluk sınırının yarısı esasına dayanır.'),(qs[2],'result','Yeni madde önergesinin komisyon sonucu','Başkan önergenin kabul edilmediğini açıkladı.')]
rec={
'practice_event_evidence':[dict(event_id=event,passage_id=q,supported_point=point,stage=stage,concrete_basis=basis,limitation='Komisyon konuşmasındaki talep; yürürlüğe giren gelir veya fiilî ödeme değildir.',epistemic_type='claim') for q,stage,point,basis in points],
'practice_evidence_assessment':[dict(event_id=event,passage_id=q,stage=stage,basis_kind='document') for q,stage,_,_ in points],
'practice_contribution':[dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='objection',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='Kaya’nın parti adına konuşması ve üç imzacının önergesi; komisyon reddi ayrı, kanunlaşma veya ödeme değildir.')],
'practice_attempt_v2':[dict(id='0406-5344-kaya-reading',scope_id=scope,attempted_at=now,query='TBMM 15 Ocak 2026 2/3464 Adalet Kaya DEM yaşlı kadın temel yurttaşlık geliri',url=ver['original_url'],result='examined',reason='Tutanak PDF 20–21 konuşmacı ve parti adına belirtilen talepler okundu.',source_version_id=ver['id'])],
'practice_scope_source':[dict(scope_id=scope,version_id=ver['id'],inspected_sections=json.dumps([v['section'] for v in passages.values()],ensure_ascii=False),inspected_at=now)],
'practice_candidate':[dict(id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Kongre kararları ekindeki temel gelir beyanıyla konu ilişkili; ekin tarihi belirsiz ve bu komisyon talebi gelir uygulamasının gerçekleşmesi değildir. Önceki söylem ve dönemsel ilişki araştırması açık.',passage_ids=json.dumps(qs,ensure_ascii=False))]}
pkg['entries']+=entries
for k,v in rec.items():pkg['practice_records'].setdefault(k,[]).extend(v)
items=[('practice_event_evidence',event+'|'+q+'|'+stage,[q],point) for q,stage,point,_ in points]
items += [('practice_contribution',contribution,qs,'DEM adına emeklilik ve yaşlı kadın geliri talepleri.'),('practice_contribution.finding_id',contribution,qs,'Kaya açıklaması özgün tutanakta.'),('practice_candidate',candidate,qs,'Önceki söylem tarihi ve uygulama araştırması açık.')]
for kind,ident,ps,claim in items:
 review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps([ver['id']]),passage_ids=json.dumps(ps),inspected_sections=json.dumps([passages[q]['section'] for q in ps],ensure_ascii=False),supported_claim=claim,limitations='DEM adına belirtilen talepler fiilen sağlanan gelir veya isimli oy değildir.',result='reviewed',reason='TBMM özgün tutanağı okundu: '+claim))
event_review=next(x for x in review['practice_source_review'] if x['subject_kind']=='practice_event' and x['subject_id']==event)
event_review['passage_ids']=json.dumps(list(dict.fromkeys(json.loads(event_review['passage_ids'])+qs)),ensure_ascii=False)
event_review['inspected_sections']=json.dumps(list(dict.fromkeys(json.loads(event_review['inspected_sections'])+[passages[q]['section'] for q in qs])),ensure_ascii=False)
event_review['supported_claim']+=' Kaya konuşması ve üç imzalı önergenin komisyonda reddi de ayrı kaynaklanır.'
event_review['reason']+=' Komisyon olayına eklenen tüm yeni pasajlar da incelendi.'
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
for name,obj in [('5344-kaya-draft.json',pkg),('5344-kaya-review-draft.json',review)]:
 path=p/name;path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(path.read_bytes()))
