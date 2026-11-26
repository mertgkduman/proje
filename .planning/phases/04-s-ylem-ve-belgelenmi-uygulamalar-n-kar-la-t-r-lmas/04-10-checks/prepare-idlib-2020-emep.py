import copy,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
c=Path(__file__).resolve().parent; now=datetime.now(timezone.utc).isoformat(timespec='seconds'); read=lambda p:json.loads(Path(p).read_bytes()); package=read('data/practices/04-emep.json'); review=read('data/practices/04-emep-review.json'); base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json'); inv=read('data/practices/04-inventory.json'); entries=package['entries']; records=package['practice_records']; assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(86,80,0)
case='0410-idlib-2020'; topic='dis-politika'; event=case+'-event'; relation=case+'-relation'; statement=case+'-statement'; sources=read(c/'idlib-2020-emep-v2-source-draft.json')['entries']; entries.extend(sources); passages={e['values']['id']:e['values'] for e in sources if e['kind']=='passage'}; versions={e['values']['id']:e['values'] for e in sources if e['kind']=='document_version'}
def add(table,**v): records[table].append(v)
def insert(table,**v): entries.append(dict(kind=table,values=v))
def finding(suffix,text,provenance,refs,heading,pair):
 fid=case+'-'+suffix; insert('finding',id=fid,party_id='emep',heading=heading,pair_id=pair,text=text,provenance=provenance,epistemic_type='claim'); insert('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Parti açıklaması ve BM protokolü ayrı okundu.')
 for pid in refs: insert('finding_evidence',finding_id=fid,passage_id=pid,role='support'); insert('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün metindeki pasaj doğrulandı.')
 return fid
q=case+'-call-quote'; allp=case+'-call-all'; sig=case+'-bm-signature'; start=case+'-bm-start'; patrol=case+'-bm-patrol'; letter=case+'-bm-transmission'
limit='EMEP İdlib’de ateş altındaki Türk askerlerinin ve Suriye’deki tüm askerî güçlerin çekilmesini ister. 5 Mart protokolü İdlib gerginliği azaltma bölgesindeki temas hattıyla sınırlı ateşkes ve devriye hükümleri içerir; tam çekilme kararı değildir. 6 Mart saat 00.01 öngörülen ateşkes başlangıcı ve 15 Mart devriyesi, 5 Mart imza ve 6 Mart BM iletiminden ayrıdır. Ateşkes veya devriyenin fiilen uygulanması, toplam asker çekilmesi ve partinin karar üzerindeki etkisi doğrulanmadı.'
summary=finding('call-summary','EMEP Genel Merkezi 28 Şubat 2020’de İdlib’de ateş altındaki askerlerin acilen çekilmesini, Suriye’ye müdahaleye son verilmesini ve bölgedeki tüm askerî güçlerin çekilmesini istedi.','summary',[q,allp],'Dış politika',statement)
quote=finding('call-quote-finding',passages[q]['exact'],'quote',[q],'Dış politika',statement)
result=finding('result','Türkiye ve Rusya 5 Mart 2020’de İdlib için ek protokol imzaladı. Protokol 6 Mart 00.01 itibarıyla temas hattında askerî eylemlerin durdurulmasını ve 15 Marttan itibaren ortak devriyeyi öngörür.','summary',[sig,start,patrol,letter],'Belgelenmiş uygulamalar',case+'-result')
explanation=finding('comparison','EMEP 28 Şubatta İdlib’deki askerlerin ve bölgedeki tüm askerî güçlerin çekilmesini istedi. Türkiye ve Rusya 5 Martta İdlib temas hattında öngörülen ateşkes ve ortak devriyeyi düzenleyen protokolü imzaladı. Protokol tüm güçlerin çekilmesini düzenlemez; sahadaki uygulama burada değerlendirilmedi.','summary',[q,allp,sig,start,patrol,letter],'Belgelenmiş uygulamalar',case+'-comparison')
for lane in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='emep' and x['topic_id']==topic and x['research_kind']==lane); sid=cell['cell_id']
 if not any(x['id']==sid for x in records['practice_scope_v2']): add('practice_scope_v2',id=sid,party_id='emep',topic_id=topic,taxonomy_version=4,period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=lane,boundary_reason='İdlib açıklaması ve protokol incelendi; kapsam açık.')
 if lane=='statement': ss=sid
 else: es=sid
add('practice_statement',id=statement,party_id='emep',topic_id=topic,taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at='2020-02-28',date_precision='day',version_id=case+'-call-v1',period_basis='EMEP Genel Merkezinin 28 Şubat 2020 tarihli asıl yayımı.',uncertainty_reason='Söz partiye aittir; sahadaki askerî durum ve sebeplere ilişkin değerlendirmeler bağımsız doğrulanmadı.',comparison_row_id='04-03-v3-0309-emep-program-016-0-row')
add('practice_event',id=event,common_event_key='idlib-2020-03-05-moskova-ek-protokol',event_at='2020-03-05',date_precision='day',date_unknown_reason=None,title='Türkiye ve Rusya’nın İdlib ek protokolü',scope_context='5 Mart 2020’de Moskova’da Türkiye ve Rusya’nın İdlib Gerginliği Azaltma Bölgesi için imzaladığı ek protokol.',occurrence_basis='Türkiye ve Rusya temsilcilerinin 6 Mart tarihli S/2020/187 ortak iletimi ve ekindeki protokol.')
evidence=[(sig,'action','S/2020/187 eki, 5 Mart Moskova imzası.'),(start,'result','S/2020/187 eki madde 1, İdlib temas hattında ateşkesin öngörülen başlangıcı.'),(patrol,'result','S/2020/187 eki madde 3, 15 Mart için ortak devriye düzenlemesi.'),(letter,'result','S/2020/187 mektubu, BM’ye 6 Mart iletimi.')]
for pid,stage,point in evidence: add('practice_event_evidence',event_id=event,passage_id=pid,stage=stage,supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'); add('practice_evidence_assessment',event_id=event,passage_id=pid,stage=stage,basis_kind='document')
add('practice_relation',id=relation,statement_id=statement,event_id=event,party_id='emep',topic_id=topic,scope_id=es,comparability_reason='İdlib’de askerlerin geri çekilmesini isteyen önceki EMEP açıklaması, aynı bölgeye ilişkin Türkiye-Rusya ek protokolünün içeriğiyle kapsam farkı gözetilerek karşılaştırılır.',target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,temporal_context='28 Şubat EMEP talebi; 5 Mart protokol imzası; 6 Mart 00.01 öngörülen ateşkes ve BM’ye iletim; 15 Mart öngörülen devriye.',authority_context='Talep EMEP Genel Merkezine; protokol Türkiye ve Rusya’ya; BM mektubu iki ülkenin daimi temsilcilerine aittir. Partiye karar veya uygulama yetkisi atfedilmez.',uncertainty_reason=limit)
add('practice_candidate',id=case+'-candidate',scope_id=es,event_id=event,relation_id=relation,state='eligible',reason='İdlib’e ilişkin önceki talep ile sonraki protokolün ortak coğrafyası ve farklı kapsamları özgün belgelerde izlenebilir.',passage_ids=json.dumps([q,allp,sig,start,patrol,letter]))
for ver,v in versions.items():
 for scope in ((ss,es) if '-call-' in ver else (es,)):
  sections=sorted({p['section'] for p in passages.values() if p['version_id']==ver}); aid=ver+'-reading-'+('statement' if scope==ss else 'event'); add('practice_scope_source',scope_id=scope,version_id=ver,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now); add('practice_attempt_v2',id=aid,scope_id=scope,attempted_at=now,query=v['original_url'],url=v['original_url'],result='examined',reason='EMEP çağrısı ve BM ek protokolü okundu.',source_version_id=ver); add('practice_lead',id='lead-'+aid,scope_id=scope,url=v['original_url'],state='examined',relevance_reason='İdlib talebi ve protokol.',attempt_ids=json.dumps([aid]))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items(): data.setdefault(table,[]).extend(r for r in rows if r not in data[table])
rules.validate_practices(data); targets=rules.practice_review_package_targets(data,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep'); all_passages={p['id']:p for p in data['passage']}; reviews=list(review['practice_source_review']); old={(r['subject_kind'],r['subject_id']) for r in reviews}; assert old<=targets.keys()
for (kind,identity),(ids,_) in sorted(targets.items()):
 if (kind,identity) in old: continue
 ps=[all_passages[i] for i in sorted(ids)]; assert ps; claims=[]
 if q in ids: claims.append('EMEP İdlib’de ateş altındaki askerlerin geri çekilmesini ister.')
 if allp in ids: claims.append('EMEP bölgedeki bütün askerî güçlerin geri çekilmesini savunur.')
 for pid,stage,point in evidence:
  if pid in ids: claims.append(point)
 assert claims,(kind,identity,ids)
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in ps})),passage_ids=json.dumps([p['id'] for p in ps]),inspected_sections=json.dumps(sorted({p['section'] for p in ps}),ensure_ascii=False),supported_claim=' '.join(claims),limitations=limit,result='reviewed',reason=kind+' / '+identity+' için özgün kaynak incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets)); refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs; review['practice_source_review']=reviews; review['source_review_refs']=refs
for name,obj in [('idlib-2020-emep-v2-draft.json',package),('idlib-2020-emep-v2-review-draft.json',review)]:
 with (c/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('IDLIB_SEMANTIC_OK',len(records['practice_event']),len(records['practice_relation']),len(reviews))
