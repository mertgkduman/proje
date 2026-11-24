import copy,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
c=Path(__file__).resolve().parent;now=datetime.now(timezone.utc).isoformat(timespec='seconds');read=lambda p:json.loads(Path(p).read_bytes())
package=read('data/practices/04-emep.json');review=read('data/practices/04-emep-review.json');base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json');inv=read('data/practices/04-inventory.json');entries=package['entries'];records=package['practice_records'];assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(80,77,0)
case='0410-ankara-workshop';event=case+'-event';finding=case+'-finding';contribution=case+'-contribution';candidate=case+'-candidate';actor='0410-emep-institution';topic='demokrasi-katilim';sources=read(c/'ankara-workshop-emep-source-draft.json')['entries'];entries.extend(sources);passages={e['values']['id']:e['values'] for e in sources if e['kind']=='passage'};versions={e['values']['id']:e['values'] for e in sources if e['kind']=='document_version'}
def add(table,**v):records[table].append(v)
def insert(table,**v):entries.append({'kind':table,'values':v})
cell=next(x for x in inv['cells'] if x['party_id']=='emep' and x['topic_id']==topic and x['research_kind']=='event');scope=cell['cell_id']
if not any(x['id']==scope for x in records['practice_scope_v2']):add('practice_scope_v2',id=scope,party_id='emep',topic_id=topic,taxonomy_version=4,period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind='event',boundary_reason='Ankara ortak çalıştayı incelendi; araştırma kapsamı açık.')
if not any(e['kind']=='actor' and e['values']['id']==actor for e in entries):insert('actor',id=actor,kind='institution',party_id='emep',person_id=None,authorization_passage_id=None)
pids=[case+'-emep-p',case+'-dem-p',case+'-ilke-p'];limit='EMEP altı ortak düzenleyiciden biridir; tek düzenleyici veya uygulama sahibi değildir. 3 Kasım EMEP ve DEM sayfalarının yayım günüdür; sonuçların ilk açıklanma günü ya da önerilerin uygulanması değildir. Önceki genel birleşik mücadele çağrısı bu çalıştayı tarih veya adla belirtmez; somut öncül eşleşmesi kurulmadı.'
insert('finding',id=finding,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=finding,text='EMEP, DEM Parti, EHP, SMF, TİP ve TÖP 1–2 Kasım 2025’te Ankara’da Demokrasi ve Barış çalıştayını ortak düzenledi. İlke TV 2 Kasımda ikinci günün sürdüğünü bildirdi; EMEP ve DEM Parti 3 Kasımda ortak sonuç metnini yayımladı. Metindeki taleplerin yayımlanması, uygulandıklarını göstermez.',provenance='summary',epistemic_type='claim')
insert('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Ortak düzenleme ve bağımsız haber okundu; yayın, toplantı ve politika sonuçları ayrıldı.')
add('practice_event',id=event,common_event_key='ankara-2025-11-01-02-demokrasi-baris-calistayi',event_at='2025-11-01',date_precision='day',date_unknown_reason=None,title='Ankara Demokrasi ve Barış Çalıştayı',scope_context='DEM Parti, EHP, EMEP, SMF, TİP ve TÖP tarafından Ankara’da 1–2 Kasım 2025’te düzenlenen ortak çalıştay.',occurrence_basis='DEM 3 Kasım ortak metni ve İlke TV 2 Kasım ikinci gün haberi.')
for role,stage,point in [('emep','initiative','EMEP ortak düzenlemeyi ve 3 Kasım sonuç metnini yayımlar.'),('dem','initiative','DEM metni altı düzenleyici, Ankara ve 1–2 Kasım tarihlerini belirtir.'),('ilke','action','İlke TV 2 Kasımda Ankarada ikinci günün sürdüğünü ve altı ortak düzenleyiciyi bildirir.')]:
 p=case+'-'+role+'-p';insert('finding_evidence',finding_id=finding,passage_id=p,role='support');insert('verification',finding_id=finding,passage_id=p,checked_at=now,result='confirmed',reason='Özgün metin ve olay-yayın tarihi ayrımı incelendi.');add('practice_event_evidence',event_id=event,passage_id=p,stage=stage,supported_point=point,concrete_basis=passages[p]['section'],limitation=limit,epistemic_type='claim');add('practice_evidence_assessment',event_id=event,passage_id=p,stage=stage,basis_kind='document')
add('practice_contribution',id=contribution,event_id=event,party_id='emep',actor_id=actor,contribution_kind='task',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='EMEP altı ortak düzenleyiciden biridir; sonuç metni taleplerinin uygulandığı veya etkinliği tek başına düzenlediği çıkarılmaz.')
add('practice_candidate',id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Eylül genel birleşik mücadele çağrısı bu çalıştayı ad veya tarihle belirlemez; önceki bağımsız somut söylem eşleşmesi açık.',passage_ids=json.dumps(pids))
for ver,v in versions.items():
 sections=sorted({p['section'] for p in passages.values() if p['version_id']==ver});aid=ver+'-event-reading';add('practice_scope_source',scope_id=scope,version_id=ver,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now);add('practice_attempt_v2',id=aid,scope_id=scope,attempted_at=now,query='1–2 Kasım Ankara demokrasi barış çalıştayı',url=v['original_url'],result='examined',reason='Ortak düzenleme, ikinci gün ve yayım tarihleri ayrı incelendi.',source_version_id=ver);add('practice_lead',id='lead-'+aid,scope_id=scope,url=v['original_url'],state='examined',relevance_reason='Altı kurumun ortak çalıştayı ve sonuç metni.',attempt_ids=json.dumps([aid]))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(r for r in rows if r not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep');allp={p['id']:p for p in data['passage']};reviews=list(review['practice_source_review']);old={(r['subject_kind'],r['subject_id']) for r in reviews};assert old<=targets.keys()
for (kind,identity),(ids,_) in sorted(targets.items()):
 if (kind,identity) in old:continue
 ps=[allp[i] for i in sorted(ids)];assert ids
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in ps})),passage_ids=json.dumps([p['id'] for p in ps]),inspected_sections=json.dumps(sorted({p['section'] for p in ps}),ensure_ascii=False),supported_claim='1–2 Kasım Ankara ortak çalıştayı, EMEPin altı düzenleyiciden biri olduğu ve ilgili yayım veya haber günü kaynakta belirtildi.',limitations=limit,result='reviewed',reason=kind+' / '+identity+' için özgün kaynak incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs;review['practice_source_review']=reviews;review['source_review_refs']=refs
for name,obj in [('ankara-workshop-emep-draft.json',package),('ankara-workshop-emep-review-draft.json',review)]:
 with (c/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('ANKARA_WORKSHOP_EMEP_SEMANTIC_OK',len(reviews),len(records['practice_event']),len(records['practice_relation']))
