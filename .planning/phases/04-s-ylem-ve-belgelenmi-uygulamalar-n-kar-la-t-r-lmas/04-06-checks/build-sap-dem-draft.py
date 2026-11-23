"""63 olaylı adaydan sonra 10/2882 için DEM konuşmasını hazırlar."""
import datetime, hashlib, json
from pathlib import Path
from uygulamalar import practice_review_targets, validate_practice_source_review
c=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base,review=c/'iklim-103-motions-dem-draft.json',c/'iklim-103-motions-dem-review-draft.json'
assert sha(base)=='560d462a1d24a52b7535a7f41f646613f9795e840f6be52f61b7ccad4f9916d9'
assert sha(review)=='94ab250fda1f9414e9557b69c9d2b21ef5ea9309141c21166fba713b0738a4f8'
pkg,rev=json.loads(base.read_text()),json.loads(review.read_text())
entries=json.loads((c/'sap-2882-source-records.json').read_text())['entries']
passages={x['values']['id']:x['values'] for x in entries if x['kind']=='passage'}
versions={x['values']['id']:x['values'] for x in entries if x['kind']=='document_version'}
floor=next(e['values'] for e in pkg['entries'] if e['kind']=='document_version' and e['values']['id']=='0406-iklim-final-floor-v1');versions[floor['id']]=floor
q=lambda s:'0406-sap-2882-'+s
event,finding,contribution,candidate=(q(s) for s in ('event','finding','contribution','candidate'))
scope='practice-7a023a771bdbf733b7194911ea57488514664331820c5d923e17794709742742'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
new={k:[] for k in ('practice_scope_v2','practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(k,**v):new[k].append(v)
add('practice_scope_v2',id=scope,party_id='dem',topic_id='tarim-hayvancilik',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='Yalnız 2 Temmuz 2025 şap hastalığı araştırmasının gündem talebi ve DEM grup görüşü; tarım ve hayvancılık kapsamı araştırılıyor.')
points=[('signed-number','initiative'),('register-number','initiative'),('register-date','initiative'),('register-count','initiative'),('register-status','result'),('floor-call','initiative'),('floor-role','action'),('floor-speech','action'),('floor-vote','result')]
ids=[q(n) for n,_ in points]
add('practice_event',id=event,common_event_key='tbmm-28-3-104-10-2882-gundem',event_at='2025-07-02',date_precision='day',date_unknown_reason=None,title='10/2882 şap hastalığı araştırmasının ön görüşme talebinin reddi',scope_context='İYİ Parti Grubu, Mehmet Akalın’ın şap hastalığı ve hayvan ithalatına ilişkin 10/2882 araştırma önergesinin ön görüşmesinin 2 Temmuz 2025 birleşiminde yapılmasını istedi. Genel Kurul bu gündem talebini reddetti.',occurrence_basis='TBMM 28. Dönem 3. Yasama Yılı 104. Birleşim tam tutanağı, imzalı 10/2882 önergesi ve TBMM esas kaydı.')
entries.append(dict(kind='finding',values=dict(id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='2 Temmuz 2025 Genel Kurulunda DEM Parti Grubu adına Beritan Güneş Altın, şap hastalığı araştırması gündeminde yaygın ve ücretsiz aşılama çağrısı yaptı. İYİ Parti’nin 10/2882 araştırmasının aynı gün ön görüşülmesi yönündeki grup önerisi kabul edilmedi; esas kaydı erişimde Gündemdeydi. Tutanak Akalın ve 19, esas kaydı Akalın ve 20 milletvekili diyor; farkın nedeni açık. Konuşmadan açık destek veya isimli oy çıkarılamaz.',provenance='summary',epistemic_type='claim')))
for n,stage in points:
 p=passages[q(n)];entries.extend([dict(kind='finding_evidence',values=dict(finding_id=finding,passage_id=q(n),role='support')),dict(kind='verification',values=dict(finding_id=finding,passage_id=q(n),checked_at=now,result='confirmed',reason='İmzalı dosya üç sayfa görsel, esas sicili ve tutanak ilgili kesiti incelendi.'))]);add('practice_event_evidence',event_id=event,passage_id=q(n),supported_point=p['section'],stage=stage,concrete_basis='TBMM imzalı önerge, esas sicili ve birleşim tutanağı.',limitation='Gündem kararı esas araştırmanın sonucu değildir; imzacı sayıları arasında fark açık.',epistemic_type='claim');add('practice_evidence_assessment',event_id=event,passage_id=q(n),stage=stage,basis_kind='document')
entries.append(dict(kind='review',values=dict(id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Grup konuşması, kaynaklar ve imzacı sayısı farkı incelendi.')))
add('practice_contribution',id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='unknown',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM grubu adına aşılama çağrısı; açık destek, kişisel oy ve esas sonuca ilişkin çıkarım yapılmadı.')
add('practice_candidate',id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Tarım ve hayvancılıkta önceki bağımsız parti söylemi ve dönemsel eşleştirme araştırması açıktır.',passage_ids=json.dumps(ids,ensure_ascii=False))
for vid in dict.fromkeys(passages[i]['version_id'] for i in ids):
 refs=[i for i in ids if passages[i]['version_id']==vid];add('practice_scope_source',scope_id=scope,version_id=vid,inspected_sections=json.dumps([passages[i]['section'] for i in refs],ensure_ascii=False),inspected_at=now);add('practice_attempt_v2',id=q(vid+'-reading'),scope_id=scope,attempted_at=now,query='2 Temmuz 2025 10/2882 şap ve DEM grup konuşması',url=versions[vid]['original_url'],result='examined',reason='Tutanak ve sicil okundu; imzalı belgenin üç sayfası görsel incelendi.',source_version_id=vid)
pkg['entries']+=entries
for k,rows in new.items():pkg['practice_records'].setdefault(k,[]).extend(rows)
data=dict(pkg['practice_records'])
for x in pkg['entries']:data.setdefault(x['kind'],[]).append(x['values'])
selection={k:new[k] for k in ('practice_event','practice_event_evidence','practice_contribution','practice_candidate')};targets=practice_review_targets(data,selection);allp={p['id']:p for p in data['passage']};reviews=[]
for (typ,ident),(refs,_) in targets.items():
 refs=sorted(refs);reviews.append(dict(subject_kind=typ,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(allp[x]['version_id'] for x in refs)),ensure_ascii=False),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps(list(dict.fromkeys(allp[x]['section'] for x in refs)),ensure_ascii=False),supported_claim='10/2882 kaynak ve DEM katkısı: '+typ+' / '+ident,limitations='İmzacı sayıları farkı açık; destek, isimli oy ve esas önergenin sonucu çıkarılmadı.',result='reviewed',reason='Kaynak pasajları ve üç görsel sayfa incelendi.'))
validate_practice_source_review(data,reviews,selection=selection);rev['practice_source_review']+=reviews;rev['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in rev['practice_source_review']]
for name,obj in [('sap-dem-draft.json',pkg),('sap-dem-review-draft.json',rev)]:
 p=c/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(name,sha(p))
print('SAP_TARGET_REVIEW_PASS',len(targets))
