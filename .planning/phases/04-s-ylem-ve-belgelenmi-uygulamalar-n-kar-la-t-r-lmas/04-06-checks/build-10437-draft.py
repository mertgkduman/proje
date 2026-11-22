"""İYİ 10/437 ön görüşme önerisine DEM katkısı: eşlemesi açık aday."""
import datetime, hashlib, json
from pathlib import Path
from arsiv import html_source_text

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
d=Path('data/practices'); source=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-07-checks/aged-source-records.json')
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(d/'04-dem.json').read_bytes(); rr=(d/'04-dem-review.json').read_bytes()
assert sha(raw)=='72d9d9215ca7a3765e776852888efbca672a947f2defbc3f50c21aa1ffa3ba4e'
assert sha(rr)=='6f8b110c4acb7d2b5c0a98d388d66344dec103b64586ce545620119ff9bf7f5e'
pkg,review=json.loads(raw),json.loads(rr); now=datetime.datetime.now(datetime.timezone.utc).isoformat(); original=json.loads(source.read_text())['entries']
docs={'0407-aged-iyi-437','0407-aged-pension-2024-session','0407-aged-pension-2024-summary'}
passages={'0407-aged-iyi-437-id','0407-aged-iyi-437-submitted','0407-aged-iyi-437-first','0407-aged-pension-2024-session-proposal','0407-aged-pension-2024-session-dem-role','0407-aged-pension-2024-session-dem-support','0407-aged-pension-2024-summary-topic','0407-aged-pension-2024-summary-result'}
entries=[]
for e in original:
 k=e['kind'];v=e['values']; ident=v.get('id',''); version=v.get('version_id','')
 if k=='document' and ident not in docs:continue
 if k=='document_version' and v['document_id'] not in docs:continue
 if k in ('source_attribution','archive_view') and not any(version==x+'-v1' for x in docs):continue
 if k=='passage' and ident not in passages:continue
 if k not in ('document','document_version','source_attribution','archive_view','passage'):continue
 v=json.loads(json.dumps(v,ensure_ascii=False).replace('0407-aged','0406-aged'))
 if k=='document':v['party_id']='dem'
 if k=='document_version':
  assert sha((d/'sources/dem'/v['original_path']).read_bytes())==v['sha256']
 entries.append(dict(kind=k,values=v))
passages={x.replace('0407-aged','0406-aged') for x in passages}
for e in entries:
 if e['kind']=='passage':
  v=e['values'];version=next(x['values'] for x in entries if x['kind']=='document_version' and x['values']['id']==v['version_id'])
  assert v['exact'] in html_source_text((d/'sources/dem'/version['original_path']).read_bytes()),v['id']
event='0406-2024-10437-gundem'; contribution='0406-2024-10437-contribution'; candidate='0406-2024-10437-unmatched'; scope='practice-5a881b0a216826a2360edc436182d8f5270ed950adef9e13b3f8072eed6e9365'; finding='0406-2024-10437-f'
pt=lambda s:'0406-aged-'+s
points=[(pt('iyi-437-id'),'initiative','10/437 esas numarası','TBMM ayrıntı kaydı esas numarasını gösterir.'),(pt('iyi-437-submitted'),'initiative','Önergenin gelişi','Önergenin geliş günü 12 Ekim 2023 olarak kayıtlıdır.'),(pt('pension-2024-session-proposal'),'initiative','Grup takvim önerisi','TBMM tutanağı yaşlıların sorunlarına ilişkin ön görüşme önerisini gösterir.'),(pt('pension-2024-session-dem-role'),'action','DEM grup konuşmacısı','Tutanak Kaya’nın DEM grubu adına söz aldığını gösterir.'),(pt('pension-2024-session-dem-support'),'action','DEM grup desteği','Kaya bakımevlerinin iyileştirilmesi için önergeye destek beyan eder.'),(pt('pension-2024-summary-result'),'result','Takvim önerisi kabul edilmedi','Özet, ön görüşmenin o gün yapılması önerisinin kabul edilmediğini belirtir.')]
def add(k,**v):entries.append(dict(kind=k,values=v))
add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='Adalet Kaya, DEM Grubu adına yaşlı bakımevleri hizmetlerinin iyileştirilmesi için araştırma önergesini destekledi; ön görüşmenin o gün yapılması önerisi kabul edilmedi.',provenance='summary',epistemic_type='claim')
for q,_,_,_ in points:
 add('finding_evidence',finding_id=finding,passage_id=q,role='support');add('verification',finding_id=finding,passage_id=q,checked_at=now,result='confirmed',reason='Özgün TBMM detay kaydı, birleşim ve özet bağlamıyla okundu.')
add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Grup beyanı, takvim oylaması ve hizmet sonucu ayrı değerlendirildi.')
versions={e['values']['id']:e['values']['version_id'] for e in entries if e['kind']=='passage'}
sections={e['values']['id']:e['values']['section'] for e in entries if e['kind']=='passage'}
rec={
'practice_scope_v2':[dict(id=scope,party_id='dem',topic_id='sosyal-hizmetler-v2',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='Yalnız 17 Ocak 2024 yaşlı bakımı ön görüşme takvimi; sosyal hizmetler kapsamı araştırması sürüyor.')],
'practice_event':[dict(id=event,common_event_key='tbmm-28-2-050-10-437-gundem',event_at='2024-01-17',date_precision='day',date_unknown_reason=None,scope_context='TBMM 28. dönem 2. yasama yılı 50. birleşimde İYİ 10/437 araştırma önergesinin ön görüşme takvimi',title='Yaşlı bakımı araştırmasının ön görüşme takvimi',occurrence_basis='İmzalı önerge, TBMM detay ve Genel Kurul tutanağı ile özetindeki takvim önerisi.')],
'practice_event_evidence':[dict(event_id=event,passage_id=q,supported_point=point,stage=stage,concrete_basis=basis,limitation='Grup destek beyanı isimli oy değildir; takvim reddi araştırmanın nihai sonucu veya bakım hizmetinin değişimi değildir.',epistemic_type='claim') for q,stage,point,basis in points],
'practice_evidence_assessment':[dict(event_id=event,passage_id=q,stage=stage,basis_kind='document') for q,stage,_,_ in points],
'practice_contribution':[dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='support',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM grubu adına sözlü destek; isimli oy veya fiilî bakım sonucu değil.')],
'practice_attempt_v2':[dict(id='0406-10437-reading',scope_id=scope,attempted_at=now,query='TBMM 28/2/50 İYİ 10/437 yaşlı bakım ön görüşmesi ve DEM katkısı',url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/2/50/Tam/8eacee7b-6d28-4728-ae25-74885298f608.html',result='examined',reason='Kaya’nın grup açıklaması ve ön görüşme takvimi okundu; kapsam açık.',source_version_id=pt('pension-2024-session-v1')),dict(id='0406-10437-detail-reading',scope_id=scope,attempted_at=now,query='TBMM 10/437 araştırma önergesi künye ve esas numarası',url='https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/1de74186-02dd-4030-a545-018b3d649158',result='examined',reason='Önerge esas numarası ve geliş günü künye kaydından okundu.',source_version_id=pt('iyi-437-v1')),dict(id='0406-10437-summary-reading',scope_id=scope,attempted_at=now,query='TBMM 28/2/50 birleşim özeti İYİ 10/437 gündem önerisi sonucu',url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/2/50/Ozet/daf93bf0-106b-4149-93f4-b97383f560c0.html',result='examined',reason='Ön görüşme takviminin aynı gün kabul edilmediği özette okundu.',source_version_id=pt('pension-2024-summary-v1'))],
'practice_scope_source':[dict(scope_id=scope,version_id=ver,inspected_sections=json.dumps(ss,ensure_ascii=False),inspected_at=now) for ver,ss in [(pt('iyi-437-v1'),['Önerge esas numarası ve geliş günü']),(pt('pension-2024-session-v1'),['İYİ grup önerisi ve DEM grup konuşması']),(pt('pension-2024-summary-v1'),['Takvim önerisinin sonucu'])]],
'practice_candidate':[dict(id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Seçili Faz 3 bulgularında yaşlı bakımevleri hedefi bulunmadı; ilgisiz yaşlı mahpusların tahliyesi hedefi bu öneriye bağlanmadı. Önceki bağımsız parti programı ve başka söylemler araştırılacak.',passage_ids=json.dumps([q for q,_,_,_ in points],ensure_ascii=False))]}
pkg['entries']+=entries
for k,v in rec.items():pkg['practice_records'].setdefault(k,[]).extend(v)
qs=[q for q,_,_,_ in points]; items=[('practice_event_evidence',event+'|'+q+'|'+stage,[q],point) for q,stage,point,_ in points]
items += [('practice_event',event,qs,'Önerge, destek ve takvim sonucu ayrı.'),('practice_contribution',contribution,qs,'Kaya grup adına bakım önergesine destek verdi.'),('practice_contribution.finding_id',contribution,qs,'Katkı ve takvim sonucu ayrı kaynaklarla desteklenir.'),('practice_candidate',candidate,qs,'Seçili söylemle eşleme bulunmadı; kapsam araştırması açık.')]
for kind,ident,ps,claim in items:
 review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(versions[q] for q in ps)),ensure_ascii=False),passage_ids=json.dumps(ps,ensure_ascii=False),inspected_sections=json.dumps(list(dict.fromkeys(sections[q] for q in ps)),ensure_ascii=False),supported_claim=claim,limitations='Gündeme alma reddi araştırma önergesinin nihai reddi değildir; DEM konuşması isimli oy ve bakım sonucu değildir.',result='reviewed',reason='Özgün TBMM kaynakları ilgili bağlamda okundu: '+claim))
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
assert len({(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']})==len(review['practice_source_review'])
for name,obj in [('10437-combined-draft.json',pkg),('10437-combined-review-draft.json',review)]:
 path=p/name;path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(path.read_bytes()))
