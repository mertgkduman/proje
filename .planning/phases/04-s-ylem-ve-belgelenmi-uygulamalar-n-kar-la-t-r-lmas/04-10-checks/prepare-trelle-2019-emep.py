import copy,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
c=Path(__file__).resolve().parent; now=datetime.now(timezone.utc).isoformat(timespec='seconds'); read=lambda p:json.loads(Path(p).read_bytes()); package=read('data/practices/04-emep.json'); review=read('data/practices/04-emep-review.json'); base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json'); inv=read('data/practices/04-inventory.json'); entries=package['entries']; records=package['practice_records']; assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(85,79,0)
case='0410-trelle-2019'; topic='sendika-grev'; event=case+'-event'; relation=case+'-relation'; statement=case+'-statement'; sources=read(c/'trelle-2019-emep-source-draft.json')['entries']; entries.extend(sources); passages={e['values']['id']:e['values'] for e in sources if e['kind']=='passage'}; versions={e['values']['id']:e['values'] for e in sources if e['kind']=='document_version'}
def add(table,**v): records[table].append(v)
def insert(table,**v): entries.append(dict(kind=table,values=v))
def finding(suffix,text,provenance,refs,heading,pair):
 fid=case+'-'+suffix; insert('finding',id=fid,party_id='emep',heading=heading,pair_id=pair,text=text,provenance=provenance,epistemic_type='claim'); insert('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Önceki ve sonraki gazete haberleri ayrı okundu.')
 for pid in refs: insert('finding_evidence',finding_id=fid,passage_id=pid,role='support'); insert('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün haber pasajı incelendi.')
 return fid
q=case+'-call-quote'; specific=case+'-call-specific'; plan=case+'-call-plan'; meeting=case+'-visit-meeting'; role=case+'-visit-role'
limit='30 Aralık haberindeki EMEP Gebze açıklamasının kendi günü belirtilmez. Ziyaret 31 Aralık 2019–1 Ocak 2020 yılbaşı gecesindedir; kesin başlangıç günü ve saati doğrulanmadı. 1 Ocak tarihli sonraki haberin erişilen sürümü 2 Ocakta güncellenmiştir. 22 Ocaktaki sendikal sözleşme ziyaretten ayrı işlemdir; partiye sözleşme yetkisi veya sonuca nedensel katkı atfedilmez.'
summary=finding('call-summary','Evrensel’in 30 Aralık 2019 haberine göre EMEP Gebze İlçe Örgütü, yeni yılda Trelleborg grevindeki işçilerle birlikte olma çağrısı yaptı.','summary',[q,specific,plan],'Sendika ve grev',statement)
quote=finding('call-quote-finding',passages[q]['exact'],'quote',[q],'Sendika ve grev',statement)
result=finding('result','Evrensel’in yılbaşı sonrası haberine göre Emek Partisi yeni yıla grevdeki Trelleborg işçileriyle girdi; Kocaeli İl Başkanı Arzu Erkan açıklama yaptı.','summary',[meeting,role],'Belgelenmiş uygulamalar',case+'-result')
explanation=finding('comparison','30 Aralık tarihli haber EMEP’in Trelleborg işçileriyle yılbaşını geçirme çağrısını, yılbaşı sonrası haber ise partinin yeni yıla işçilerle girdiğini aktarır. Çağrı ve gerçekleşme farklı haberlerden aktarılır.','summary',[q,specific,plan,meeting,role],'Belgelenmiş uygulamalar',case+'-comparison')
institution=finding('institution','Evrensel haberine göre EMEP yeni yıla Trelleborg işçileriyle girdi ve il başkanı Arzu Erkan konuştu.','summary',[meeting,role],'Belgelenmiş uygulamalar',case+'-institution')
for lane in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='emep' and x['topic_id']==topic and x['research_kind']==lane); sid=cell['cell_id']
 if not any(x['id']==sid for x in records['practice_scope_v2']): add('practice_scope_v2',id=sid,party_id='emep',topic_id=topic,taxonomy_version=4,period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=lane,boundary_reason='Trelleborg yılbaşı çağrısı ve ziyareti incelendi; kapsam açık.')
 if lane=='statement': ss=sid
 else: es=sid
add('practice_statement',id=statement,party_id='emep',topic_id=topic,taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at=None,date_precision='unknown',version_id=case+'-call-v1',period_basis='30 Aralık 2019 tarihli gazete haberi çağrıyı yılbaşı öncesinde aktarır.',uncertainty_reason='Parti açıklamasının kendi günü bilinmiyor; haber tarihinden geç olamaz.',comparison_row_id='04-03-v3-0309-emep-program-006-1-row')
add('practice_event',id=event,common_event_key='trelleborg-2019-2020-emep-yilbasi-ziyareti',event_at=None,date_precision='unknown',date_unknown_reason='31 Aralık 2019 akşamından 1 Ocak 2020’ye uzanan yılbaşı gecesi; kesin başlangıç günü ve saati doğrulanmadı.',title='EMEP’in Trelleborg grev çadırında yılbaşı ziyareti',scope_context='31 Aralık 2019–1 Ocak 2020 yılbaşı gecesinde Trelleborg grev çadırında EMEP ve işçilerin buluşması.',occurrence_basis='1 Ocak 2020 tarihli, 2 Ocakta güncellenmiş Evrensel haberi EMEP’in yeni yıla Trelleborg işçileriyle girdiğini bildiriyor.')
for pid,point in [(meeting,'Gazete EMEP’in yeni yıla Trelleborg işçileriyle girdiğini bildirir.'),(role,'Gazete Kocaeli il başkanı Arzu Erkan’ın sözlerini aktarır.')]:
 add('practice_event_evidence',event_id=event,passage_id=pid,stage='action',supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'); add('practice_evidence_assessment',event_id=event,passage_id=pid,stage='action',basis_kind='document')
add('practice_event_evidence',event_id=event,passage_id=meeting,stage='result',supported_point='Gazete yılbaşının işçilerle birlikte karşılandığını bildirir.',concrete_basis=passages[meeting]['section'],limitation=limit,epistemic_type='claim'); add('practice_evidence_assessment',event_id=event,passage_id=meeting,stage='result',basis_kind='document')
add('practice_relation',id=relation,statement_id=statement,event_id=event,party_id='emep',topic_id=topic,scope_id=es,comparability_reason='Önceki haberdeki belirli Trelleborg yılbaşı dayanışma çağrısı ile aynı yılbaşı buluşmasına ilişkin sonraki haber karşılaştırılır.',target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,temporal_context='30 Aralık haberi çağrıyı aktarır; yılbaşı buluşması 31 Aralık–1 Ocak gecesindedir; sonraki haber 1 Ocak tarihlidir.',authority_context='Çağrı EMEP Gebze ilçe örgütüne, sonradan bildirilen katılım EMEP’e ve sözler Kocaeli il başkanı Arzu Erkan’a gazete tarafından atfedilir.',uncertainty_reason=limit)
add('practice_candidate',id=case+'-candidate',scope_id=es,event_id=event,relation_id=relation,state='eligible',reason='Özgül çağrı ve aynı yılbaşı ziyareti öncesi ve sonrası ayrı haberlerde bildirildi.',passage_ids=json.dumps([q,specific,plan,meeting,role])); add('practice_contribution',id=case+'-contribution',event_id=event,party_id='emep',actor_id='0410-emep-institution',contribution_kind='support',finding_id=institution,authority_passage_id=None,membership_passage_id=None,responsibility_limit=limit)
for ver,v in versions.items():
 for scope in ((ss,es) if '-call-' in ver else (es,)):
  sections=sorted({p['section'] for p in passages.values() if p['version_id']==ver}); aid=ver+'-reading-'+('statement' if scope==ss else 'event'); add('practice_scope_source',scope_id=scope,version_id=ver,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now); add('practice_attempt_v2',id=aid,scope_id=scope,attempted_at=now,query=v['original_url'],url=v['original_url'],result='examined',reason='Trelleborg yılbaşı çağrısı veya sonrası haber okundu.',source_version_id=ver); add('practice_lead',id='lead-'+aid,scope_id=scope,url=v['original_url'],state='examined',relevance_reason='Yılbaşı grev dayanışması.',attempt_ids=json.dumps([aid]))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items(): data.setdefault(table,[]).extend(r for r in rows if r not in data[table])
rules.validate_practices(data); targets=rules.practice_review_package_targets(data,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep'); allp={p['id']:p for p in data['passage']}; reviews=list(review['practice_source_review']); old={(r['subject_kind'],r['subject_id']) for r in reviews}; assert old<=targets.keys()
for (kind,identity),(ids,_) in sorted(targets.items()):
 if (kind,identity) in old: continue
 ps=[allp[i] for i in sorted(ids)]; assert ps
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in ps})),passage_ids=json.dumps([p['id'] for p in ps]),inspected_sections=json.dumps(sorted({p['section'] for p in ps}),ensure_ascii=False),supported_claim='Evrensel’in ilgili pasajları, yılbaşı dayanışma çağrısını veya gerçekleştiği bildirilen buluşmayı ve belirtilen parti temsilcisini aktarır.',limitations=limit,result='reviewed',reason=kind+' / '+identity+' için özgün haber pasajı incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets)); refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs; review['practice_source_review']=reviews; review['source_review_refs']=refs
for name,obj in [('trelle-2019-emep-draft.json',package),('trelle-2019-emep-review-draft.json',review)]:
 with (c/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('TRELLE_SEMANTIC_OK',len(records['practice_event']),len(records['practice_relation']),len(reviews))
