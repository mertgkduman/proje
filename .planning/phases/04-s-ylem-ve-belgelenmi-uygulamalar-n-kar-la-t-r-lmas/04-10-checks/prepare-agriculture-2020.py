import copy,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
c=Path(__file__).resolve().parent; now=datetime.now(timezone.utc).isoformat(timespec='seconds'); read=lambda p:json.loads(Path(p).read_bytes())
package=read('data/practices/04-emep.json'); review=read('data/practices/04-emep-review.json'); base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json'); inv=read('data/practices/04-inventory.json')
entries=package['entries']; records=package['practice_records']; assert (len(records['practice_event']),len(records['practice_relation']))==(76,73); assert not records['practice_closure']
case='0410-agriculture-2020'; topic='tarim-hayvancilik'; event=case+'-event'; relation=case+'-relation'; statement=case+'-statement'; sources=read(c/'agriculture-2020-source-draft.json')['entries']; entries.extend(sources)
passages={e['values']['id']:e['values'] for e in sources if e['kind']=='passage'}; versions={e['values']['id']:e['values'] for e in sources if e['kind']=='document_version'}
def add(table,**v): records[table].append(v)
def insert(table,**v): entries.append({'kind':table,'values':v})
def finding(suffix,text,provenance,refs,heading,pair):
 fid=case+'-'+suffix; insert('finding',id=fid,party_id='emep',heading=heading,pair_id=pair,text=text,provenance=provenance,epistemic_type='claim'); insert('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Parti metni, takvim ve bütçe gerçekleşmesi ayrı okundu.')
 for pid in refs: insert('finding_evidence',finding_id=fid,passage_id=pid,role='support'); insert('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün pasaj ve sınırı incelendi.')
 return fid
pid=lambda s:case+'-'+s+'-p'
party=pid('party-request'); prior=[pid('prior-day'),pid('prior-schedule')]; schedule=pid('schedule-schedule'); budget=[pid('budget-row'),pid('budget-header')]
summary=finding('request-summary','EMEP Genel Merkezi, 22 Nisan 2020’de 2019 yılından kalan tarım desteklerinin tamamının Nisan ayında ödenmesini istedi.','summary',[party],'Tarım ve hayvancılık',statement)
quote=finding('request-quote',passages[party]['exact'],'quote',[party],'Tarım ve hayvancılık',statement)
result=finding('result','24 Nisan 2020’de Tarım ve Orman Bakanı, 2019 ilk dönem buzağı desteği için 30 Nisan, 8 ve 15 Mayıs tarihlerini içeren kademeli ödeme takvimini açıkladı. Hazine bülteninde Nisan ve Mayıs için buzağı desteği gerçekleşmeleri yer aldı.','summary',[schedule]+budget,'Belgelenmiş uygulamalar',case+'-result')
limit='2019 desteklerinin tümüne ilişkin parti talebi, yalnız buzağı desteği takvimi ve bütçe satırı ile bütünüyle değerlendirilemez. Bütçe tutarları tüm buzağı destekleri için aylık toplamdır; yıl dönemi veya kişisel tahsilat ayrımı yoktur. Ön duyuru partiden öncedir; parti nedenselliği ve karar yetkisi gösterilmez.'
explanation=finding('comparison','EMEP 22 Nisan’da 2019’dan kalan tarım desteklerinin tamamının Nisan’da ödenmesini istedi. Balıkesir Haykoop 21 Nisan’da 2019 ilk dönem buzağı desteği takvimini 24 ve 30 Nisan ile 8 ve 15 Mayıs olarak duyurmuştu. Bakanın 24 Nisan’da basına aktarılan takvimi de Mayıs’a uzanır. Hazine’nin Ağustos bülteni, buzağı desteği bütçe gerçekleşmelerini Nisan’da 710, Mayıs’ta 690 milyon TL olarak gösterir; bu aylık toplamlar tek başına aynı dönemin veya her üreticinin ödemesini kanıtlamaz.','summary',[party]+prior+[schedule]+budget,'Belgelenmiş uygulamalar',case+'-comparison')
for lane in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='emep' and x['topic_id']==topic and x['research_kind']==lane); sid=cell['cell_id']
 if not any(x['id']==sid for x in records['practice_scope_v2']): add('practice_scope_v2',id=sid,party_id='emep',topic_id=topic,taxonomy_version=4,period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=lane,boundary_reason='Buzağı desteği takvimi ve bütçe gerçekleşmesi incelendi; tarım araştırması açık.')
 if lane=='statement': ss=sid
 else: es=sid
add('practice_statement',id=statement,party_id='emep',topic_id=topic,taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at='2020-04-22',date_precision='day',version_id=case+'-party-v1',period_basis='22 Nisan 2020 parti yayımı.',uncertainty_reason='Genel tarım destekleri talebi; tek bir buzağı desteği programı adı verilmez.',comparison_row_id='04-03-v3-0309-emep-program-056-1-row')
add('practice_event',id=event,common_event_key='turkiye-2019-ilk-donem-buzagi-destek-2020-takvim',event_at='2020-04-24',date_precision='day',date_unknown_reason=None,scope_context='2019 ilk dönem buzağı desteklerinin 2020 takvimi',title='2019 ilk dönem buzağı desteği ödeme takvimi',occurrence_basis='24 Nisan tarihli AA haberinde Bakanın Nisan ve Mayısa yayılan takvimi aktarılır. Takvim 21 Nisanda üretici birliğince de duyurulmuştur; Ağustos bütçe bülteni Nisan ve Mayıs ayları için toplu gerçekleşmeleri kaydeder.')
evidence={'prior-day':('initiative','Üretici birliği duyurusunun tarihi 21 Nisandır.'),'prior-schedule':('initiative','Birlik ilk dönem buzağı ödeme takvimini Nisan ve Mayıs için duyurmuştur.'),'schedule-schedule':('action','Bakanın AA tarafından aktarılan takvimi 30 Nisan, 8 ve 15 Mayısı içerir.'),'budget-row':('result','Bütçe tablosunda buzağı desteği aylık toplamları yer alır.'),'budget-header':('result','Hazine bülteni tutarları milyon TL cinsindendir.')}
for key,(stage,point) in evidence.items():
 p=pid(key); add('practice_event_evidence',event_id=event,passage_id=p,stage=stage,supported_point=point,concrete_basis=passages[p]['section'],limitation=limit,epistemic_type='claim'); add('practice_evidence_assessment',event_id=event,passage_id=p,stage=stage,basis_kind='document')
add('practice_relation',id=relation,statement_id=statement,event_id=event,party_id='emep',topic_id=topic,scope_id=es,comparability_reason='Partinin 2019 tarım desteklerinin Nisan içinde tamamen ödenmesi talebi, o yılın belirli bir buzağı desteğinin Nisan-Mayıs ödeme takvimiyle kısmi karşılaştırılabilir.',target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,temporal_context='21 Nisan ön duyuru, 22 Nisan parti talebi, 24 Nisan bakan takvimi ve sonraki aylık bütçe gerçekleşmeleri.',authority_context='Talep EMEPindir; takvim Bakanlık, bütçe verisi Hazine ve Maliye Bakanlığı kaynaklıdır. Parti karar yetkisi ve nedensellik gösterilmez.',uncertainty_reason=limit)
add('practice_candidate',id=case+'-candidate',scope_id=es,event_id=event,relation_id=relation,state='eligible',reason='2019 tarım desteklerine ilişkin talep ve belirli bir destek için tarihli ödeme takvimi ve aylık gerçekleşme kaynakla sınırlandı.',passage_ids=json.dumps([schedule]+budget))
for ver,v in versions.items():
 role=ver[len(case)+1:-3]; scopes=(ss,es) if role=='party' else (es,); sections=sorted({p['section'] for p in passages.values() if p['version_id']==ver})
 for scope in scopes:
  aid=ver+('-statement-reading' if scope==ss else '-event-reading'); add('practice_scope_source',scope_id=scope,version_id=ver,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now); add('practice_attempt_v2',id=aid,scope_id=scope,attempted_at=now,query=v['original_url'],url=v['original_url'],result='examined',reason='Özgün açıklama, takvim veya bütçe satırı incelendi.',source_version_id=ver); add('practice_lead',id='lead-'+aid,scope_id=scope,url=v['original_url'],state='examined',relevance_reason='2019 desteği ve 2020 ödeme takvimi.',attempt_ids=json.dumps([aid]))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items(): data.setdefault(table,[]).extend(r for r in rows if r not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep'); allp={p['id']:p for p in data['passage']}; reviews=list(review['practice_source_review']); old={(r['subject_kind'],r['subject_id']) for r in reviews}; assert old<=targets.keys()
for (kind,identity),(ids,_) in sorted(targets.items()):
 if (kind,identity) in old: continue
 ps=[allp[i] for i in sorted(ids)]; claims=[evidence[k][1] for k in evidence if pid(k) in ids]
 if party in ids: claims.append('EMEP 2019dan kalan tarım desteklerinin Nisan ayında tamamen ödenmesini istedi.')
 assert claims,(kind,identity,ids)
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in ps})),passage_ids=json.dumps([p['id'] for p in ps]),inspected_sections=json.dumps(sorted({p['section'] for p in ps}),ensure_ascii=False),supported_claim=' '.join(claims),limitations=limit,result='reviewed',reason=kind+' / '+identity+' için özgün kaynak incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets)); refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs; review['practice_source_review']=reviews; review['source_review_refs']=refs
for name,obj in [('agriculture-2020-draft.json',package),('agriculture-2020-review-draft.json',review)]:
 with (c/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('AGRICULTURE_SEMANTIC_OK',len(reviews),len(records['practice_event']),len(records['practice_relation']))
