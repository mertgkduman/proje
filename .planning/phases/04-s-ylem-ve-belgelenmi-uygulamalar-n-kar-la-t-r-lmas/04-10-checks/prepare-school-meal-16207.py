import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text
import uygulamalar as rules

D = Path(__file__).parent
read = lambda p: json.loads(Path(p).read_text())
package = read(D/'betek-20147-21425-union-draft.json')
previous = read(D/'betek-20147-21425-union-review-draft.json')
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries, records = package['entries'], package['practice_records']
entries.extend(read(D/'school-meal-16207-source-draft.json')['entries'])
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
scope = next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='egitime-erisim' and x['research_kind']=='event')
def add(k, **v): entries.append(dict(kind=k, values=v))
stem = '0410-emep-school-meal-16207-'
detail = stem+'detail'
owner = detail+'-owner-p'
raw = (D/'school-meal-16207-detail.html').read_bytes()
exact = 'Sevda KARACA DEM&#x130;R'
assert exact in html_source_text(raw)
add('passage', id=owner, version_id=detail+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='Soru ve cevap bildirimi', pdf_page_index=None, printed_page=None)
eid, rid, fid = '0410-school-meal-16207-event', '0410-school-meal-16207-relation', '0410-school-meal-16207-explanation'
add('finding', id=fid, party_id='emep', heading='Belgelenmiş uygulamalar', pair_id=fid, text='Parti programı ücretsiz eğitimi savunur. Sevda Karaca Demir, okullarda ücretsiz yemek için Bakanlığa iletilen dilekçelerin akıbetini yazılı soruyla sordu; TBMM kaydı yanıtın bildirildiğini gösterir.', provenance='summary', epistemic_type='claim')
add('review', id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program, TBMM soru kaydı, imzalı soru, komisyon tutanağı ve taranmış yanıt okundu; tarih farkı ve yanıtın kapsamı ayrı tutuldu.')
pids = ['0309-emep-program-012-0-passage', detail+'-number-p', detail+'-date-p', detail+'-reply-p', owner, stem+'question-p', stem+'commission-p']
for p in pids:
    add('finding_evidence', finding_id=fid, passage_id=p, role='support')
    add('verification', finding_id=fid, passage_id=p, checked_at=now, result='confirmed', reason='Program veya resmi soru ve komisyon kaydı okundu.')
records['practice_event'].append(dict(id=eid, common_event_key='tbmm-28-2-7-16207-okul-yemegi-dilekceleri', event_at='2024-09-13', date_precision='day', date_unknown_reason=None, scope_context='TBMM ücretsiz okul yemeği dilekçeleri yazılı soru ve yanıt kaydı', title='Ücretsiz okul yemeği dilekçeleri hakkında yazılı soru', occurrence_basis='TBMM soru kaydı Karaca Demiri, konuyu ve başkanlığa geliş gününü bildirir.'))
for p, point in [(detail+'-number-p','TBMM 7/16207 sayılı yazılı soru kaydıdır.'), (detail+'-date-p','Soru 13 Eylül 2024 tarihinde başkanlığa geldi.'), (owner,'Soru sahibi Gaziantep Milletvekili Sevda Karaca Demirdir.'), (detail+'-reply-p','TBMM kaydına göre yanıt 25 Ekim 2024 tarihinde bildirildi.')]:
    records['practice_event_evidence'].append(dict(event_id=eid, passage_id=p, supported_point=point, stage='action', concrete_basis='TBMM resmi soru kaydı.', limitation='Yanıtın bildirilmesi tüm öğrenciler için ücretsiz yemek uygulandığını veya dilekçelerin akıbetinin açıklandığını göstermez.', epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=eid, passage_id=p, stage='action', basis_kind='document'))
records['practice_relation'].append(dict(id=rid, statement_id='0410-school-statement', event_id=eid, party_id='emep', topic_id='egitime-erisim', scope_id=scope, comparability_reason='Program ücretsiz eğitimi savunur; soru okullarda ücretsiz yemek talebiyle ilişkilidir.', target_finding_id='0410-school-statement-finding', result_finding_id=None, explanation_finding_id=fid, temporal_context='2023 komisyon tutanağı, Eylül 2024 soru ve Ekim 2024 yanıt bildirimi ayrı tarihlerdir.', authority_context='Soru Sevda Karaca Demire, yanıt Millî Eğitim Bakanlığına aittir.', uncertainty_reason='İmzalı soru teslim için soru tarihinden sonraki 14 Kasım 2024ü yazarken komisyon tutanağı 14 Kasım 2023teki 10 bin imzayı gösterir; 2023 program arşivinin olay tarihinde kesintisiz yürürlüğü kanıtlanmadı.'))
records['practice_candidate'].append(dict(id='0410-school-meal-16207-candidate', scope_id=scope, event_id=eid, relation_id=rid, state='eligible', reason='TBMM soru ve komisyon kayıtları ile taranmış yanıt incelendi.', passage_ids=json.dumps(pids[1:])))
for role in ('detail','question','answer','commission'):
    v=stem+role+'-v1'; version=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==v)
    section={'detail':'Soru ve cevap bildirimi','question':'İmzalı soru','answer':'Bakanlık yanıtı','commission':'Plan ve Bütçe Komisyonu tutanağı'}[role]
    aid='0410-school-meal-16207-'+role+'-attempt'
    records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=version['original_url'],relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])))
    records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=version['original_url'],url=version['original_url'],result='examined',reason='TBMM özgün kayıtları okundu; dilekçelerin akıbetine dair somut yanıt ayrıdır.',source_version_id=v))
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
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program ve TBMM kayıt pasajları incelendi.',limitations='Yanıt bildirimi dilekçelerin akıbeti veya tüm öğrencilere yemek sağlanması sonucu değildir.',result='reviewed',reason=kind+' / '+identity+' için kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets))
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs
for name,obj in [('school-meal-16207-union-draft.json',package),('school-meal-16207-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('SCHOOL_MEAL_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
