"""7573 kesin cetvelindeki DEM milletvekili oyları için eklemeli aday."""
import datetime, hashlib, html, json, re
from pathlib import Path
from arsiv import html_source_text

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
d=Path('data/practices'); sha=lambda b: hashlib.sha256(b).hexdigest()
raw=(d/'04-dem.json').read_bytes(); rr=(d/'04-dem-review.json').read_bytes()
assert sha(raw)=='e6d6f44cbf707033d0ce6e5b75029c4b33f75eef6ed9c48be73bcdacbf4a81f9'
assert sha(rr)=='eee25bd692d7fd6e24eb0da4160d28323b5b16af43a2ae810ae1aaae4bdccc54'
pkg,review=json.loads(raw),json.loads(rr); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
source=json.loads(Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-07-checks/pension-floor-final-source-records.json').read_text())['entries']
srcid='0407-floor-iyi-7573-ballot'; prefix='0406-7573-ballot'; entries=[]
for e in source:
 k=e['kind']; v=e['values']; ident=v.get('id',''); version=v.get('version_id','')
 if k=='document' and ident!=srcid: continue
 if k=='document_version' and v['document_id']!=srcid: continue
 if k in ('archive_view','source_attribution') and version!=srcid+'-v1': continue
 if k=='passage' and ident!=srcid+'-tally': continue
 if k not in ('document','document_version','archive_view','source_attribution','passage'): continue
 v=json.loads(json.dumps(v,ensure_ascii=False).replace(srcid,prefix))
 if k=='document': v['party_id']='dem'
 entries.append(dict(kind=k,values=v))
version=next(e['values'] for e in entries if e['kind']=='document_version')
ballot=(d/'sources/dem'/version['original_path']).read_bytes(); assert sha(ballot)==version['sha256']
text=html_source_text(ballot); selected=[]
for row in re.findall(r'<tr>.*?</tr>',text,flags=re.S):
 decoded=html.unescape(row)
 if 'Halkların Eşitlik ve Demokrasi Partisi' not in decoded: continue
 cells=re.findall(r'<td[^>]*>(.*?)</td>',decoded,flags=re.S)
 clean=[re.sub(r'<[^>]+>','',c).strip() for c in cells]
 if len(clean)==9 and clean[6]=='RET': selected.append((clean[1],row))
assert len(selected)==9
for i,(name,exact) in enumerate(selected):
 entries.append(dict(kind='passage',values=dict(id=f'{prefix}-ret-{i+1}',version_id=prefix+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='DEM etiketli milletvekili nihai ret kaydı: '+name,pdf_page_index=None,printed_page=None)))
passages=[f'{prefix}-ret-{i+1}' for i in range(9)]; tally=prefix+'-tally'; qs=passages+[tally]
event='0406-2026-7573-vote'; contribution='0406-2026-7573-contribution'; candidate='0406-2026-7573-unmatched'; finding='0406-2026-7573-f'; scope='practice-5a881b0a216826a2360edc436182d8f5270ed950adef9e13b3f8072eed6e9365'
def add(k,**v): entries.append(dict(kind=k,values=v))
add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='7573 sayılı kanunun tümünün kesin açık oylama cetvelinde DEM etiketli dokuz milletvekilinin nihai oyu ret olarak yer aldı; kanun 245 kabul ve 179 ret ile kabul edildi.',provenance='summary',epistemic_type='claim')
for q in qs:
 add('finding_evidence',finding_id=finding,passage_id=q,role='support'); add('verification',finding_id=finding,passage_id=q,checked_at=now,result='confirmed',reason='TBMM kesin cetvelinde sistem, pusula ve nihai sütunlar karşılaştırıldı.')
add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='İsimli oylar ve kanunun bütünü için sonuç ayrı kaydedildi.')
points=[(q,'action','Milletvekilinin nihai ret oyu','İsimli cetvelde DEM etiketi ve nihai ret satırı.') for q in passages]+[(tally,'result','Kanunun kesin sonucu','Kesin cetvel 245 kabul ve 179 ret gösterir.')]
rec={
'practice_event':[dict(id=event,common_event_key='tbmm-28-4-050-2-3464-7573',event_at='2026-01-23',date_precision='day',date_unknown_reason=None,scope_context='TBMM 28. dönem 4. yasama yılı 50. birleşimin 22 Ocak günü başlayan, gece yarısından sonra süren oturumunda 2/3464 sayılı teklifin tümü',title='7573 sayılı kanunun tümünün açık oylaması',occurrence_basis='TBMM kesin isimli cetvelinde oy zamanları 23 Ocak 2026 olarak görünür.')],
'practice_event_evidence':[dict(event_id=event,passage_id=q,supported_point=point,stage=stage,concrete_basis=basis,limitation='Tüm kanun oyu; belirli madde, tek tek kanun gerekçesi veya uygulama sonucu değildir.',epistemic_type='claim') for q,stage,point,basis in points],
'practice_evidence_assessment':[dict(event_id=event,passage_id=q,stage=stage,basis_kind='document') for q,stage,_,_ in points],
'practice_contribution':[dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='objection',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='Cetvelde DEM etiketli dokuz kişinin bireysel oyu; bütün grubun tek bir irade beyanı veya maddeye ayrı oy değildir.')],
'practice_attempt_v2':[dict(id='0406-7573-ballot-reading',scope_id=scope,attempted_at=now,query='TBMM 2/3464 7573 kesin açık oy cetveli DEM milletvekilleri',url=version['original_url'],result='examined',reason='İsimli satırlarda sistem, pusula ve nihai oy karşılaştırıldı.',source_version_id=version['id'])],
'practice_scope_source':[dict(scope_id=scope,version_id=version['id'],inspected_sections=json.dumps(['Kesin oy toplamı','DEM etiketli isimli oy satırları'],ensure_ascii=False),inspected_at=now)],
'practice_candidate':[dict(id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Kanunun bütünü için bireysel oylar, seçili Faz 3 sosyal hizmet veya gelir söylemine maddeye özgü tutum olarak bağlanamaz; önceki emeklilik söylemi ve diğer araştırmalar açık.',passage_ids=json.dumps(qs,ensure_ascii=False))]}
pkg['entries']+=entries
for k,v in rec.items(): pkg['practice_records'].setdefault(k,[]).extend(v)
sections={e['values']['id']:e['values']['section'] for e in entries if e['kind']=='passage'}
items=[('practice_event_evidence',event+'|'+q+'|'+stage,[q],point) for q,stage,point,_ in points]
items += [('practice_event',event,qs,'Kanunun tümü ve kesin sonuç.'),('practice_contribution',contribution,qs,'Dokuz milletvekilinin nihai ret oyu.'),('practice_contribution.finding_id',contribution,qs,'İsimli oylar ve sonuç ayrı desteklenir.'),('practice_candidate',candidate,qs,'Maddeye özgü söylemle eşleme araştırması açık.')]
for kind,ident,ps,claim in items:
 review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps([version['id']]),passage_ids=json.dumps(ps),inspected_sections=json.dumps(list(dict.fromkeys(sections[q] for q in ps)),ensure_ascii=False),supported_claim=claim,limitations='Oy tüm teklif içindir; maddeye özel oy veya uygulama sonucu değildir.',result='reviewed',reason='TBMM kesin isimli cetveli incelendi: '+claim))
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
for name,obj in [('7573-combined-draft.json',pkg),('7573-combined-review-draft.json',review)]:
 path=p/name; path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n'); print(name,sha(path.read_bytes()))
