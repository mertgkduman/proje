"""8 Ekimdeki iki ayrı grup talebini, 5472 adayının üzerine hazırlar."""
import datetime, hashlib, json
from pathlib import Path
c=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
p=c/'5472-motions-v2-draft.json'; r=c/'5472-motions-v2-review-draft.json'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='c6d3d3f3d8fbb75639cfc4bc94fe0dc85acd25d062b116a252877136314d6e74'
assert hashlib.sha256(r.read_bytes()).hexdigest()=='aefdb613131b4a115fdff379b726c6497fb9ca57f458bf99b65d9db34e4bb6d8'
pkg,review=json.loads(p.read_bytes()),json.loads(r.read_bytes())
entries=json.loads((c/'2026-oct08-source-records.json').read_text())['entries']; passages={e['values']['id']:e['values'] for e in entries if e['kind']=='passage'}
now=datetime.datetime.now(datetime.timezone.utc).isoformat(); ver='0406-oct08-floor-v1'; scope='practice-eef45ed112da730d31f83015964c900d73e2f2a0bd64ee6694e03dacdad1839e'; q=lambda x:'0406-oct08-floor-'+x
specs=[
 ('yeniyol','tbmm-28-5-004-10-4603-gundem','10/4603 araştırma önergesinin 8 Ekim’de görüşülmesi','Yeni Yol Grubu 10/4603’ün 8 Ekim birleşiminde ön görüşmeye alınmasını önerdi. Genel Kurul grup önerisini kabul etmedi.','TBMM önergesi, birleşim tutanağı ve ilgili işlem belgeleri.','support','8 Ekim 2026 Genel Kurulunda DEM Parti Grubu adına Cengiz Çiçek, Yeni Yol’un 10/4603 önergesinin aynı gün görüşülmesi önerisini sözlü destekledi. Başkan grup önerisinin kabul edilmediğini duyurdu. Bu açıklama isimli oy veya araştırma komisyonu kurulduğu anlamına gelmez.', [('agenda','initiative'),('yeniyol-role','action'),('yeniyol-support','action'),('decision','result')]),
 ('dem','tbmm-28-5-004-dem-19972-gundem','DEM’in 19972 grup numaralı araştırma önergesinin 8 Ekim’de görüşülmesi','DEM Grubu 19972 grup numaralı araştırma önergesinin 8 Ekim birleşiminde ön görüşmeye alınmasını önerdi. Başkan grup önerisinin kabul edilmediğini duyurdu.','TBMM Genel Kurul tam birleşim tutanağı.','task','DEM Parti Grubu, Koçyiğit ve Temelli’nin 21 Eylül 2026 tarihli 19972 grup numaralı fon krizi araştırma önergesinin 8 Ekimde görüşülmesini önerdi; grup adına Kamuran Tanhan konuştu. Başkan kabul edilmediğini duyurdu; Koçyiğit karar yeter sayısı arandığını, başkan ise oyladığını söyledi. Esas numarası ve isimli oy bu kaynaktan çıkarılmadı.', [('dem-agenda','initiative'),('dem-role','action'),('dem-decision','result'),('dem-quorum','result'),('dem-chair','result')])]
def add(kind,**values):pkg['practice_records'].setdefault(kind,[]).append(values)
for key,common,title,context,basis,kind,claim,points in specs:
 event='0406-oct08-'+key+'-event'; finding='0406-oct08-'+key+'-finding'; contribution='0406-oct08-'+key+'-contribution'; candidate='0406-oct08-'+key+'-candidate'; ids=[q(n) for n,_ in points]
 entries.append(dict(kind='finding',values=dict(id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text=claim,provenance='summary',epistemic_type='claim')))
 for n,stage in points:
  pid=q(n); entries.extend([dict(kind='finding_evidence',values=dict(finding_id=finding,passage_id=pid,role='support')),dict(kind='verification',values=dict(finding_id=finding,passage_id=pid,checked_at=now,result='confirmed',reason='TBMM tam birleşim tutanağının ilgili bölümü okundu.'))])
  add('practice_event_evidence',event_id=event,passage_id=pid,supported_point=passages[pid]['section'],stage=stage,concrete_basis='8 Ekim 2026 TBMM tam birleşim tutanağı.',limitation='Gündem kararı araştırma önergesinin esası veya isimli oy değildir.',epistemic_type='claim')
  add('practice_evidence_assessment',event_id=event,passage_id=pid,stage=stage,basis_kind='document')
 entries.append(dict(kind='review',values=dict(id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='İki ayrı gündem önerisi, konuşma, ret ve usul talebi ayrıldı.')))
 add('practice_event',id=event,common_event_key=common,event_at='2026-10-08',date_precision='day',date_unknown_reason=None,scope_context=context,title=title,occurrence_basis=basis)
 add('practice_contribution',id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind=kind,finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='Grup konuşması ve gündem talebi; isimli oy veya araştırma komisyonunun kurulması değildir.')
 add('practice_candidate',id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Önceki yayımlanmış parti söylemiyle eşleştirme araştırması açık.',passage_ids=json.dumps(ids,ensure_ascii=False))
 targets=[('practice_event_evidence',event+'|'+q(n)+'|'+stage,[q(n)],passages[q(n)]['section']) for n,stage in points]
 targets += [('practice_event',event,ids,'Ayrı grup talebi ve gündem sonucu.'),('practice_contribution',contribution,ids,'DEM grup adına kaydedilen katkı.'),('practice_contribution.finding_id',contribution,ids,'Katkı, usul ve sonuç bulgusunun kapsamı.'),('practice_candidate',candidate,ids,'Önceki parti söylemi için araştırma açık.')]
 for typ,ident,refs,description in targets:
  review['practice_source_review'].append(dict(subject_kind=typ,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps([ver]),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps([passages[x]['section'] for x in refs],ensure_ascii=False),supported_claim=description+' '+title,limitations='Gündem oyu, isimli oy ve araştırma komisyonunun kurulması ayrı konulardır.',result='reviewed',reason='TBMM tam birleşim tutanağı ilgili pasajları okundu.'))
add('practice_attempt_v2',id='0406-oct08-floor-reading',scope_id=scope,attempted_at=now,query='8 Ekim 2026 4. birleşim DEM 19972 Yeni Yol 10/4603 grup önerileri',url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/4/Tam/a78ffde7-97e0-4bb8-b6ea-6582538fbefb.html',result='examined',reason='İki ayrı gündem talebi, DEM sözlü katkıları ve karar bölümleri okundu; bütün birleşim okunmadı.',source_version_id=ver)
add('practice_scope_source',scope_id=scope,version_id=ver,inspected_sections=json.dumps([x['section'] for x in passages.values()],ensure_ascii=False),inspected_at=now)
pkg['entries']+=entries; review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
for name,obj in [('oct08-two-events-draft.json',pkg),('oct08-two-events-review-draft.json',review)]:
 path=c/name; path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n'); print(name,hashlib.sha256(path.read_bytes()).hexdigest())
