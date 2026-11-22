import copy,datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent;read=lambda p:json.loads(Path(p).read_text())
package=read(D/'institution-agriculture-union-draft.json');previous=read(D/'institution-agriculture-union-review-draft.json');base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries,records=package['entries'],package['practice_records'];now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
entries.extend(read(D/'kocaeli-discipline-source-draft.json')['entries'])
pid='0410-emep-kocaeli-2026-congress-ozgun-discipline-p';eid='0410-kocaeli-2026-congress-event';rid='0410-kocaeli-discipline-2026-relation';result='0410-kocaeli-discipline-2026-result';explanation='0410-kocaeli-discipline-2026-explanation';program='0309-emep-html-019-0-passage'
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='il-disiplin-kurulu' and x['research_kind']=='event')
def add(k,**v):entries.append(dict(kind=k,values=v))
def finding(fid,text,pids):
 add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text=text,provenance='summary',epistemic_type='claim');add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Tüzük ve 1 Kasım yerel haberdeki kurul bilgisi ayrı okundu.')
 for p in pids:add('finding_evidence',finding_id=fid,passage_id=p,role='support');add('verification',finding_id=fid,passage_id=p,checked_at=now,result='confirmed',reason='İlgili tüzük veya kongre haber pasajı okundu.')
finding(result,'Özgün Kocaeli, il kongresinde Osman Nuri Şenol, Ahmet Orhan Tüzmen ve Nizam Umur’un il disiplin kurulu üyesi olarak belirlendiğini bildirdi.',[pid])
finding(explanation,'Tüzük il disiplin kurulunu üç üyeli düzenler. Özgün Kocaeli, Kocaeli kongresinde üç kurul üyesinin belirlendiğini aktardı.',[program,pid])
for stage in ['action','result']:
 records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,supported_point='1 Kasım haberinde aynı kongrede üç il disiplin kurulu üyesinin belirlendiği bildiriliyor.',stage=stage,concrete_basis='Bahar Özdemir imzalı Özgün Kocaeli kongre haberi.',limitation='Kurul üyelerinin nasıl oylandığı, seçim tutanağı ve tüzüğün 2026 ara sürümü görülmedi.',epistemic_type='claim'))
 records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id='0410-il-disiplin-statement',event_id=eid,party_id='emep',topic_id='il-disiplin-kurulu',scope_id=scope,comparability_reason='İl disiplin kurulunun bileşimi ve aynı il kongresinde bildirilen kurul üyeleri aynı konudadır.',target_finding_id='0410-il-disiplin-finding',result_finding_id=result,explanation_finding_id=explanation,temporal_context='2019/2020 parti tüzüğü yayını ile 1 Kasım 2026 kongre haberi ayrı tarihlidir.',authority_context='Tüzük il kongresinin üç üyeli kurulu gizli oyla seçmesini öngörür.',uncertainty_reason='Haber üç üye bildirir; gizli oy veya 2026’da kesintisiz yürürlük ayrıca doğrulanmadı.'))
records['practice_candidate'].append(dict(id='0410-kocaeli-discipline-2026-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='Aynı il kongresindeki il disiplin kurulu üyeleri kaynakta belirtiliyor.',passage_ids=json.dumps([pid])))
version='0410-emep-kocaeli-2026-congress-ozgun-v1';url='https://www.ozgunkocaeli.com.tr/ilhami-sahbaz-yeniden-il-baskani-secildi';aid='0410-kocaeli-discipline-2026-attempt';section='İl disiplin kurulu üyeleri'
records['practice_scope_source'].append(dict(scope_id=scope,version_id=version,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason='1 Kasım özgün haber okundu; gizli oy ve tüzük ara sürümü açık.',source_version_id=version))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);newpass={x['passage_id'] for x in records['practice_event_evidence']};targets=rules.practice_review_package_targets(data,records,newpass,party_id='emep');passages={x['id']:x for x in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[];changed=[]
for key,(pids,parties) in sorted(targets.items()):
 if key in old:
  r=copy.deepcopy(old[key]);before=set(json.loads(r['passage_ids']))
  if before!=pids:
   assert key in {('practice_event',eid),('practice_relation','0410-kocaeli-2026-congress-relation')} and before<=pids
   r['passage_ids']=json.dumps(sorted(pids));r['source_version_ids']=json.dumps(sorted({passages[x]['version_id'] for x in pids}));r['inspected_sections']=json.dumps(sorted({passages[x]['section'] for x in pids}),ensure_ascii=False);r['supported_claim']+=' Aynı kongrede üç disiplin kurulu üyesi ayrıca bildiriliyor.';r['limitations']+=' Kurul üyelerinin gizli oy yöntemi haberden çıkarılmaz.';r['reason']+=' Ek kurul pasajı yeniden okundu.';changed.append(key)
  reviews.append(r);continue
 inspected=[passages[x] for x in sorted(pids)]
 reviews.append(dict(subject_kind=key[0],subject_id=key[1],reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Tüzük il disiplin kurulunu üç üyeli düzenler; haber Kocaeli kongresinde üç üyeyi bildirir.',limitations='Gizli oy yöntemi ve tüzüğün 2026 ara sürümü doğrulanmadı.',result='reviewed',reason=key[0]+' / '+key[1]+' için ilgili tüzük ve haber pasajları okundu.'))
assert set(changed)=={('practice_event',eid),('practice_relation','0410-kocaeli-2026-congress-relation')}
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for n,obj in [('kocaeli-discipline-union-draft.json',package),('kocaeli-discipline-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs)),('kocaeli-discipline-union-notes.json',dict(same_event=eid,updated_review_subjects=changed,old_review_passages_are_subset=True,limits='Kurul üyeleri bildiriliyor; gizli oy ve ara tüzük yürürlüğü bilinmiyor.'))]:
 with (D/n).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('KOCAELI_DISCIPLINE_PACKAGE_TARGET_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
