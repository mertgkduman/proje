import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
import uygulamalar as rules

D = Path(__file__).parent
read = lambda path: json.loads(Path(path).read_text())
package = read('data/practices/04-emep.json')
previous = read('data/practices/04-emep-review.json')
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
inventory = read('data/practices/04-inventory.json')
entries, records = package['entries'], package['practice_records']
assert len(records['practice_event']) == 68 and len(records['practice_relation']) == 70
assert not any('melih bulu' in str(v).lower() or 'boğaziçi' in str(v).lower() for v in records['practice_event'])
entries.extend(read(D/'bulu-2021-source-v2-draft.json')['entries'])
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
cell = next(c for c in inventory['cells'] if c['party_id']=='emep' and c['topic_id']=='yuksekogretim' and c['research_kind']=='event')
scope = cell['cell_id']
if not any(s['id']==scope for s in records['practice_scope_v2']):
    records['practice_scope_v2'].append(dict(id=scope, party_id='emep', topic_id='yuksekogretim', taxonomy_version=4, period_start=cell['period_start'], cutoff_at=cell['cutoff_at'], research_kind='event', boundary_reason='Resmî rektör görevden alma kararı ve EMEP MYK açıklaması incelendi; bütün diğer olay ve kaynaklar açık.'))
official='0410-emep-bulu-2021-official-p'; party='0410-emep-bulu-2021-party-p'; tbmm='0410-emep-bulu-2021-tbmm-p'; eid='0410-bulu-dismissal-2021-event'
records['practice_event'].append(dict(id=eid,common_event_key='cb-2021-360-bogazici-bulu-dismissal',event_at='2021-07-14',date_precision='day',date_unknown_reason=None,scope_context='Boğaziçi Üniversitesi rektörlüğü',title='Melih Bulu’nun rektörlükten görevden alınması',occurrence_basis='14 Temmuz tarihli Cumhurbaşkanı kararı 15 Temmuz mükerrer Resmî Gazetede yayımlandı.'))
for pid, stage, basis, point in [(official,'action','document','Resmî Gazetede 14 Temmuz 2021 tarihli 2021/360 kararı yayımlandı; görsel sayfa görevden alma işlemini içeriyor.'),(tbmm,'action','document','TBMM tutanağında Garo Paylan Bulu’nun görevden alındığını söylüyor.'),(party,'initiative','party_announcement','EMEP MYK açıklaması mücadeleyi anlatırken Bulu için istifa ifadesini kullanır.')]:
    records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,supported_point=point,concrete_basis='Resmî karar' if pid==official else 'EMEP MYK açıklaması',limitation='Parti açıklaması 2 Ağustostadır ve işlem türündeki ifadesi resmî görevden alma kararından farklıdır; karar gerekçe veya parti katkısı belirtmez.',epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
for pid, role, day in [(official,'official','2021-07-15'),(party,'party','2021-08-02'),(tbmm,'tbmm','2021-11-02')]:
    v=next(x['values'] for x in entries if x['kind']=='document_version' and x['values']['id']=='0410-emep-bulu-2021-'+role+'-v1')
    aid='0410-bulu-2021-'+role+'-reading'
    records['practice_scope_source'].append(dict(scope_id=scope,version_id=v['id'],inspected_sections=json.dumps([{'official':'2021/360 sayılı karar','party':'Yükseköğretim ve mücadele','tbmm':'Garo Paylan komisyon konuşması'}[role]],ensure_ascii=False),inspected_at=now))
    records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=v['original_url'],url=v['original_url'],result='examined',reason='Özgün karar görsel veya parti açıklaması gerçek gövde okumasıyla incelendi.',source_version_id=v['id']))
    records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=v['original_url'],relevance_reason='Rektörlük kararı ve parti açıklamasının farklı işlem türleri.',state='examined',attempt_ids=json.dumps([aid])))
reason=('Parti programının 0309-emep-program-014-0 pasajı özerk, bilimsel ve demokratik üniversite önerir; kabul ve tarihsel yürürlük günü bilinmiyor. Bu karar Cumhurbaşkanına aittir; partiye uygulama veya neden atfedilemez. EMEP MYK aynı gelişmeye ilişkin istifa ifadesini kullanır, resmî karar görevden alma der.')
records['practice_candidate'].append(dict(id='0410-bulu-2021-unmatched',scope_id=scope,event_id=eid,relation_id=None,state='unmatched',reason=reason,passage_ids=json.dumps([official,party,tbmm])))
def add(table, **values): entries.append(dict(kind=table,values=values))
fid='0410-bulu-2021-conflict-finding'; did='0410-bulu-2021-conflict'
add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Cumhurbaşkanı kararı Melih Bulu’nun rektörlükten görevden alındığını belirtir; EMEP MYK açıklaması aynı gelişmeyi istifa olarak adlandırır. Karar, partiye yetki veya sonucun nedeni hakkında bilgi vermez.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Resmî kararın görsel sayfası ve MYK açıklaması incelendi; işlem türü farkı ve yetki sınırı korundu.')
for pid in [official,party,tbmm]:
    add('finding_evidence',finding_id=fid,passage_id=pid,role='support')
    add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='İşlem türü iki özgün kaynakta ayrı okundu.')
records['practice_dispute'].append(dict(id=did,event_id=eid,supported_points='2021/360 sayılı karar görevden alma işlemidir.',disputed_points='EMEP MYK aynı gelişme için istifa ifadesi kullanır.',unresolved_points='Karar gerekçe belirtmez; partiye kurumsal yetki veya görevden almanın nedeni atfedilemez.',summary_finding_id=fid))
for pid,role,position in [(tbmm,'support','TBMM konuşmasında Paylan görevden alma der.'),(party,'conflict','MYK açıklaması istifa der.')]:
    records['practice_dispute_evidence'].append(dict(dispute_id=did,passage_id=pid,point='İşlemin niteliği',source_position=position,role=role))
data=copy.deepcopy(base)
for e in entries:
    if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items(): data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep')
passages={p['id']:p for p in data['passage']}; old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']}; reviews=[]
for (kind,identity),(ids,owners) in sorted(targets.items()):
    if (kind,identity) in old: reviews.append(old[(kind,identity)]); continue
    inspected=[passages[x] for x in sorted(ids)]
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Resmî karar görevden alma; parti açıklaması istifa diyor.',limitations='Resmî kararda neden veya parti yetkisi bulunmaz; programın kesin yürürlük tarihi bilinmiyor.',result='reviewed',reason=kind+' / '+identity+' için ilgili özgün pasajlar okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets))
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs
for name,obj in [('bulu-2021-v2-union-draft.json',package),('bulu-2021-v2-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('BULU_SEMANTIC_OK',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
