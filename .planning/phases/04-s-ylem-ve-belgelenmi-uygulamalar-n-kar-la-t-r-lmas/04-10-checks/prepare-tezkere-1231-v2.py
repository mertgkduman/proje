import copy, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
import uygulamalar as rules
c=Path(__file__).resolve().parent; now=datetime.now(timezone.utc).isoformat(timespec='seconds'); read=lambda p:json.loads(Path(p).read_bytes())
package=read('data/practices/04-emep.json'); review=read('data/practices/04-emep-review.json'); base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json'); inv=read('data/practices/04-inventory.json'); entries=package['entries']; records=package['practice_records']
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(78,75,0)
case='0410-tezkere-1231'; topic='dis-politika'; event=case+'-event'; relation=case+'-relation'; statement=case+'-statement'; sources=read(c/'tezkere-1231-source-draft-v2.json')['entries']; entries.extend(sources); passages={e['values']['id']:e['values'] for e in sources if e['kind']=='passage'}; versions={e['values']['id']:e['values'] for e in sources if e['kind']=='document_version'}
def add(table,**v): records[table].append(v)
def insert(table,**v): entries.append({'kind':table,'values':v})
def finding(suffix,text,provenance,refs,heading,pair):
 fid=case+'-'+suffix; insert('finding',id=fid,party_id='emep',heading=heading,pair_id=pair,text=text,provenance=provenance,epistemic_type='claim'); insert('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Parti çağrısı ve TBMM tutanakları ayrı okundu; atıf ve tarih sınırları korundu.')
 for pid in refs: insert('finding_evidence',finding_id=fid,passage_id=pid,role='support'); insert('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün kaynak pasajı ve atıf sınırı incelendi.')
 return fid
pid=lambda s:case+'-'+s+'-p'; call=pid('party-call'); east=pid('party-east'); request=pid('floor-request'); accepted=pid('floor-accepted'); opening=pid('floor-opening'); closing=pid('floor-closing'); registry=pid('later-registry')
limit='EMEP metni 3/878 numarasını yazmaz; eşleştirme tarih ve konuya dayanır. Tutanaktaki 17.23 ve 19.36 oturum sınırlarıdır, kesin oylama saati değildir. İsimli veya sayısal oy cetveli ve Resmî Gazete özgün karar metni doğrulanmadı; bireysel veya parti oyu ve EMEP etkisi çıkarılmaz. 1231 numarası sonraki 2020 tutanağının geçmiş karara atfıdır.'
summary=finding('call-summary','EMEP Genel Merkezi 8 Ekim 2019’da Fırat’ın doğusu ve sınır ötesi tezkere bağlamında milletvekillerine tezkerede hayır oyu verme çağrısı yaptı.','summary',[call,east],'Dış politika',statement)
quote=finding('call-quote',passages[call]['exact'],'quote',[call],'Dış politika',statement)
result=finding('result','TBMM 8 Ekim 2019’da 3/878 esas numaralı Irak ve Suriye tezkeresini kabul etti; izin 30 Ekim 2019’dan itibaren bir yıl uzatıldı. 2020 tutanağı bu önceki kararı 8 Ekim 2019 tarihli 1231 sayılı karar olarak anar.','summary',[request,accepted,registry],'Belgelenmiş uygulamalar',case+'-result')
explanation=finding('comparison','EMEP 8 Ekim’de Fırat’ın doğusuna ilişkin tezkereye hayır çağrısı yaptı; açıklama 3/878 numarasını yazmaz. Aynı gün TBMM 3/878 sayılı Irak ve Suriye tezkeresini kabul etti; iznin uzatma dönemi 30 Ekim’de başladı. 2020 tarihli sonraki tutanak önceki kararı 1231 olarak anar. Resmî Gazete karar aslı ve isimli oy cetveli doğrulanamadı.','summary',[call,east,request,accepted,registry],'Belgelenmiş uygulamalar',case+'-comparison')
for lane in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='emep' and x['topic_id']==topic and x['research_kind']==lane); sid=cell['cell_id']
 if not any(x['id']==sid for x in records['practice_scope_v2']): add('practice_scope_v2',id=sid,party_id='emep',topic_id=topic,taxonomy_version=4,period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=lane,boundary_reason='2019 tezkere görüşmesi incelendi; kaynak araştırması açık.')
 if lane=='statement': ss=sid
 else: es=sid
add('practice_statement',id=statement,party_id='emep',topic_id=topic,taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at='2019-10-08',date_precision='day',version_id=case+'-party-v1',period_basis='Parti yayımı 8 Ekim 2019 saat 13.18 +03; TBMM ikinci oturumu 17.23te açıldı.',uncertainty_reason='Açıklama 3/878 numarasını açıkça vermez; kendi çağrısı herhangi bir milletvekilinin veya partinin gerçekleşen oyu değildir.',comparison_row_id='04-03-v3-0309-emep-program-016-0-row')
add('practice_event',id=event,common_event_key='tbmm-2019-irak-suriye-tezkere-3-878-karar-1231',event_at='2019-10-08',date_precision='day',date_unknown_reason=None,scope_context='TBMM 27. dönem 3. yasama yılı 3. birleşim, Irak ve Suriye tezkere görüşmesi',title='TBMM 3/878 Irak ve Suriye tezkeresini kabul etti',occurrence_basis='8 Ekim ikinci oturum tutanağında başkan 3/878 tezkeresinin kabul edildiğini açıkladı. İzin dönemi 30 Ekim 2019’dan itibaren bir yıldır; 2020 tutanağı 2019 kararını 1231 diye anar.')
evidence={'floor-request':('initiative','3/878, iznin 30 Ekim 2019’dan itibaren bir yıl uzatılmasını içerir.'),'floor-accepted':('result','Başkan 3/878 esas numaralı tezkerenin kabul edildiğini açıklar.'),'floor-opening':('action','İkinci oturum 17.23te açılır; bu oylamanın tam saati değildir.'),'floor-closing':('result','İkinci oturum 19.36da kapanır; bu oylamanın tam saati değildir.'),'later-registry':('result','2020 görüşmesindeki metin 8 Ekim 2019 tarihli 1231 sayılı önceki kararı anar.')}
for key,(stage,point) in evidence.items():
 p=pid(key); add('practice_event_evidence',event_id=event,passage_id=p,stage=stage,supported_point=point,concrete_basis=passages[p]['section'],limitation=limit,epistemic_type='claim'); add('practice_evidence_assessment',event_id=event,passage_id=p,stage=stage,basis_kind='document')
add('practice_relation',id=relation,statement_id=statement,event_id=event,party_id='emep',topic_id=topic,scope_id=es,comparability_reason='Aynı gün parti, Fırat’ın doğusundaki sınır ötesi tezkereye ret çağrısı yaptı; TBMM Irak ve Suriye hakkındaki 3/878 tezkeresini görüştü ve kabul etti. Parti numarayı yazmadığı için eşleştirme konu ve zamana dayanır.',target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,temporal_context='8 Ekim 2019 parti açıklaması ve Meclis kabulü; izin uzatması 30 Ekim 2019da başlar. 2020 tutanağı önceki kararı anar.',authority_context='Çağrı EMEP Genel Merkezine, kabul TBMMye aittir; parti karar yetkisi veya etkisi çıkarılmaz.',uncertainty_reason=limit)
add('practice_candidate',id=case+'-candidate',scope_id=es,event_id=event,relation_id=relation,state='eligible',reason='Parti çağrısı ve aynı gün TBMM kabulü içerik, zaman ve kimlik sınırlarıyla karşılaştırıldı.',passage_ids=json.dumps([request,accepted,registry]))
for ver,v in versions.items():
 role=ver[len(case)+1:-3]; scopes=(ss,es) if role=='party' else (es,); sections=sorted({p['section'] for p in passages.values() if p['version_id']==ver})
 for scope in scopes:
  aid=ver+('-statement-reading' if scope==ss else '-event-reading'); add('practice_scope_source',scope_id=scope,version_id=ver,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now); add('practice_attempt_v2',id=aid,scope_id=scope,attempted_at=now,query=v['original_url'],url=v['original_url'],result='examined',reason='Özgün parti açıklaması veya TBMM tutanağı incelendi.',source_version_id=ver); add('practice_lead',id='lead-'+aid,scope_id=scope,url=v['original_url'],state='examined',relevance_reason='2019 Irak-Suriye tezkeresi ve önceki karara 2020 atfı.',attempt_ids=json.dumps([aid]))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items(): data.setdefault(table,[]).extend(r for r in rows if r not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep'); allp={p['id']:p for p in data['passage']}; reviews=list(review['practice_source_review']); old={(r['subject_kind'],r['subject_id']) for r in reviews}; assert old<=targets.keys()
for (kind,identity),(ids,_) in sorted(targets.items()):
 if (kind,identity) in old: continue
 ps=[allp[i] for i in sorted(ids)]; claims=[evidence[k][1] for k in evidence if pid(k) in ids]
 if call in ids: claims.append('EMEP milletvekillerine tezkereye hayır çağrısı yaptı.')
 if east in ids: claims.append('Parti açıklaması Fıratın doğusundan söz eder.')
 assert claims,(kind,identity,ids)
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in ps})),passage_ids=json.dumps([p['id'] for p in ps]),inspected_sections=json.dumps(sorted({p['section'] for p in ps}),ensure_ascii=False),supported_claim=' '.join(claims),limitations=limit,result='reviewed',reason=kind+' / '+identity+' için özgün kaynak incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets)); refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs; review['practice_source_review']=reviews; review['source_review_refs']=refs
for name,obj in [('tezkere-1231-draft-v2.json',package),('tezkere-1231-review-draft-v2.json',review)]:
 with (c/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('TEZKERE1231_SEMANTIC_OK',len(reviews),len(records['practice_event']),len(records['practice_relation']))
