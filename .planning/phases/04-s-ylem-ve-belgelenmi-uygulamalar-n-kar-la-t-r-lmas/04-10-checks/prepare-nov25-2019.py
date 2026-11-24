import copy,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
c=Path(__file__).resolve().parent;now=datetime.now(timezone.utc).isoformat(timespec='seconds');read=lambda p:json.loads(Path(p).read_bytes())
package=read('data/practices/04-emep.json');review=read('data/practices/04-emep-review.json');base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json');inv=read('data/practices/04-inventory.json');entries=package['entries'];records=package['practice_records'];assert (len(records['practice_event']),len(records['practice_relation']))==(77,74);assert not records['practice_closure']
case='0410-nov25-2019';topic='demokrasi-katilim';event=case+'-event';relation=case+'-relation';statement=case+'-statement';sources=read(c/'nov25-2019-source-draft.json')['entries'];entries.extend(sources);passages={e['values']['id']:e['values'] for e in sources if e['kind']=='passage'};versions={e['values']['id']:e['values'] for e in sources if e['kind']=='document_version'}
def add(table,**v):records[table].append(v)
def insert(table,**v):entries.append({'kind':table,'values':v})
def finding(suffix,text,provenance,refs,heading,pair):
 fid=case+'-'+suffix;insert('finding',id=fid,party_id='emep',heading=heading,pair_id=pair,text=text,provenance=provenance,epistemic_type='claim');insert('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Parti açıklaması, haber ve tutanak ayrı okundu; resmî karar metninin eksikliği korundu.')
 for pid in refs:insert('finding_evidence',finding_id=fid,passage_id=pid,role='support');insert('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün kaynak pasajı ve atıf sınırı incelendi.')
 return fid
pid=lambda s:case+'-'+s+'-p';call=pid('party-call');partyban=pid('party-ban');ban=[pid('ban-time'),pid('ban-decision')];walk=[pid('event-walk'),pid('floor-walk')];later=[pid('event-narrow'),pid('event-police'),pid('floor-response')]
limit='Kaymakamlığın yasak ve iptal/değişiklik metinlerine doğrudan erişilemedi; yasak haberin kaymakamlık aktarımına dayanır. Değişiklik ve polis müdahalesi güncellenmiş haberin, dağıtılma TBMMdeki milletvekili beyanının anlatımıdır. Parti katılımı, karar yetkisi ve nedensellik gösterilmez; parti açıklaması ile değişiklik haberinin gün içindeki sırası belirsizdir.'
summary=finding('call-summary','EMEP Genel Merkezi 25 Kasım 2019’da İstanbul’daki yasaklamayı eleştirerek kadınları sokakta buluşmaya çağırdı.','summary',[call,partyban],'Demokrasi ve katılım',statement)
quote=finding('call-quote',passages[call]['exact'],'quote',[call],'Demokrasi ve katılım',statement)
result=finding('result','Gazete Emek’in haberine göre 25 Kasım’da kadınlar Tünel’de toplandı; güzergâh kısaltılarak yasak kaldırıldı ve yürüyüş sonrasında polis müdahalesi yaşandı. TBMM’de 26 Kasım’da Akbaşoğlu Tünel’den başlayan yaklaşık 100 metrelik etkinlikten ve ardından bir grubun dağıtılmasından söz etti.','summary',walk+later,'Belgelenmiş uygulamalar',case+'-result')
explanation=finding('comparison','EMEP 25 Kasım’da yasağı eleştirip kadınları sokakta buluşmaya çağırdı. 24 Kasım’da Beyoğlu Kaymakamlığı’nın Tünel’deki belirli yürüyüşü yasakladığı kararı haber tarafından aktarıldı; bu karar parti açıklamasından öncedir. Gazete Emek 25 Kasım’da güzergâh kısaltılarak yasağın kaldırıldığını, Tünel’de buluşma ve sonrasında polis müdahalesi olduğunu bildirdi. TBMM’de 26 Kasım’da Akbaşoğlu yaklaşık 100 metrelik etkinlikten ve sonrasında bir grubun dağıtılmasından söz etti. İptal veya değişiklik kararı aslına ulaşılamadı; parti açıklamasıyla değişiklik haberinin gün içindeki kesin sırası bilinmiyor.','summary',[call,partyban]+ban+walk+later,'Belgelenmiş uygulamalar',case+'-comparison')
for lane in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='emep' and x['topic_id']==topic and x['research_kind']==lane);sid=cell['cell_id']
 if not any(x['id']==sid for x in records['practice_scope_v2']):add('practice_scope_v2',id=sid,party_id='emep',topic_id=topic,taxonomy_version=4,period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=lane,boundary_reason='25 Kasım 2019 Tünel etkinliğine ilişkin haberler ve tutanak incelendi; araştırma kapsamı açık.')
 if lane=='statement':ss=sid
 else:es=sid
add('practice_statement',id=statement,party_id='emep',topic_id=topic,taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at='2019-11-25',date_precision='day',version_id=case+'-party-v1',period_basis='25 Kasım 2019 parti yayımı 12.31 +03; gün içindeki sonraki olay ve haber saatleri tüm yönleriyle saptanmadı.',uncertainty_reason='Partinin genel buluşma çağrısı, EMEP katılımı veya yürüyüşü düzenlemesi kanıtı değildir.',comparison_row_id='04-03-v3-03-v2-emep-demokrasi')
add('practice_event',id=event,common_event_key='istanbul-beyoglu-25-kasim-kadin-yuruyusu-2019',event_at='2019-11-25',date_precision='day',date_unknown_reason=None,scope_context='İstanbul, Beyoğlu Tünel ve İstiklal Caddesi; 25 Kasım Kadın Platformu yürüyüşü',title='25 Kasım 2019 Beyoğlu kadın yürüyüşü ve bildirilen müdahale',occurrence_basis='Gazete Emek Tünel buluşmasını ve yürüyüşü haberleştirir; 26 Kasım TBMM tutanağında Akbaşoğlu yaklaşık 100 metrelik etkinlikten söz eder. İlk yasak önceki güne, bildirilen güzergâh değişikliği ve müdahale 25 Kasıma ilişkindir.')
evidence={'ban-time':('initiative','Haberde 25 Kasım saat 19.00 için Tünel Meydanı buluşması kaymakamlık duyurusuna atıfla aktarılır.'),'ban-decision':('initiative','Haber 24 Kasım tarih ve 2804 numaralı Beyoğlu Kaymakamlığı yasak kararını aktarır; özgün karar elde edilmedi.'),'event-walk':('action','Gazete Emek 25 Kasım Kadın Platformunun Tünel’de toplandığını bildirir.'),'floor-walk':('action','Akbaşoğlu TBMMde Tünel’de yaklaşık 100 metrelik etkinlikten söz eder.'),'event-narrow':('result','Güncellenmiş haber güzergâh kısaltılıp yasağın kaldırıldığını bildirir; resmî değişiklik metni elde edilmedi.'),'event-police':('result','Güncellenmiş haber basın açıklaması sonrası biber gazıyla müdahale bildirir.'),'floor-response':('result','Akbaşoğlu bir grubun dağıtıldığını söyler; gerekçe ve sayılar kendi beyanıdır.')}
for key,(stage,point) in evidence.items():
 p=pid(key);add('practice_event_evidence',event_id=event,passage_id=p,stage=stage,supported_point=point,concrete_basis=passages[p]['section'],limitation=limit,epistemic_type='claim');add('practice_evidence_assessment',event_id=event,passage_id=p,stage=stage,basis_kind='document')
add('practice_relation',id=relation,statement_id=statement,event_id=event,party_id='emep',topic_id=topic,scope_id=es,comparability_reason='Aynı 25 Kasım günü İstanbul’daki kadınların sokakta buluşma çağrısı ve Tünel’deki kadın yürüyüşü karşılaştırılır; yasak, değişiklik ve müdahale farklı aşamalardır.',target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,temporal_context='24 Kasım yasak haberi; 25 Kasım parti çağrısı ve yürüyüş; 26 Kasım Meclis beyanı. İptal/değişiklik saati ile parti açıklamasının sırası bilinmez.',authority_context='Çağrı EMEPindir; haberin aktardığı yasak Beyoğlu Kaymakamlığına, sonraki müdahale polise aittir. Parti katılımı, karar yetkisi veya nedensellik çıkarılmaz.',uncertainty_reason=limit)
add('practice_candidate',id=case+'-candidate',scope_id=es,event_id=event,relation_id=relation,state='eligible',reason='25 Kasım çağrısı, aynı günkü Tünel buluşması ve karşıt kaynak sınırları ayrı pasajlarla desteklenmiştir.',passage_ids=json.dumps(walk+later))
for ver,v in versions.items():
 role=ver[len(case)+1:-3];scopes=(ss,es) if role=='party' else (es,);sections=sorted({p['section'] for p in passages.values() if p['version_id']==ver})
 for scope in scopes:
  aid=ver+('-statement-reading' if scope==ss else '-event-reading');add('practice_scope_source',scope_id=scope,version_id=ver,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now);add('practice_attempt_v2',id=aid,scope_id=scope,attempted_at=now,query=v['original_url'],url=v['original_url'],result='examined',reason='Özgün parti açıklaması, haber veya tutanak pasajı incelendi.',source_version_id=ver);add('practice_lead',id='lead-'+aid,scope_id=scope,url=v['original_url'],state='examined',relevance_reason='25 Kasım Tünel toplantısı ve yasak süreci.',attempt_ids=json.dumps([aid]))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(r for r in rows if r not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep');allp={p['id']:p for p in data['passage']};reviews=list(review['practice_source_review']);old={(r['subject_kind'],r['subject_id']) for r in reviews};assert old<=targets.keys()
for (kind,identity),(ids,_) in sorted(targets.items()):
 if (kind,identity) in old:continue
 ps=[allp[i] for i in sorted(ids)];claims=[evidence[k][1] for k in evidence if pid(k) in ids]
 if call in ids:claims.append('EMEP Genel Merkezi kadınları sokaklarda buluşmaya çağırdı.')
 if partyban in ids:claims.append('EMEP açıklaması yasağı valiye atfederek eleştirdi.')
 assert claims,(kind,identity,ids)
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in ps})),passage_ids=json.dumps([p['id'] for p in ps]),inspected_sections=json.dumps(sorted({p['section'] for p in ps}),ensure_ascii=False),supported_claim=' '.join(claims),limitations=limit,result='reviewed',reason=kind+' / '+identity+' için özgün kaynak incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs;review['practice_source_review']=reviews;review['source_review_refs']=refs
for name,obj in [('nov25-2019-draft.json',package),('nov25-2019-review-draft.json',review)]:
 with (c/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('NOV25_SEMANTIC_OK',len(reviews),len(records['practice_event']),len(records['practice_relation']))
