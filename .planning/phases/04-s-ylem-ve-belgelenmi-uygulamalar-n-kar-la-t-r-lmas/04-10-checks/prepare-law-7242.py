import copy, json, sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
checks=Path(__file__).resolve().parent; now=datetime.now(timezone.utc).isoformat(timespec='seconds')
read=lambda p:json.loads(Path(p).read_bytes())
package=read('data/practices/04-emep.json'); review=read('data/practices/04-emep-review.json'); base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json'); inv=read('data/practices/04-inventory.json')
entries=package['entries']; records=package['practice_records']; assert (len(records['practice_event']),len(records['practice_relation']))==(75,72); assert not records['practice_closure']; assert not any('7242' in str(v) or '2762' in str(v) for v in records['practice_event'])
case='0410-law-7242'; topic='cezaevleri'; event=case+'-event'; relation=case+'-relation'; statement=case+'-statement'; sources=read(checks/'law-7242-source-draft.json')['entries']; entries.extend(sources)
passages={e['values']['id']:e['values'] for e in sources if e['kind']=='passage'}; versions={e['values']['id']:e['values'] for e in sources if e['kind']=='document_version'}
def add(table,**v):records[table].append(v)
def insert(table,**v):entries.append({'kind':table,'values':v})
def finding(suffix,text,provenance,refs,heading,pair):
 fid=case+'-'+suffix; insert('finding',id=fid,party_id='emep',heading=heading,pair_id=pair,text=text,provenance=provenance,epistemic_type='claim'); insert('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Özgün parti açıklaması, TBMM tutanağı veya kanun maddesi incelendi; işlem ve tarih ayrımı korundu.')
 for pid in refs: insert('finding_evidence',finding_id=fid,passage_id=pid,role='support'); insert('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='İlgili özgün kaynak pasajı okundu.')
 return fid
pid=lambda s:case+'-'+s+'-p'
prior=[pid('prior-request'),pid('prior-author')]; resultrefs=[pid('proposal-number'),pid('proposal-sequence'),pid('proposal-law'),pid('floor-vote'),pid('floor-accepted'),pid('registry-adoption'),pid('registry-publication'),pid('registry-issue')]
summary=finding('request-summary','Selma Gürkan, 8 Nisan 2020’de infaz düzenlemesinin geri çekilmesini ve tutuklu ile hükümlülerin salgın güvenliğinin sağlanmasını istedi.','summary',prior,'Cezaevleri',statement)
quote=finding('request-quote',passages[pid('prior-request')]['exact'],'quote',[pid('prior-request')],'Cezaevleri',statement)
result=finding('result','TBMM Genel Kurulu infaz teklifini 14 Nisan 2020’de 279 kabul ve 51 retle kabul etti; 7242 sayılı kanun 15 Nisan tarihli 31100 sayılı Resmî Gazetede yayımlandı.','summary',resultrefs,'Belgelenmiş uygulamalar',case+'-result')
explanation=finding('comparison','Gürkan’ın geri çekme çağrısından sonra infaz düzenlemesi kabul edildi. 13 Nisan’da açılan birleşimin 14 Nisan oylamasında basılı cetvel saat 00.09 ve 279/51/330 gösterir; 15 Nisan yayımı ayrıdır. 48. madde koşullu salıverilme oranlarını düzenler. 52. madde, 30 Mart tarihine kadar işlenen suçlara ilişkin geçici denetimli serbestlikten Terörle Mücadele Kanunu kapsamındaki suçlar dahil belirli suçları hariç tutar. 53. madde disiplin ve belirli hükümlüler için salgın iznini ayrı düzenler. Bireysel tahliye veya parti oyu gösterilmedi.','summary',prior+resultrefs+[pid('floor-opening'),pid('printed-header'),pid('law-m48'),pid('law-m48-exceptions'),pid('law-m52-date'),pid('law-m52-exclusions'),pid('law-m53-leave'),pid('law-m53-discipline')],'Belgelenmiş uygulamalar',case+'-comparison')
for lane in ('statement','event'):
 c=next(c for c in inv['cells'] if c['party_id']=='emep' and c['topic_id']==topic and c['research_kind']==lane); sid=c['cell_id']
 if not any(s['id']==sid for s in records['practice_scope_v2']): add('practice_scope_v2',id=sid,party_id='emep',topic_id=topic,taxonomy_version=4,period_start=c['period_start'],cutoff_at=c['cutoff_at'],research_kind=lane,boundary_reason='7242 infaz teklifi ve açıklamalar incelendi; kapsam ve diğer konular açık.')
 if lane=='statement': ss=sid
 else: es=sid
add('practice_statement',id=statement,party_id='emep',topic_id=topic,taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at='2020-04-08',date_precision='day',version_id=case+'-prior-v1',period_basis='8 Nisan 2020 parti sayfası yayımı; açıklama oylamadan öncedir.',uncertainty_reason='Açıklama EMEP adına Genel Başkan çağrısıdır; parti oyu veya sonuç üzerindeki etkisini göstermez.',comparison_row_id='04-03-v3-0309-emep-program-scope-023-row')
add('practice_event',id=event,common_event_key='tbmm-27-3-84-2-2762-law-7242',event_at='2020-04-14',date_precision='day',date_unknown_reason=None,scope_context='TBMM 27. dönem 3. yasama yılı 84. birleşim, 2/2762, 207 sıra',title='7242 sayılı infaz kanunu teklifinin kabulü',occurrence_basis='13 Nisanda açılan birleşim gece yarısını geçti; 14 Nisan oylamasında 279 kabul, 51 ret, toplam 330 oy ve 7242 sicilinde kabul günü 14 Nisandır. Basılı cetvelde saat 00.09 görsel olarak okundu.')
evidence={
 'proposal-number':('action','TBMM sicili 2/2762 esas numarasını kaydeder.'), 'proposal-sequence':('action','Aynı teklif sicilinde sıra sayısı 207dir.'), 'proposal-law':('action','Teklif sicili 7242 kanununa bağlanır.'),
 'floor-opening':('action','84. birleşim 13 Nisan başlığıyla açıldı; gece yarısından sonra sürmesi kapanıştan anlaşılır.'),
 'floor-request':('action','207 sıra teklifinin tümü için açık oylama istendi.'),'floor-vote':('action','Tutanak 330 oy, 279 kabul ve 51 ret kaydeder.'),
 'floor-accepted':('action','Tutanak teklifin kabul edildiğini açıklar ve birleşimin 00.17de kapandığını gösterir.'),
 'printed-header':('action','Basılı sayfa 383 başlığı metin katmanındadır; cetvel görselinde saat 00.09 ve toplamlar okundu.'),
 'registry-adoption':('result','TBMM sicili kabul gününü 14 Nisan gösterir.'),'registry-publication':('result','TBMM sicili yayım gününü 15 Nisan gösterir.'),'registry-issue':('result','TBMM sicili Resmî Gazete sayısını 31100 gösterir.'),
 'law-m48':('result','48. madde koşullu salıverilme genel oranını değiştirir.'),'law-m48-exceptions':('result','48. maddede belirli suç kategorileri için üçte iki düzenlenir.'),
 'law-m52-date':('result','52. madde 30 Mart 2020ye kadar işlenmiş suçlar için düzenleme yapar.'),'law-m52-exclusions':('result','52. maddedeki süreye ilişkin istisnalar arasında Terörle Mücadele Kanunu kapsamı vardır.'),
 'law-m53-leave':('result','53. madde belirli hükümlüleri 31 Mayısa kadar salgın izninde sayar.'),'law-m53-discipline':('result','53. madde disiplin tedbirleri için ayrı hükümler içerir.'),
 'joint-sign':('initiative','6 Nisan ortak açıklamada EMEP imzacılardan biridir.'),'after-accepted':('initiative','14 Nisan EMEP genel merkez açıklaması Meclis kabulünü eleştirir.'),
}
limit='Basılı cetvelin saat ve oylar tablosu görsel okundu; metin katmanı yalnız başlığı içerir. Sicil kabul gününü, tutanak toplamları doğrular. Kanun maddeleri ayrı rejimlerdir; kişisel tahliye, parti oyu ve nedensellik gösterilmedi.'
for key,(stage,point) in evidence.items():
 p=pid(key); add('practice_event_evidence',event_id=event,passage_id=p,stage=stage,supported_point=point,concrete_basis=passages[p]['section'],limitation=limit,epistemic_type='claim'); add('practice_evidence_assessment',event_id=event,passage_id=p,stage=stage,basis_kind='party_announcement' if stage=='initiative' else 'document')
add('practice_relation',id=relation,statement_id=statement,event_id=event,party_id='emep',topic_id=topic,scope_id=es,comparability_reason='8 Nisan çağrısı ve 2/2762 kabulü aynı dönemde Genel Kurulda görüşülen infaz düzenlemesidir.',target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,temporal_context='6 Nisan ortak bağlam, 8 Nisan çağrı, 14 Nisan 00.09 oylama, 14 Nisan sonraki açıklama ve 15 Nisan yayımı.',authority_context='Çağrı Gürkan ve EMEPindir; karar TBMM Genel Kurulunundur. Parti oyu, yetki veya nedensellik çıkarılmaz.',uncertainty_reason=limit)
add('practice_candidate',id=case+'-candidate',scope_id=es,event_id=event,relation_id=relation,state='eligible',reason='Teklifin geri çekilmesi çağrısı ve aynı infaz teklifinin kabulü kaynak ve tarihle bağlandı.',passage_ids=json.dumps([pid('floor-vote'),pid('floor-accepted'),pid('registry-adoption'),pid('registry-publication')]))
for ver,v in versions.items():
 role=ver[len(case)+1:-3]; scopes=(ss,es) if role in ('joint','prior','after') else (es,); sections=sorted({p['section'] for p in passages.values() if p['version_id']==ver})
 for scope in scopes:
  aid=ver+('-statement-reading' if scope==ss else '-event-reading'); add('practice_scope_source',scope_id=scope,version_id=ver,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now); add('practice_attempt_v2',id=aid,scope_id=scope,attempted_at=now,query=v['original_url'],url=v['original_url'],result='examined',reason='Özgün gövde, tutanak sayfası veya kanun maddesi incelendi.',source_version_id=ver); add('practice_lead',id='lead-'+aid,scope_id=scope,url=v['original_url'],state='examined',relevance_reason='7242 açıklama, kabul, yayım ve maddeler.',attempt_ids=json.dumps([aid]))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items(): data.setdefault(table,[]).extend(r for r in rows if r not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep'); allp={p['id']:p for p in data['passage']}; reviews=list(review['practice_source_review']); old={(r['subject_kind'],r['subject_id']) for r in reviews}; assert old<=targets.keys()
for (kind,identity),(ids,_) in sorted(targets.items()):
 if (kind,identity) in old: continue
 ps=[allp[i] for i in sorted(ids)]; claims=[evidence[k][1] for k in evidence if pid(k) in ids]
 if pid('prior-request') in ids: claims.append('Gürkan infaz düzenlemesinin geri çekilmesini istedi.')
 if pid('prior-author') in ids: claims.append('Açıklama Gürkan imzasını taşıyor.')
 if pid('law-m68') in ids: claims.append('Kanun yayımı tarihinde yürürlüğe girer.')
 assert claims,(kind,identity,ids)
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in ps})),passage_ids=json.dumps([p['id'] for p in ps]),inspected_sections=json.dumps(sorted({p['section'] for p in ps}),ensure_ascii=False),supported_claim=' '.join(claims),limitations=limit,result='reviewed',reason=kind+' / '+identity+' için özgün kaynak incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets)); refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs; review['practice_source_review']=reviews; review['source_review_refs']=refs
for name,obj in [('law-7242-draft.json',package),('law-7242-review-draft.json',review)]:
 with (checks/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('LAW7242_SEMANTIC_OK',len(reviews),len(records['practice_event']),len(records['practice_relation']))
