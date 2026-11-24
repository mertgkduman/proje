import copy,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
c=Path(__file__).resolve().parent; now=datetime.now(timezone.utc).isoformat(timespec='seconds'); read=lambda p:json.loads(Path(p).read_bytes())
package=read('data/practices/04-emep.json'); review=read('data/practices/04-emep-review.json'); base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json'); inv=read('data/practices/04-inventory.json'); entries=package['entries']; records=package['practice_records']
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(79,76,0)
case='0410-law-7527-emep'; topic='doga-ekoloji'; event=case+'-event'; relation=case+'-relation'; statement=case+'-statement'; sources=read(c/'law-7527-emep-source-draft-v2.json')['entries']; entries.extend(sources); passages={e['values']['id']:e['values'] for e in sources if e['kind']=='passage'}; versions={e['values']['id']:e['values'] for e in sources if e['kind']=='document_version'}
def add(table,**v): records[table].append(v)
def insert(table,**v): entries.append({'kind':table,'values':v})
def finding(suffix,text,provenance,refs,heading,pair):
 fid=case+'-'+suffix; insert('finding',id=fid,party_id='emep',heading=heading,pair_id=pair,text=text,provenance=provenance,epistemic_type='claim'); insert('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='EMEP yayımı ve TBMM kaynakları, beyan, kişisel oy ve kabul ayrılarak okundu.')
 for pid in refs: insert('finding_evidence',finding_id=fid,passage_id=pid,role='support'); insert('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün kaynak pasajı ve atıf sınırı incelendi.')
 return fid
pid=lambda s:case+'-'+s+'-p'; context=pid('party-context'); call=pid('party-withdraw'); adoption=pid('floor-adoption'); chair=pid('floor-chair'); tally=pid('floor-tally'); personal=pid('floor-personal'); correction=pid('correction-request'); number=pid('register-number'); date=pid('register-date'); publication=pid('register-publication'); issue=pid('register-issue')
limit='EMEP yayımı milletvekili Sevda Karacanın açıklamasını aktarır; kesin cetveldeki ret kendisinin kişisel oyudur. TBMM kabulü, kişisel oy ve sonraki uygulama ayrıdır; parti oylaması veya kişisel sonuç çıkarılmaz. Başkan 275 kabul açıklamıştır; kesin cetvel 273 kabul ve iki mükerrer gösterir. Aydoğdunun sonraki kabul niyeti talebi bir yeniden sayım ya da Karaca oyunun düzeltmesi değildir. Sicildeki yayım bilgisi Resmî Gazete özgün nüshası değildir.'
summary=finding('call-summary','EMEP 18 Temmuz 2024’te yayımladığı haberde milletvekili Sevda Karaca’nın hayvanların korunması yasa teklifi hakkındaki eleştirisini ve teklifin geri alınması çağrısını aktardı.','summary',[context,call],'Doğa ve ekoloji',statement)
quote=finding('call-quote',passages[call]['exact'],'quote',[call],'Doğa ve ekoloji',statement)
result=finding('result','TBMM 2/2275 sayılı teklifi 30 Temmuz 2024’te 7527 sayılı kanun olarak kabul etti. Kesin açık oy cetvelinde Sevda Karaca Demir’in kişisel oyu ret olarak yer aldı. TBMM sicili Resmî Gazete yayımını 2 Ağustos olarak kaydeder.','summary',[adoption,personal,number,date,publication],'Belgelenmiş uygulamalar',case+'-result')
explanation=finding('comparison','EMEP’in 18 Temmuzdaki yayımı Karaca’nın hayvanlarla ilgili teklifi geri alma çağrısını aktarır. TBMM 30 Temmuzda 2/2275 teklifini kabul ederek 7527 sayılı kanunu çıkardı; kesin cetvel Karaca Demir’in kişisel ret oyunu gösterir. Sicilde yayım günü 2 Ağustostur. Başkanın 275 kabul açıklaması ile kesin cetveldeki 273 kabul ve iki mükerrer ayrı kaydedilir. 15 Ağustostaki Aydoğdu düzeltme talebi Karaca’nın oyuna ilişkin değildir.','summary',[context,call,adoption,personal,number,date,publication,chair,tally,correction],'Belgelenmiş uygulamalar',case+'-comparison')
for lane in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='emep' and x['topic_id']==topic and x['research_kind']==lane); sid=cell['cell_id']
 if not any(x['id']==sid for x in records['practice_scope_v2']): add('practice_scope_v2',id=sid,party_id='emep',topic_id=topic,taxonomy_version=4,period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=lane,boundary_reason='Hayvan koruma teklifi doğa ve ekoloji kapsamı içinde incelendi; araştırma açık.')
 if lane=='statement': ss=sid
 else: es=sid
add('practice_statement',id=statement,party_id='emep',topic_id=topic,taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at='2024-07-18',date_precision='day',version_id=case+'-party-v1',period_basis='18 Temmuz 2024 tarihli EMEP yayımı; program satırı başka bir belgedir ve bununla özdeşleştirilmez.',uncertainty_reason='Komisyon konuşması ve çağrı Sevda Karacaya atfedilir; EMEP adına kolektif oy veya karar olarak gösterilmez.',comparison_row_id='04-03-v3-0309-emep-program-041-0-row')
add('practice_event',id=event,common_event_key='tbmm-28-2-112-2-2275-law-7527',event_at='2024-07-30',date_precision='day',date_unknown_reason=None,scope_context='28. Dönem 2. Yasama Yılı 112. birleşim, 2/2275 ve 160 sıra sayılı teklif.',title='7527 sayılı Hayvanları Koruma Kanunu değişikliğinin kabulü',occurrence_basis='TBMM Genel Kurul tutanağı, kesin açık oy cetveli ve kanun sicili.')
evidence={'floor-adoption':('result','TBMM başkanı teklifin kabul edilip kanunlaştığını açıkladı.'),'floor-chair':('result','Başkan oturumda 275 kabul, 224 ret, bir çekimser bildirdi.'),'floor-tally':('result','Kesin cetvel 03.46, 273 kabul, 224 ret, bir çekimser ve iki mükerrer gösterir.'),'floor-personal':('action','Kesin cetvel Sevda Karaca Demirin kişisel oyunu EMEP / ret gösterir.'),'correction-request':('result','15 Ağustosta Cengiz Aydoğdu, kullanamadığı oyunun kabul yönünde kayda geçirilmesini istedi.'),'register-number':('result','TBMM sicilinde kanun numarası 7527dir.'),'register-date':('result','Sicil kabul tarihini 30 Temmuz 2024 olarak verir.'),'register-publication':('result','Sicil Resmî Gazete tarihini 2 Ağustos 2024 verir.'),'register-issue':('result','Sicil Resmî Gazete sayısını 32620 verir.')}
for key,(stage,point) in evidence.items():
 p=pid(key); add('practice_event_evidence',event_id=event,passage_id=p,stage=stage,supported_point=point,concrete_basis=passages[p]['section'],limitation=limit,epistemic_type='claim'); add('practice_evidence_assessment',event_id=event,passage_id=p,stage=stage,basis_kind='document')
add('practice_relation',id=relation,statement_id=statement,event_id=event,party_id='emep',topic_id=topic,scope_id=es,comparability_reason='EMEP yayımının aktardığı Karaca geri alma çağrısı ile aynı hayvan koruma teklifinin Genel Kurul kabulü ve kesin cetvelde Karacanın kişisel oyu karşılaştırılır.',target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,temporal_context='18 Temmuz EMEP yayımı, 29 Temmuz açılan birleşimde 30 Temmuz kabul, 2 Ağustos sicilde yayım, 15 Ağustos başka milletvekilinin düzeltme talebi.',authority_context='Beyan ve ret oyu Sevda Karacaya, teklifin kabulü TBMMye aittir; parti adına kolektif oy veya karar yetkisi atfedilmez.',uncertainty_reason=limit)
add('practice_candidate',id=case+'-candidate',scope_id=es,event_id=event,relation_id=relation,state='eligible',reason='Dönemsel beyan, aynı teklifin kabulü ve konuşmacının kişisel oyu ayrı özgün pasajlarla desteklenmiştir.',passage_ids=json.dumps([adoption,personal,number,date]))
for ver,v in versions.items():
 role=ver[len(case)+1:-3]; scopes=(ss,es) if role=='party' else (es,); sections=sorted({p['section'] for p in passages.values() if p['version_id']==ver})
 for scope in scopes:
  aid=ver+('-statement-reading' if scope==ss else '-event-reading'); add('practice_scope_source',scope_id=scope,version_id=ver,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now); add('practice_attempt_v2',id=aid,scope_id=scope,attempted_at=now,query=v['original_url'],url=v['original_url'],result='examined',reason='EMEP açıklaması veya TBMM tutanak ve sicili incelendi.',source_version_id=ver); add('practice_lead',id='lead-'+aid,scope_id=scope,url=v['original_url'],state='examined',relevance_reason='7527 ve 2/2275 hakkında çağrı, kabul, oy veya yayın evresi.',attempt_ids=json.dumps([aid]))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items(): data.setdefault(table,[]).extend(r for r in rows if r not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep'); allp={p['id']:p for p in data['passage']}; reviews=list(review['practice_source_review']); old={(r['subject_kind'],r['subject_id']) for r in reviews}; assert old<=targets.keys()
for (kind,identity),(ids,_) in sorted(targets.items()):
 if (kind,identity) in old: continue
 ps=[allp[i] for i in sorted(ids)]; claims=[evidence[k][1] for k in evidence if pid(k) in ids]
 if context in ids: claims.append('EMEP yayımı Karacanın hayvan koruma teklifi hakkındaki komisyon açıklamasını aktarır.')
 if call in ids: claims.append('Yayım Karacanın teklifi geri alma çağrısını aktarır.')
 assert claims,(kind,identity,ids)
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in ps})),passage_ids=json.dumps([p['id'] for p in ps]),inspected_sections=json.dumps(sorted({p['section'] for p in ps}),ensure_ascii=False),supported_claim=' '.join(claims),limitations=limit,result='reviewed',reason=kind+' / '+identity+' için özgün kaynak incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets)); refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs; review['practice_source_review']=reviews; review['source_review_refs']=refs
for name,obj in [('law-7527-emep-draft-v2.json',package),('law-7527-emep-review-draft-v2.json',review)]:
 with (c/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('LAW7527_EMEP_SEMANTIC_OK',len(reviews),len(records['practice_event']),len(records['practice_relation']))
