import copy,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
c=Path(__file__).resolve().parent;now=datetime.now(timezone.utc).isoformat(timespec='seconds');read=lambda p:json.loads(Path(p).read_bytes());package=read('data/practices/04-emep.json');review=read('data/practices/04-emep-review.json');base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json');inv=read('data/practices/04-inventory.json');entries=package['entries'];records=package['practice_records'];assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(81,77,0)
case='0410-akbelen-meeting';topic='doga-ekoloji';event=case+'-event';relation=case+'-relation';statement=case+'-statement';sources=read(c/'akbelen-emep-source-draft.json')['entries'];entries.extend(sources);passages={e['values']['id']:e['values'] for e in sources if e['kind']=='passage'};versions={e['values']['id']:e['values'] for e in sources if e['kind']=='document_version'}
def add(table,**v):records[table].append(v)
def insert(table,**v):entries.append({'kind':table,'values':v})
def finding(suffix,text,provenance,refs,heading,pair):
 fid=case+'-'+suffix;insert('finding',id=fid,party_id='emep',heading=heading,pair_id=pair,text=text,provenance=provenance,epistemic_type='claim');insert('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Parti açıklaması, tarihli haber ve Meclis oturum tutanağı farklı aşamalar olarak incelendi.')
 for pid in refs:insert('finding_evidence',finding_id=fid,passage_id=pid,role='support');insert('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün kaynak pasajı ve tarihi incelendi.')
 return fid
pid=lambda s:case+'-'+s+'-p';support=pid('party-support');speaker=pid('press-speaker');call=pid('press-call');quoteid=pid('press-quote');invite=pid('floor-invitation');invitedate=pid('floor-invitation-date');opening=pid('floor-opening');quorum=pid('floor-quorum');continuation=pid('floor-continuation');debate=pid('floor-debate')
limit='4 Ağustos baskısı çağrıyı Karaca Demire atfeder; konuşmanın kesin tarihi bilinmez ve Başkanlığın 3 Ağustos davetinden önce yapıldığı çıkarılamaz. 4/13 toplantı istemi, 3/756 Başkanlık daveti, 8 Ağustos açılışı, 8/14 ön görüşmesi ve 4/15 devam önergesi farklı aşamalardır. Bu kayıt EMEP milletvekilinin 4/13te imzasını, 8/14te oyunu, orman izninin iptalini veya çevresel sonucu kanıtlamaz; açıklama ve karar arasında nedensellik kurulmaz.'
summary=finding('call-summary','4 Ağustos 2023 Başkent Gazetesi, EMEP milletvekili Sevda Karaca Demir’in Akbelen için Meclisi olağanüstü toplanmaya çağırdıklarını söylediğini aktardı. Konuşmanın günü haberde belirtilmedi.','summary',[speaker,call],'Doğa ve ekoloji',statement)
quote=finding('call-quote',passages[quoteid]['exact'],'quote',[quoteid],'Doğa ve ekoloji',statement)
result=finding('result','TBMM Başkanlığının 3 Ağustos tarihli daveti üzerine 8 Ağustos 2023’te olağanüstü birleşimin ilk oturumu 15.01’de açıldı ve toplantı yeter sayısı olduğu açıklandı.','summary',[invite,invitedate,opening,quorum],'Belgelenmiş uygulamalar',case+'-result')
explanation=finding('comparison','EMEP Genel Başkan Yardımcısı Başkavak 29 Temmuzda Akbelen’de kesime karşı İkizköylülerle dayanışma açıkladı. 4 Ağustos tarihli gazete, EMEP milletvekili Karaca Demir’in Meclisi olağanüstü toplantıya çağırdıklarını aktardı; sözün kesin günü bilinmiyor. TBMM Başkanlığı 3 Ağustosta 8 Ağustos için davet çıkarmıştı; 8 Ağustosta oturum 15.01’de açıldı. 8/14 genel görüşme önergesi ve 4/15 devam önergesi bu toplantı açılışından ayrıdır.','summary',[support,speaker,call,invite,invitedate,opening,quorum,continuation,debate],'Belgelenmiş uygulamalar',case+'-comparison')
for lane in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='emep' and x['topic_id']==topic and x['research_kind']==lane);sid=cell['cell_id']
 if not any(x['id']==sid for x in records['practice_scope_v2']):add('practice_scope_v2',id=sid,party_id='emep',topic_id=topic,taxonomy_version=4,period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=lane,boundary_reason='Akbelen olağanüstü toplantı süreci incelendi; araştırma kapsamı açık.')
 if lane=='statement':ss=sid
 else:es=sid
add('practice_statement',id=statement,party_id='emep',topic_id=topic,taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at=None,date_precision='unknown',version_id=case+'-press-v1',period_basis='Başkent Gazetesi 4 Ağustos 2023 baskısında toplantı çağrısını aktarır; haber toplantının 8 Ağustos açılışından öncedir.',uncertainty_reason='Konuşmanın gün ve saati gazete nüshasında belirtilmedi; 3 Ağustos Başkanlık davetinden önce veya sonra olduğu doğrulanmadı.',comparison_row_id='04-03-v3-0309-emep-program-041-0-row')
add('practice_event',id=event,common_event_key='tbmm-28-1-18-akbelen-olaganustu-toplanti-acilisi',event_at='2023-08-08',date_precision='day',date_unknown_reason=None,scope_context='TBMM 28. dönem 1. yasama yılı 18. olağanüstü birleşimin Akbelen gündemiyle ilk oturum açılışı.',title='Akbelen için olağanüstü Meclis toplantısının açılması',occurrence_basis='TBMM 18. birleşim tam tutanağında 3/756 Başkanlık daveti ve 8 Ağustos 15.01 açılışı.')
evidence={'floor-invitation':('initiative','Başkanlık TBMMyi Akbelen önergesini görüşmek üzere 8 Ağustosta olağanüstü toplantıya çağırdı.'),'floor-invitation-date':('initiative','Başkanlık çağrısı metninde 3 Ağustos 2023 tarihi yer alır.'),'floor-opening':('action','18. birleşimin ilk oturumu 8 Ağustosta saat 15.01de açıldı.'),'floor-quorum':('result','Açılışta oturum başkanı toplantı yeter sayısının bulunduğunu açıkladı.')}
for key,(stage,point) in evidence.items():
 p=pid(key);add('practice_event_evidence',event_id=event,passage_id=p,stage=stage,supported_point=point,concrete_basis=passages[p]['section'],limitation=limit,epistemic_type='claim');add('practice_evidence_assessment',event_id=event,passage_id=p,stage=stage,basis_kind='document')
add('practice_relation',id=relation,statement_id=statement,event_id=event,party_id='emep',topic_id=topic,scope_id=es,comparability_reason='Karaca Demire atfedilen Akbelen için olağanüstü Meclis toplantısı çağrısı ile aynı gündemli 8 Ağustos toplantısının açılışı karşılaştırılır; bu kayıt genel görüşmenin kabulü veya kişisel oy değildir.',target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,temporal_context='29 Temmuz EMEP dayanışması; 3 Ağustos Başkanlık daveti; 4 Ağustos gazete yayını; 8 Ağustos toplantının açılması. Haberde bildirilen konuşmanın kesin günü bilinmez.',authority_context='Söz gazetede Sevda Karaca Demire atfedilir; davet TBMM Başkanlığına, toplantının açılması Genel Kurula aittir. EMEP imzası, kararı veya etkisi çıkarılmaz.',uncertainty_reason=limit)
add('practice_candidate',id=case+'-candidate',scope_id=es,event_id=event,relation_id=relation,state='eligible',reason='4 Ağustosta aktarılan Akbelen toplantı çağrısı ve 8 Ağustos aynı gündemli toplantı açılışı farklı otoriteler ve tarihlerle desteklenir.',passage_ids=json.dumps([invite,opening,quorum]))
for ver,v in versions.items():
 role=ver[len(case)+1:-3];scopes=(ss,es) if role in ('party','press') else (es,);sections=sorted({p['section'] for p in passages.values() if p['version_id']==ver})
 for scope in scopes:
  aid=ver+('-statement-reading' if scope==ss else '-event-reading');add('practice_scope_source',scope_id=scope,version_id=ver,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now);add('practice_attempt_v2',id=aid,scope_id=scope,attempted_at=now,query=v['original_url'],url=v['original_url'],result='examined',reason='Parti açıklaması, tarihli gazete nüshası veya tutanak okundu.',source_version_id=ver);add('practice_lead',id='lead-'+aid,scope_id=scope,url=v['original_url'],state='examined',relevance_reason='Akbelen ve olağanüstü toplantı açılışı.',attempt_ids=json.dumps([aid]))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(r for r in rows if r not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep');allp={p['id']:p for p in data['passage']};reviews=list(review['practice_source_review']);old={(r['subject_kind'],r['subject_id']) for r in reviews};assert old<=targets.keys()
for (kind,identity),(ids,_) in sorted(targets.items()):
 if (kind,identity) in old:continue
 ps=[allp[i] for i in sorted(ids)];claims=[evidence[k][1] for k in evidence if pid(k) in ids]
 if support in ids:claims.append('Başkavak 29 Temmuzda Akbelen’deki İkizköylülere dayanışma açıklar.')
 if continuation in ids:claims.append('4/15 Saadet grubunun çalışmalara devam önergesidir.')
 if debate in ids:claims.append('8/14 Akbelen için genel görüşme açılması önergesidir.')
 if speaker in ids or call in ids or quoteid in ids:claims.append('4 Ağustos gazetesi Karaca Demire Akbelen ve Meclisi toplama çağrısı atfeder; sözün günü bilinmez.')
 assert claims,(kind,identity,ids)
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in ps})),passage_ids=json.dumps([p['id'] for p in ps]),inspected_sections=json.dumps(sorted({p['section'] for p in ps}),ensure_ascii=False),supported_claim=' '.join(claims),limitations=limit,result='reviewed',reason=kind+' / '+identity+' için özgün kaynak incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs;review['practice_source_review']=reviews;review['source_review_refs']=refs
for name,obj in [('akbelen-emep-draft.json',package),('akbelen-emep-review-draft.json',review)]:
 with (c/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('AKBELEN_EMEP_SEMANTIC_OK',len(reviews),len(records['practice_event']),len(records['practice_relation']))
