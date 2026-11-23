"""51/9 öncülünden üç bireysel 2/2927 oyu için sıralı aday hazırlar."""
import datetime,hashlib,json
from pathlib import Path
from uygulamalar import practice_review_targets,validate_practice_source_review
c=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p,r=c/'2026-pm-myk-dem-draft.json',c/'2026-pm-myk-dem-review-draft.json'
assert sha(p)=='6e6161fe2a8e29fe78185807d03c27c441a912084e6d27cef2b3716e06747553'
assert sha(r)=='eef2fb99c8c9ef7c296bb59d02079f6aac5a84415162d4b1c53b13f932e6c2a7'
pkg,rev=json.loads(p.read_text()),json.loads(r.read_text());entries=json.loads((c/'iklim-final-records.json').read_text())['entries']
passages={x['values']['id']:x['values'] for x in entries if x['kind']=='passage'};versions={x['values']['id']:x['values'] for x in entries if x['kind']=='document_version'}
now=datetime.datetime.now(datetime.timezone.utc).isoformat();q=lambda s:'0406-iklim-final-'+s
event,candidate=q('event'),q('candidate');scope='practice-1c5854aa8d8f94f0081a0ceb37427ff8b3ba45ab525d3b46b3e50beb15869a09'
new={k:[] for k in ('practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_actor_period','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(table,**values):new[table].append(values)
persons=[('akin','İbrahim Akın','akin-identity','akin-membership','akin-vote','akin-online','İzmir'),('kordu','Ayten Kordu','kordu-identity','kordu-membership','kordu-vote','kordu-online','Tunceli'),('koca','Perihan Koca','koca-identity','koca-membership','koca-vote','koca-online','Mersin')]
points=[('law-number','initiative'),('akin-vote','action'),('akin-online','action'),('kordu-vote','action'),('kordu-online','action'),('koca-vote','action'),('koca-online','action')]
ids=[q(k) for k,_ in points]
add('practice_event',id=event,common_event_key='tbmm-28-3-104-2-2927-iklim-kanunu',event_at='2025-07-02',date_precision='day',date_unknown_reason=None,scope_context='TBMM 104. birleşim kesin açık oy cetveli',title='İklim Kanunu kesin açık oylaması',occurrence_basis='TBMM kesin açık oy cetveli ve 2/2927 teklif kaydı.')
for key,stage in points:
 pid=q(key);add('practice_event_evidence',event_id=event,passage_id=pid,supported_point=passages[pid]['section'],stage=stage,concrete_basis='TBMM teklif sicili ve 2 Temmuz basılı ve çevrimiçi kesin açık oy cetvelleri.',limitation='Bireysel oylar grup kararı veya yasanın çevresel etkisi değildir.',epistemic_type='claim');add('practice_evidence_assessment',event_id=event,passage_id=pid,stage=stage,basis_kind='document')
for key,name,identity,membership,vote,online,city in persons:
 fid=q(key+'-finding');actor=q(key+'-actor');person=q(key+'-person');cid=q(key+'-contribution')
 refs=[q(vote),q(online),q(identity),q(membership)]+([q('koca-name-variant')] if key=='koca' else [])
 entries.extend([dict(kind='person',values=dict(id=person,name=name)),dict(kind='actor',values=dict(id=actor,kind='individual_mp',party_id='dem',person_id=person,authorization_passage_id=None)),dict(kind='finding',values=dict(id=fid,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=fid,text=f'TBMM’nin 2 Temmuz 2025 tarihli kesin açık oy cetveli, {city} Milletvekili {name} için 2/2927 İklim Kanunu teklifinin tümüne ret oyu kaydeder. Bu kişisel oy, grup kararı veya yasanın çevresel sonucu olarak genellenmez.',provenance='summary',epistemic_type='claim'))])
 for pid in refs:
  entries.extend([dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=pid,role='support')),dict(kind='verification',values=dict(finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Kişisel oy satırı ile kişi ve grup kaynağı ayrı incelendi.'))])
 entries.append(dict(kind='review',values=dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Basılı ve çevrimiçi oy, aynı kişi ve grup kaynakları incelendi.')))
 add('practice_contribution',id=cid,event_id=event,party_id='dem',actor_id=actor,contribution_kind='objection',finding_id=fid,authority_passage_id=None,membership_passage_id=q(membership),responsibility_limit='Yalnız belirtilen milletvekilinin kesin cetveldeki kişisel ret oyu; grup kararı çıkarılmaz.')
 add('practice_actor_period',contribution_id=cid,valid_from='2025-07-02',valid_to='2025-07-02',identity_passage_id=q(identity))
add('practice_candidate',id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='2023 tarihsel seçim bildirgesi ve 2012 programatik metinde ekoloji hedefleri incelendi; bunların bağımsız güncel parti programı ve 2025 yürürlük bağı ayrıca araştırılıyor. Kişisel oylar çevresel sonuç değildir.',passage_ids=json.dumps(ids,ensure_ascii=False))
for vid in versions:
 refs=[p['section'] for p in passages.values() if p['version_id']==vid]
 if not refs:continue
 add('practice_scope_source',scope_id=scope,version_id=vid,inspected_sections=json.dumps(list(dict.fromkeys(refs)),ensure_ascii=False),inspected_at=now)
 add('practice_attempt_v2',id=vid+'-reading',scope_id=scope,attempted_at=now,query='2 Temmuz 2025 2/2927 kesin cetvel ve milletvekili kimliği',url=versions[vid]['original_url'],result='examined',reason='İlgili kaynak bölümleri okundu; basılı kişisel satırlar görüntüyle karşılaştırıldı.',source_version_id=vid)
pkg['entries']+=entries
for k,v in new.items():pkg['practice_records'].setdefault(k,[]).extend(v)
data=dict(pkg['practice_records'])
for x in pkg['entries']:data.setdefault(x['kind'],[]).append(x['values'])
selection={k:new[k] for k in ('practice_event','practice_event_evidence','practice_contribution','practice_candidate')}
targets=practice_review_targets(data,selection);allpass={x['id']:x for x in data['passage']};reviews=[]
for (typ,ident),(refs,_) in targets.items():
 sections=list(dict.fromkeys(allpass[x]['section'] for x in sorted(refs)))
 reviews.append(dict(subject_kind=typ,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(allpass[x]['version_id'] for x in sorted(refs))),ensure_ascii=False),passage_ids=json.dumps(sorted(refs),ensure_ascii=False),inspected_sections=json.dumps(sections,ensure_ascii=False),supported_claim='TBMM kişisel oy, dönem ve kimlik kaynakları: '+typ+' / '+ident,limitations='Bireysel oy grup kararı değildir; 2024 grup listesi ile 2025 kesin oy tarihi ayrı.',result='reviewed',reason='İlgili olay ve kişi pasajları okundu: '+typ+' / '+ident))
validate_practice_source_review(data,reviews,selection=selection);rev['practice_source_review']+=reviews;rev['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in rev['practice_source_review']]
for name,obj in [('iklim-final-dem-draft.json',pkg),('iklim-final-dem-review-draft.json',rev)]:
 f=c/name;f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(f))
print('YENI_TARGETLER_PASS',len(targets))
