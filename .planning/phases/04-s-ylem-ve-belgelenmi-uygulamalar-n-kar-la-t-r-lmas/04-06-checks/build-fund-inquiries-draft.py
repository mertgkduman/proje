"""21 Ekim tarihli iki bağımsız araştırma önergesini ayrı olaylar olarak ekle."""
import datetime
import hashlib
import json
from pathlib import Path

checks = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
sha = lambda b: hashlib.sha256(b).hexdigest()
raw = (checks/'fund-event-alignment-draft.json').read_bytes()
rr = (checks/'fund-event-alignment-review.json').read_bytes()
assert sha(raw)=='f537c6246f655f10608c82797eb9c4ac5554cc675d0b1e4c177f629b3d343d77'
assert sha(rr)=='b1dba2674a0ce8c1c901b80b5a638d0ddc49df59531810e36ab9bc8d9f72601d'
pkg, review = json.loads(raw), json.loads(rr)
entries = json.loads((checks/'fund-inquiries-source-records.json').read_text())['entries']
ps = {e['values']['id']:e['values'] for e in entries if e['kind']=='passage'}
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
scope = 'practice-eef45ed112da730d31f83015964c900d73e2f2a0bd64ee6694e03dacdad1839e'
add = lambda k, **v: entries.append(dict(kind=k, values=v))
for number, name in [('4830','Hüseyin Olan'),('4918','Mehmet Zeki İrmez')]:
    event = '0406-fund-'+number+'-event'
    finding = '0406-fund-'+number+'-f'
    contribution = '0406-fund-'+number+'-contribution'
    candidate = '0406-fund-'+number+'-unmatched'
    ver = '0406-fund-'+number+'-v1'
    pver = '0406-fund-'+number+'pdf-v1'
    q = lambda label: '0406-fund-'+number+'-'+label+'-p'
    ids = [q(x) for x in ('number','filed','owner','party','summary','pending')]+['0406-fund-'+number+'pdf-number-p']
    add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text=f'DEM Parti milletvekili {name} ve 19 milletvekilinin sermaye piyasalarında manipülasyon iddiaları ile idari ihmal ve sorumluların araştırılması için verdiği 10/{number} Meclis araştırması önergesi, 21 Ekim 2026 tarihinde TBMM Başkanlığına ulaştı. TBMM işlem kaydında erişim anındaki durum “Gündemde” olarak yer alıyor. Önerge, araştırma komisyonu kurulması veya iddiaların kanıtlanması anlamına gelmez.',provenance='summary',epistemic_type='claim')
    for pid in ids:
        add('finding_evidence',finding_id=finding,passage_id=pid,role='support')
        add('verification',finding_id=finding,passage_id=pid,checked_at=now,result='confirmed',reason='TBMM kaydı ve imzalı belgenin esas numarası karşılaştırıldı.')
    add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='İddialar önergeye atfedildi; araştırma istemi, erişim durumu ve gerçekleşmiş sonuç ayrıldı.')
    points = [(q('number'),'initiative','TBMM esas numarası'),(q('filed'),'initiative','Başkanlığa geliş tarihi'),(q('owner'),'action','İlk imza sahibi ve milletvekilleri'),(q('party'),'action','İlk imza sahibinin TBMM parti bilgisi'),(q('summary'),'action','Araştırma isteminin TBMM özeti'),(q('pending'),'action','Erişim anındaki kayıt durumu'),('0406-fund-'+number+'pdf-number-p','initiative','İmzalı belgedeki esas numarası')]
    records = {
      'practice_event':[dict(id=event,common_event_key='tbmm-28-5-10-'+number+'-arastirma-onergesi',event_at='2026-10-21',date_precision='day',date_unknown_reason=None,scope_context='TBMM Başkanlığına sermaye piyasası iddialarının araştırılması için verilen Meclis araştırması önergesi.',title='10/'+number+' Meclis araştırması önergesi',occurrence_basis='TBMM işlem kaydı ve imzalı önerge.')],
      'practice_event_evidence':[dict(event_id=event,passage_id=p,supported_point=point,stage=stage,concrete_basis='TBMM işlem kaydı veya imzalı belgenin esas numarası.',limitation='İddialar doğrulanmış olgu değildir; önerge komisyon kurulduğu sonucunu göstermez.',epistemic_type='claim') for p,stage,point in points],
      'practice_evidence_assessment':[dict(event_id=event,passage_id=p,stage=stage,basis_kind='document') for p,stage,_ in points],
      'practice_contribution':[dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='İlk imza sahibi ve diğer imzacılar adına araştırma talebi; komisyon kararı değil.')],
      'practice_attempt_v2':[dict(id='0406-fund-'+number+'-reading',scope_id=scope,attempted_at=now,query='TBMM 10/'+number+' sermaye piyasaları araştırma önergesi',url=next(e['values']['original_url'] for e in entries if e['kind']=='document_version' and e['values']['id']==ver),result='examined',reason='İşlem kaydı ve imzalı üç sayfa okundu; daha sonra komisyon kurulması doğrulanmadı.',source_version_id=ver),dict(id='0406-fund-'+number+'-pdf-reading',scope_id=scope,attempted_at=now,query='TBMM 10/'+number+' imzalı önerge',url=next(e['values']['original_url'] for e in entries if e['kind']=='document_version' and e['values']['id']==pver),result='examined',reason='İmzalı belgenin üç taranmış sayfası görsel okundu; esas numarası metin katmanıyla karşılaştırıldı.',source_version_id=pver)],
      'practice_scope_source':[dict(scope_id=scope,version_id=ver,inspected_sections=json.dumps([ps[p]['section'] for p in ids if ps[p]['version_id']==ver],ensure_ascii=False),inspected_at=now),dict(scope_id=scope,version_id=pver,inspected_sections=json.dumps(['İmzalı belgenin esas numarası'],ensure_ascii=False),inspected_at=now)],
      'practice_candidate':[dict(id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Tarihsel önceki söylemin uygunluğu ve kapsam eşlemesi açık; bu önerge araştırma komisyonu kurulduğu sonucu değildir.',passage_ids=json.dumps(ids,ensure_ascii=False))],
    }
    for k, values in records.items(): pkg['practice_records'].setdefault(k,[]).extend(values)
    targets=[('practice_event_evidence',event+'|'+p+'|'+stage,[p],point) for p,stage,point in points]
    targets += [('practice_event',event,ids,'Meclis araştırması istemi.'),('practice_contribution',contribution,ids,'DEM imzalı önerge.'),('practice_contribution.finding_id',contribution,ids,'Araştırma istemi ile sonuç ayrımı.'),('practice_candidate',candidate,ids,'Önceki söylem eşlemesi açık.')]
    for kind, ident, passages, claim in targets:
        review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(ps[p]['version_id'] for p in passages)),ensure_ascii=False),passage_ids=json.dumps(passages,ensure_ascii=False),inspected_sections=json.dumps(list(dict.fromkeys(ps[p]['section'] for p in passages)),ensure_ascii=False),supported_claim=claim,limitations='Önerge iddiaları doğrulanmış olgu veya komisyon kararı değildir.',result='reviewed',reason='TBMM işlem ve özgün belge karşılaştırıldı: '+claim))
pkg['entries'] += entries
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
for name,obj in [('fund-inquiries-draft.json',pkg),('fund-inquiries-review-draft.json',review)]:
    path=checks/name
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    print(name,sha(path.read_bytes()))
