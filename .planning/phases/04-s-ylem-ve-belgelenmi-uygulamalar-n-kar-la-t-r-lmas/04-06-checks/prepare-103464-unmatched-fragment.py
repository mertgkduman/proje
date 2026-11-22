"""Önceki söyleme eşlenmemiş 10/3464 olayı için eklenebilir taslak."""
import datetime
import json
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
event, candidate, contribution = '0406-2025-103464-gundem', '0406-2025-103464-unmatched', '0406-2025-103464-contribution'
scope = 'practice-ae547a34c2afbfccd7913c6eed51c5a5a6d7f422594965429bb8466e60594705'
version = '0406-tbmm-2025-24-v1'
speaker, proposal, first, second = ['0406-tbmm-2025-24-'+x+'-p' for x in ('disability-speaker','disability-income','noquorum','second-rollcall')]
points = [(speaker,'initiative','DEM grubu konuşmacısı','Tutanak DEM grubu adına Gergerlioğlu’nu gösterir.'),(proposal,'initiative','Gelire ilişkin öneri','Konuşmacı gelir eşiği ve asgari ücret düzeyinde ödeme önerir.'),(first,'result','İlk yoklamada yeter sayı yok','Tutanak DEM grup önerisinin oylanması öncesinde yeter sayı bulunmadığını belirtir.'),(second,'result','İkinci yoklama ve kapanış','Başkan ikinci yoklamada yeter sayı bulunamadığından birleşimi kapatır.')]
entries = []
def add(kind, values): entries.append({'kind':kind,'values':values})
finding='0406-103464-contribution-f'
add('finding',dict(id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='Ömer Faruk Gergerlioğlu DEM grubu adına engelli yurttaşların gelirine ilişkin öneriyi açıkladı; oylama öncesi iki yoklamada yeter sayı bulunmadığından birleşim kapandı.',provenance='summary',epistemic_type='claim'))
for q,_,_,_ in points:
    add('finding_evidence',dict(finding_id=finding,passage_id=q,role='support'))
    add('verification',dict(finding_id=finding,passage_id=q,checked_at=now,result='confirmed',reason='TBMM birleşim tutanağının özgün metni incelendi.'))
add('review',dict(id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Öneri, görüşme takvimi ve yeter sayı yokluğu ayrı okundu.'))
url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/24/Tam/2842bd28-bf72-4455-bc86-4efae804ab3f.html'
r={
 'practice_scope_v2':[dict(id=scope,party_id='dem',topic_id='engellilik',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='Yalnız 3 Aralık 2025 araştırma önergesinin ön görüşme takvimi; engellilik kapsamı araştırması sürüyor.')],
 'practice_event':[dict(id=event,common_event_key='tbmm-28-4-24-10-3464-gundem',event_at='2025-12-03',date_precision='day',date_unknown_reason=None,scope_context='TBMM 28. dönem 4. yasama yılı 24. birleşim; DEM 10/3464 araştırma önergesi ön görüşme takvimi',title='Engelli yurttaşlar araştırmasının ön görüşme takvimi',occurrence_basis='TBMM Genel Kurulu birleşim tutanağı.')],
 'practice_event_evidence':[dict(event_id=event,passage_id=q,supported_point=point,stage=stage,concrete_basis=basis,limitation='Yoklama sonucu araştırma önergesinin kabulü veya reddi değildir; ödeme yapıldığı gösterilmez.',epistemic_type='claim') for q,stage,point,basis in points],
 'practice_evidence_assessment':[dict(event_id=event,passage_id=q,stage=stage,basis_kind='document') for q,stage,point,basis in points],
 'practice_contribution':[dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='support',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='Grup adına açıklanan öneri; kabul, ret veya ödeme sonucu değil.')],
 'practice_attempt_v2':[dict(id='0406-103464-tutanak-okuma',scope_id=scope,attempted_at=now,query='TBMM 28/4/24 DEM 10/3464 grup önerisi ve yoklama',url=url,result='examined',reason='Grup konuşması ve iki yoklama özgün tutanakta okundu.',source_version_id=version)],
 'practice_scope_source':[dict(scope_id=scope,version_id=version,inspected_sections=json.dumps(['DEM grup konuşması','İlk ve ikinci yoklama, birleşimin kapanışı'],ensure_ascii=False),inspected_at=now)],
 'practice_candidate':[dict(id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Faz 3 seçili engellilik söylemi parti faaliyetlerinin sesli, görsel ve işaret dili sürümleridir; gelir önerisini o hedefin gerçekleşmesi olarak bağlamak desteklenmez. Diğer uygun söylemler ve adaylar araştırılacak.',passage_ids=json.dumps([x[0] for x in points],ensure_ascii=False))]
}
items=[('practice_event_evidence',event+'|'+q+'|'+stage,[q],point) for q,stage,point,_ in points]
items += [('practice_event',event,[speaker,proposal,first,second],'DEM grubu konuşması ve iki yoklama ayrı aşamalardır.'),('practice_contribution',contribution,[speaker,proposal,first,second],'Gergerlioğlu grup adına gelir önerisini açıkladı; oylama yapılmadı.'),('practice_contribution.finding_id',contribution,[speaker,proposal,first,second],'Katkı ve yoklama sınırı tutanakla desteklenir.'),('practice_candidate',candidate,[speaker,proposal,first,second],'Gelir önerisi, seçili işaret dili söyleminin gerçekleşmesi sayılmaz; eşleme araştırması açık.')]
reviews=[]
for kind, ident, passages, claim in items:
    reviews.append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps([version]),passage_ids=json.dumps(passages,ensure_ascii=False),inspected_sections=json.dumps([next(x[2] for x in points if x[0]==q) for q in passages],ensure_ascii=False),supported_claim=claim,limitations='Ön görüşme takviminde yeter sayı bulunmaması kabul, ret veya ödeme sonucu değildir; söylem eşlemesi açık.',result='reviewed',reason='İlgili kaynak ve sınırları okundu: '+claim))
(p/'103464-unmatched-fragment-draft.json').write_text(json.dumps(dict(entries=entries,practice_records=r,practice_source_review=reviews),ensure_ascii=False,indent=2)+'\n')
print('103464_UNMATCHED_FRAGMENT_DRAFT',len(entries),len(reviews))
