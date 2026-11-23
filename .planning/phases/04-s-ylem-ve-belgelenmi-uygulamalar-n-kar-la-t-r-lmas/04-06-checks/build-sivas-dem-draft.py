"""58 olaylı adaydan sonra iki ayrı 2 Temmuz Sivas gündemi için aday."""
import datetime, hashlib, json
from pathlib import Path
from uygulamalar import practice_review_targets, validate_practice_source_review

c = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
base, review = c/'iklim-floor-motions-dem-draft.json', c/'iklim-floor-motions-dem-review-draft.json'
assert sha(base)=='9cf37562ff02b983dd28a457cd6426168dc9de8f98b06e33ab2dab453b951f56'
assert sha(review)=='f98256dfcb690a39fe179024efdbb6ad2bf31a4e6424658f5cd951b346534d33'
pkg, rev = json.loads(base.read_text()), json.loads(review.read_text())
entries = json.loads((c/'sivas-2880-2883-source-records.json').read_text())['entries']
passages = {x['values']['id']:x['values'] for x in entries if x['kind']=='passage'}
versions = {x['values']['id']:x['values'] for x in entries if x['kind']=='document_version'}
floor = next(e['values'] for e in pkg['entries'] if e['kind']=='document_version' and e['values']['id']=='0406-iklim-final-floor-v1')
versions[floor['id']]=floor
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
scope = 'practice-32598cee77548f2dce224908e63dc9005f9de70be0fff59b0b4990064ad650ae'
new = {k:[] for k in ('practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_candidate','practice_scope_v2','practice_scope_source','practice_attempt_v2')}
def add(kind, **v): new[kind].append(v)
add('practice_scope_v2', id=scope, party_id='dem', topic_id='inanc-mezhep-esitligi', taxonomy_version=4, period_start='2012-11-30', cutoff_at='2026-11-10T14:38:46.154751+00:00', research_kind='event', boundary_reason='Yalnız 2 Temmuz 2025 iki ayrı Sivas araştırması gündemi ve grup konuşmaları; inanç ve mezhep eşitliği kapsamı araştırması sürüyor.')
specs = [
 ('2880','DEM Parti Grubu','10/2880 Sivas araştırmasının ön görüşme talebinin reddi','DEM Parti Grubu, Gülüstan Kılıç Koçyiğit ve Sezai Temelli’nin Sivas katliamına ilişkin 10/2880 araştırma önergesinin ön görüşmesinin 2 Temmuz 2025 birleşiminde yapılmasını istedi. İlk oylamada karar yeter sayısı sağlanamadı; Genel Kurul ikinci oylamada bu gündem talebini reddetti.', '2 Temmuz 2025 Genel Kurulunda DEM Parti Grubu adına Onur Düşünmez Sivas katliamının araştırılmasını savundu. DEM Grup Başkanvekilleri Gülüstan Kılıç Koçyiğit ve Sezai Temelli’nin 10/2880 önergesinin aynı gün ön görüşülmesi talebi, ilk oylamada karar yeter sayısına ulaşılamamasının ardından ikinci oylamada reddedildi. Esas araştırma kaydı Gündemde idi; bu gündem kararı esas dosya sonucundan ve isimli oydan ayrıdır.'),
 ('2883','CHP Grubu','10/2883 Sivas araştırmasının ön görüşme talebinin reddi','CHP Grubu, Ali Mahir Başarır’ın Sivas katliamına ilişkin 10/2883 araştırma önergesinin ön görüşmesinin 2 Temmuz 2025 birleşiminde yapılmasını istedi. Genel Kurul bu gündem talebini reddetti.', '2 Temmuz 2025 Genel Kurulunda CHP’nin 10/2883 araştırma önergesinin ön görüşme talebi üzerine DEM Parti Grubu adına Sevilay Çelenk inançlara ve dünya görüşlerine saygıdan söz etti. Genel Kurul gündem talebini reddetti; esas araştırma kaydı Gündemde idi. Konuşmadan açık destek veya isimli oy çıkarılamaz.')]
for num,group,title,context,finding_text in specs:
 q=lambda x:'0406-sivas-'+num+'-'+x
 event,finding,contribution,candidate=(q(x) for x in ('event','finding','contribution','candidate'))
 points=[('signed-number','initiative'),('register-number','initiative'),('register-date','initiative'),('register-status','result'),('floor-call','initiative'),('floor-role','action'),('floor-speech','action')]
 if num=='2880': points.append(('floor-no-quorum','result'))
 points.append(('floor-retry','result'))
 ids=[q(n) for n,_ in points]
 add('practice_event',id=event,common_event_key='tbmm-28-3-104-10-'+num+'-gundem',event_at='2025-07-02',date_precision='day',date_unknown_reason=None,title=title,scope_context=context,occurrence_basis='TBMM 28. Dönem 3. Yasama Yılı 104. Birleşim tam tutanağı, imzalı 10/'+num+' önergesi ve TBMM esas kaydı.')
 entries.append(dict(kind='finding',values=dict(id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text=finding_text,provenance='summary',epistemic_type='claim')))
 for name,stage in points:
  pid=q(name); p=passages[pid]
  entries.extend([dict(kind='finding_evidence',values=dict(finding_id=finding,passage_id=pid,role='support')),dict(kind='verification',values=dict(finding_id=finding,passage_id=pid,checked_at=now,result='confirmed',reason='Sicil, imzalı belgenin tam görsel okuması ve tutanak incelendi.'))])
  add('practice_event_evidence',event_id=event,passage_id=pid,supported_point=p['section'],stage=stage,concrete_basis='TBMM esas dosyası ve 104. birleşim tutanağı.',limitation='Gündem kararı, esas araştırmanın sonucu ve isimli oy ayrıdır.',epistemic_type='claim')
  add('practice_evidence_assessment',event_id=event,passage_id=pid,stage=stage,basis_kind='document')
 entries.append(dict(kind='review',values=dict(id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='İki ayrı gündem, grup sıfatı ve oylama sonucu incelendi.')))
 add('practice_contribution',id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='task' if num=='2880' else 'unknown',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM grubu adına '+('önerge ve konuşma' if num=='2880' else 'konuşma; açık destek çıkarılmadı')+'; kişisel oy ve esas dosyanın sonucu çıkarılmaz.')
 add('practice_candidate',id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='İnanç eşitliği konusunda önceki bağımsız parti söylemi ve dönemsel ilişki araştırması açık; gündem kararı esas dosyanın sonucu değildir.',passage_ids=json.dumps(ids,ensure_ascii=False))
 for vid in dict.fromkeys(passages[i]['version_id'] for i in ids):
  refs=[i for i in ids if passages[i]['version_id']==vid]
  existing=next((x for x in new['practice_scope_source'] if x['version_id']==vid),None)
  sections=[passages[i]['section'] for i in refs]
  if existing: existing['inspected_sections']=json.dumps(list(dict.fromkeys(json.loads(existing['inspected_sections'])+sections)),ensure_ascii=False)
  else: add('practice_scope_source',scope_id=scope,version_id=vid,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now)
  add('practice_attempt_v2',id=q(vid+'-reading'),scope_id=scope,attempted_at=now,query='2 Temmuz 2025 '+num+' Sivas grup gündemi',url=versions[vid]['original_url'],result='examined',reason='İmzalı önergenin tüm sayfaları görsel, sicil ve tutanak okundu.',source_version_id=vid)
pkg['entries']+=entries
for k,vals in new.items(): pkg['practice_records'].setdefault(k,[]).extend(vals)
data=dict(pkg['practice_records'])
for x in pkg['entries']: data.setdefault(x['kind'],[]).append(x['values'])
selection={k:new[k] for k in ('practice_event','practice_event_evidence','practice_contribution','practice_candidate')}
targets=practice_review_targets(data,selection); allp={x['id']:x for x in data['passage']}; reviews=[]
for (typ,ident),(refs,_) in targets.items():
 refs=sorted(refs); reviews.append(dict(subject_kind=typ,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(allp[x]['version_id'] for x in refs)),ensure_ascii=False),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps(list(dict.fromkeys(allp[x]['section'] for x in refs)),ensure_ascii=False),supported_claim='TBMM Sivas esas kaydı ve ayrı gündem işlemi: '+typ+' / '+ident,limitations='Esas dosya sonucu, gündem kararı ve isimli oy ayrı; CHP gündemindeki DEM konuşması açık destek değildir.',result='reviewed',reason='İlgili kaynaklar ve ayrı oylama süreci okundu.'))
validate_practice_source_review(data,reviews,selection=selection)
rev['practice_source_review']+=reviews
rev['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in rev['practice_source_review']]
for name,obj in [('sivas-two-dem-draft.json',pkg),('sivas-two-dem-review-draft.json',rev)]:
 path=c/name;path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(name,sha(path))
print('SIVAS_TARGET_REVIEW_PASS',len(targets))
