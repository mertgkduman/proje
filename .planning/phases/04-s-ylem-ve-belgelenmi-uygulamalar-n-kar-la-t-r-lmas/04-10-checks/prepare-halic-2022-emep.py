import copy,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
c=Path(__file__).resolve().parent;now=datetime.now(timezone.utc).isoformat(timespec='seconds');read=lambda p:json.loads(Path(p).read_bytes());package=read('data/practices/04-emep.json');review=read('data/practices/04-emep-review.json');base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json');inv=read('data/practices/04-inventory.json');entries=package['entries'];records=package['practice_records'];assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(82,78,0)
case='0410-halic-2022';topic='demokrasi-katilim';event=case+'-event';relation=case+'-relation';statement=case+'-statement';sources=read(c/'halic-2022-emep-source-draft.json')['entries'];entries.extend(sources);passages={e['values']['id']:e['values'] for e in sources if e['kind']=='passage'};versions={e['values']['id']:e['values'] for e in sources if e['kind']=='document_version'}
def add(table,**v):records[table].append(v)
def insert(table,**v):entries.append({'kind':table,'values':v})
def finding(suffix,text,provenance,refs,heading,pair):
 fid=case+'-'+suffix;insert('finding',id=fid,party_id='emep',heading=heading,pair_id=pair,text=text,provenance=provenance,epistemic_type='claim');insert('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Önceki çağrı ve sonraki buluşma yayınları ayrı okundu.')
 for pid in refs:insert('finding_evidence',finding_id=fid,passage_id=pid,role='support');insert('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün yayın pasajı ve dönem incelendi.')
 return fid
pid=lambda s:case+'-'+s+'-p';call=pid('call-call');plan=pid('call-declaration');speech=pid('akdeniz-speech');welcome=pid('akdeniz-welcome');six=pid('august-six');aug=pid('august-plan');mee=pid('meeting-component');role=pid('meeting-role');guest=pid('meeting-guest');program=pid('program-published');news=pid('bianet-meeting');hour=pid('bianet-time');newsdec=pid('bianet-declaration');hdp=pid('hdp-meeting');dec=pid('hdp-declaration')
limit='14 Eylül Akdeniz çağrısı; 24 Eylül Haliç toplantısı; 25 Eylül EMEP konuşma/haber yayımı ve 26 Eylül program yayımı ayrı tarihlerdir. Bianet 15.24 yayımı 23.08 güncellenmiş; 15.30 başlangıç bilgisi erişilen güncel sürüme atfedilir. EMEP program sayfası 16 Şubat 2023 güncellemelidir. Yeşil Sol temsilcilerinin salonda bulunması altı kurucu bileşen içinde yer aldığı anlamına gelmez. Deklarasyon sonraki uygulama veya seçim sonucu değildir.'
summary=finding('call-summary','EMEP Genel Başkanı Ercüment Akdeniz, 14 Eylül 2022’de 24 Eylülde yapılacak ittifak halk buluşmasına çağırdı ve ortak deklarasyonun açıklanacağını söyledi.','summary',[call,plan],'Siyasal katılım',statement)
quote=finding('call-quote',passages[call]['exact'],'quote',[call],'Siyasal katılım',statement)
result=finding('result','24 Eylül 2022’de İstanbul Haliç Kongre Merkezinde Emek ve Özgürlük İttifakı halk buluşması yapıldı ve deklarasyon okundu. EMEP Genel Başkanı Ercüment Akdeniz konuştu.','summary',[news,newsdec,hdp,dec,speech],'Belgelenmiş uygulamalar',case+'-result')
explanation=finding('comparison','EMEP Genel Başkanı 14 Eylülde 24 Eylül halk buluşmasına çağırdı. Altı bileşenli ittifakın İstanbul Haliç buluşmasında deklarasyon okundu ve Akdeniz konuştu. Yeşil Sol temsilcileri toplantıda bulunanlar arasında ayrı gösterildi. EMEP konuşmayı 25 Eylülde ve program çerçevesini 26 Eylülde yayımladı.','summary',[call,plan,six,aug,news,hdp,dec,speech,role,guest,program],'Belgelenmiş uygulamalar',case+'-comparison')
institution=finding('institution','EMEP, Eylül sonunda halk buluşmasıyla ittifakı ilan etmeyi açıklayan altı kurucu yapıdan biridir. EMEP haberinde genel başkanı Akdeniz, ittifak bileşenleriyle salona giren temsilciler arasında yer alır.','summary',[six,aug,role],'Belgelenmiş uygulamalar',case+'-institution')
for lane in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='emep' and x['topic_id']==topic and x['research_kind']==lane);sid=cell['cell_id']
 if not any(x['id']==sid for x in records['practice_scope_v2']):add('practice_scope_v2',id=sid,party_id='emep',topic_id=topic,taxonomy_version=4,period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=lane,boundary_reason='2022 ittifak halk buluşması incelendi; kapsam açık.')
 if lane=='statement':ss=sid
 else:es=sid
add('practice_statement',id=statement,party_id='emep',topic_id=topic,taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at='2022-09-14',date_precision='day',version_id=case+'-call-v1',period_basis='14 Eylül 2022 EMEP yayımı 24 Eylül halk buluşması ve ortak deklarasyonu önceden adlandırır.',uncertainty_reason='Çağrı, sonraki deklarasyonun maddelerinin uygulandığını veya seçim sonuçlarını göstermez.',comparison_row_id='04-03-v3-03-v2-emep-demokrasi')
add('practice_event',id=event,common_event_key='halic-emek-ozgurluk-2022-09-24',event_at='2022-09-24',date_precision='day',date_unknown_reason=None,title='Emek ve Özgürlük İttifakı’nın Haliç halk buluşması',scope_context='24 Eylül 2022’de İstanbul Haliç Kongre Merkezi’nde düzenlenen Emek ve Özgürlük İttifakı halk buluşması ve deklarasyonun açıklanması.',occurrence_basis='24 Eylül 2022 tarihli Bianet haberi ve HDP yayını, Haliç Kongre Merkezi’ndeki halk buluşmasını ve deklarasyonun açıklanmasını bildiriyor.')
evidence={'august-six':('initiative','25 Ağustos ortak açıklamada EMEP dahil altı yapı adlandırılır.'),'august-plan':('initiative','Ortak açıklama Eylül sonunda halk buluşması planlar.'),'bianet-meeting':('action','Bianet güncellenen haberi Haliçte yol haritası buluşmasını bildirir.'),'bianet-declaration':('result','Bianet güncellenen haberi halk buluşmasında deklarasyonun açıklandığını bildirir.')}
for key,(stage,point) in evidence.items():
 p=pid(key);add('practice_event_evidence',event_id=event,passage_id=p,stage=stage,supported_point=point,concrete_basis=passages[p]['section'],limitation=limit,epistemic_type='claim');add('practice_evidence_assessment',event_id=event,passage_id=p,stage=stage,basis_kind='document')
add('practice_relation',id=relation,statement_id=statement,event_id=event,party_id='emep',topic_id=topic,scope_id=es,comparability_reason='Akdenizin 14 Eylülde çağırdığı 24 Eylül halk buluşması ve ortak deklarasyon ile aynı ittifakın Haliç buluşması karşılaştırılır.',target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,temporal_context='25 Ağustos ortak karar; 14 Eylül çağrı; 24 Eylül Haliç buluşması; 25 ve 26 Eylül EMEP yayımları.',authority_context='Çağrı EMEP Genel Başkanına, ortak karar altı bileşene; konuşma Akdenize ve deklarasyon ittifaka aittir. Yeşil Sol temsilcileri katılımcı olarak ayrı kaydedilir.',uncertainty_reason=limit)
add('practice_candidate',id=case+'-candidate',scope_id=es,event_id=event,relation_id=relation,state='eligible',reason='Aynı ittifakın belirli tarihli halk buluşması çağrısı, olay ve deklarasyon çeşitli yayınlarda belgelendi.',passage_ids=json.dumps([call,news,hdp,dec,speech]))
add('practice_contribution',id=case+'-contribution',event_id=event,party_id='emep',actor_id='0410-emep-institution',contribution_kind='task',finding_id=institution,authority_passage_id=None,membership_passage_id=None,responsibility_limit='EMEP altı bileşenden biridir; partinin tek başına düzenlediği veya sonraki program hedeflerinin gerçekleştiği çıkarılmaz. Akdenizin konuşması kendisine ayrıca atfedilir.')
for ver,v in versions.items():
 role_name=ver[len(case)+1:-3];scopes=(ss,es) if role_name in ('august','call') else (es,);sections=sorted({p['section'] for p in passages.values() if p['version_id']==ver})
 for scope in scopes:
  aid=ver+('-statement-reading' if scope==ss else '-event-reading');add('practice_scope_source',scope_id=scope,version_id=ver,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now);add('practice_attempt_v2',id=aid,scope_id=scope,attempted_at=now,query=v['original_url'],url=v['original_url'],result='examined',reason='İttifak çağrısı ve ilgili yayın metni okundu.',source_version_id=ver);add('practice_lead',id='lead-'+aid,scope_id=scope,url=v['original_url'],state='examined',relevance_reason='2022 Haliç buluşması ve ittifak açıklaması.',attempt_ids=json.dumps([aid]))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(r for r in rows if r not in data[table])
rules.validate_practices(data);targets=rules.practice_review_package_targets(data,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep');allp={p['id']:p for p in data['passage']};reviews=list(review['practice_source_review']);old={(r['subject_kind'],r['subject_id']) for r in reviews};assert old<=targets.keys()
for (kind,identity),(ids,_) in sorted(targets.items()):
 if (kind,identity) in old:continue
 ps=[allp[i] for i in sorted(ids)];claims=[evidence[k][1] for k in evidence if pid(k) in ids]
 if call in ids:claims.append('Akdeniz 14 Eylülde 24 Eylül halk buluşmasına çağırır.')
 if plan in ids:claims.append('Akdeniz ortak deklarasyonun seçim bildirgesi olmadığını belirtir.')
 if welcome in ids:claims.append('EMEP yayımladığı konuşmayı Akdenize atfeder.')
 if mee in ids:claims.append('EMEP haberi Haliç halk buluşmasını aktarır.')
 if hour in ids:claims.append('Güncellenmiş Bianet haberi 15.30 başlangıç bildirir.')
 if hdp in ids:claims.append('HDP yayını Haliç halk buluşmasını bildirir.')
 if dec in ids:claims.append('HDP yayını deklarasyonun okunduğunu bildirir.')
 if speech in ids:claims.append('EMEP yayını Haliç konuşmasını Akdenize atfeder.')
 if role in ids:claims.append('EMEP haberi Akdenizi ittifak bileşeni temsilcileri arasında belirtir.')
 if guest in ids:claims.append('EMEP haberi Yeşil Sol eş sözcülerinin salonda bulunduğunu ayrı belirtir.')
 if program in ids:claims.append('EMEP program çerçevesinin Haliçte açıklandığını yayımlar.')
 assert claims,(kind,identity,ids)
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in ps})),passage_ids=json.dumps([p['id'] for p in ps]),inspected_sections=json.dumps(sorted({p['section'] for p in ps}),ensure_ascii=False),supported_claim=' '.join(claims),limitations=limit,result='reviewed',reason=kind+' / '+identity+' için özgün kaynak incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs;review['practice_source_review']=reviews;review['source_review_refs']=refs
for name,obj in [('halic-2022-emep-draft.json',package),('halic-2022-emep-review-draft.json',review)]:
 with (c/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('HALIC2022_EMEP_SEMANTIC_OK',len(reviews),len(records['practice_event']),len(records['practice_relation']))
