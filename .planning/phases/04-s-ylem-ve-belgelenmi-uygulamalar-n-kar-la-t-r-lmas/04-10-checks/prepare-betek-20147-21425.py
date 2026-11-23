import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text
import uygulamalar as rules

D=Path(__file__).parent
read=lambda p: json.loads(Path(p).read_text())
package=read(D/'bekaert-26171-union-draft.json')
previous=read(D/'bekaert-26171-union-review-draft.json')
base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries,records=package['entries'],package['practice_records']
entries.extend(read(D/'betek-20147-21425-source-draft.json')['entries'])
now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='sendika-grev' and x['research_kind']=='event')
def add(k,**v): entries.append(dict(kind=k,values=v))
for num,date,notice,topic in [('20147','2024-12-05','1 Eylül 2025','sendikal yetki itirazı'),('21425','2024-12-26','24 Ekim 2025','işten çıkarma iddiaları ve sendikal yetki')]:
 stem='0410-emep-betek-'; detail=stem+'detail-'+num; question=stem+'question-'+num
 owner=detail+'-owner-p'; raw=(D/'betek-20147-21425'/('detail-'+num+'.html')).read_bytes(); exact='&#x130;skender BAYHAN'; assert exact in html_source_text(raw)
 add('passage',id=owner,version_id=detail+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Soru ve yanıt bildirim kaydı',pdf_page_index=None,printed_page=None)
 eid='0410-betek-'+num+'-event'; rid='0410-betek-'+num+'-relation'; fid='0410-betek-'+num+'-explanation'
 add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Program sendika ve grev hakkını savunur. İskender Bayhan Betek Boya hakkında '+topic+' konulu yazılı soru verdi; TBMM kaydı bakanlık yanıtının bildirildiğini gösterir.',provenance='summary',epistemic_type='claim')
 add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program, resmi kayıt, imzalı soru ve taranmış yanıt incelendi; iddialar ve yanıt ayrı tutuldu.')
 pids=['0309-emep-program-006-1-passage',detail+'-number-p',detail+'-date-p',detail+'-reply-p',owner,question+'-p']
 for p in pids:
  add('finding_evidence',finding_id=fid,passage_id=p,role='support')
  add('verification',finding_id=fid,passage_id=p,checked_at=now,result='confirmed',reason='Program veya resmi soru ve yanıt kaydı okundu.')
 records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-3-7-'+num+'-betek-sendikal-haklar',event_at=date,date_precision='day',date_unknown_reason=None,scope_context='TBMM Betek Boya '+topic+' yazılı soru ve yanıt kaydı',title='Betek Boya '+topic+' hakkında yazılı soru',occurrence_basis='TBMM soru kaydı Bayhanı, konuyu ve başkanlığa geliş gününü bildirir.'))
 for p,point in [(detail+'-number-p','TBMM 7/'+num+' sayılı yazılı soru kaydıdır.'),(detail+'-date-p','Soru belirtilen günde başkanlığa geldi.'),(owner,'Soru sahibi İstanbul Milletvekili İskender Bayhandır.'),(question+'-p','İmzalı soru Betek işyerindeki sendikal hakları gündeme getirir.'),(detail+'-reply-p','TBMM kaydına göre yanıt '+notice+' tarihinde bildirildi.')]:
  records['practice_event_evidence'].append(dict(event_id=eid,passage_id=p,supported_point=point,stage='action',concrete_basis='TBMM resmi soru kaydı ve imzalı soru.',limitation='Soru, iddiaların doğrulandığını ya da işten çıkarılanların işe döndüğünü göstermez.',epistemic_type='claim'))
  records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=p,stage='action',basis_kind='document'))
 records['practice_relation'].append(dict(id=rid,statement_id='0410-labor-statement',event_id=eid,party_id='emep',topic_id='sendika-grev',scope_id=scope,comparability_reason='Program sendikal hakları savunur; soru işyerindeki sendikal yetkiyi konu alır.',target_finding_id='0410-labor-statement-finding',result_finding_id=None,explanation_finding_id=fid,temporal_context='Programın 2023 arşivi, 2024 soru ve 2025 yanıtı ayrı tarihlerdir.',authority_context='Soru Bayhana; yanıt Çalışma ve Sosyal Güvenlik Bakanlığına aittir.',uncertainty_reason='Soru iddiaların doğruluğunu veya işçilerin işe dönüşünü göstermez; programın 2024te kesintisiz yürürlüğü kanıtlanmadı.'))
 records['practice_candidate'].append(dict(id='0410-betek-'+num+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='TBMM özgün soru ve yanıt kayıtları incelendi.',passage_ids=json.dumps(pids[1:])))
 for role in ('detail','question','reply'):
  v=stem+role+'-'+num+'-v1'; version=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==v)
  section='Soru ve yanıt bildirim kaydı' if role=='detail' else 'İmzalı soru' if role=='question' else 'Bakanlık yanıtı'; aid='0410-betek-'+num+'-'+role+'-attempt'
  records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now))
  records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=version['original_url'],relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])))
  records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=version['original_url'],url=version['original_url'],result='examined',reason='TBMM kayıt veya sayfaları okundu; fiilî sonuç ayrı.',source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items(): data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='emep')
passages={p['id']:p for p in data['passage']}; old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']}; reviews=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
 if (kind,identity) in old: reviews.append(old[(kind,identity)]); continue
 inspected=[passages[x] for x in sorted(ids)]
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program ve TBMM kayıt pasajları incelendi.',limitations='Soru ve yanıt iddiaların doğrulanması veya işe dönüş sonucu olarak değerlendirilmez.',result='reviewed',reason=kind+' / '+identity+' için kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets)); refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs
for name,obj in [('betek-20147-21425-union-draft.json',package),('betek-20147-21425-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('BETEK_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
