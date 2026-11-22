import copy
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, 'src')
import uygulamalar as rules

D = Path(__file__).parent
read = lambda p: json.loads(Path(p).read_text())
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
inventory = read('data/practices/04-inventory.json')
template = read('data/practices/04-iyi.json')
records = {k: [] for k in template['practice_records']}
for name in ('practice_contract', 'practice_coverage_contract', 'practice_variant_contract', 'practice_evidence_contract'):
    records[name] = copy.deepcopy(template['practice_records'][name])
records['practice_evidence_assessment'] = [x for x in template['practice_records']['practice_evidence_assessment'] if x['event_id'] == 'tracer-cesme']
entries = read(D/'congress-2023-source-draft.json')['entries']
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
topic = 'genel-kongre-gorev'
scopes = {c['research_kind']: c for c in inventory['cells'] if c['party_id']=='emep' and c['topic_id']==topic}
assert set(scopes)=={'event','statement'}
for c in scopes.values():
    row = {k:c[k] for k in ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')}
    row.update(id=c['cell_id'], boundary_reason='Yalnız kaynaklı tüzük hükmü ve 2023 genel başkan seçiminin dar incelenmesi; diğer kaynak ve dönemler açıktır.')
    records['practice_scope_v2'].append(row)
charter='0208-emep-charter-governance'
event_passage='04010-emep-2023-cumhuriyet-p'
party_passage='04010-emep-2023-party-p'
assert next(x for x in base['passage'] if x['id']==charter)['exact']=='Genel Başkan’ı, GYK ve MDK’yi seçer.'
def add(table, **values): entries.append({'kind':table, 'values':values})
def finding(fid,text,pids,provenance='summary',pair=None):
    add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=pair or fid,text=text,provenance=provenance,epistemic_type='claim')
    add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Kaynak pasajı, aktör ve tarih sınırı incelendi.')
    for pid in pids:
        add('finding_evidence',finding_id=fid,passage_id=pid,role='support')
        add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Bu bulgunun kaynak pasajıyla anlamı denetlendi.')
summary='0410-kongre-statement-finding'; quote='0410-kongre-statement-quote'; result='0410-kongre-election-result'; relation='0410-kongre-relation-finding'
finding(summary,'Parti tüzüğü metni genel başkan ve merkez kurullarının seçimini genel kongrenin görevleri arasında sayar.',[charter])
finding(quote,'Genel Başkan’ı, GYK ve MDK’yi seçer.',[charter],provenance='quote',pair=summary)
finding(result,'Cumhuriyet, 10. Kongrede Seyit Aslan’ın genel başkan seçildiğini bildirdi.',[event_passage])
finding(relation,'Partinin yayımladığı tüzük metni genel başkan seçimini kongrenin görevleri arasında sayar. Cumhuriyet, 24 Aralık 2023 kongresinde Seyit Aslan’ın genel başkan seçildiğini aktardı.',[charter,event_passage])
sid='0410-kongre-statement'; eid='0410-2023-kongre-event'; rid='0410-2023-kongre-relation'
records['practice_statement'].append(dict(id=sid,party_id='emep',topic_id=topic,taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at=None,date_precision='unknown',version_id='0208-emep-program-charter-v1',period_basis='Parti kaynağı 2019 yayın ve 2020 web güncellemesi taşır; tüzük kabul tarihi bildirilmemiştir.',uncertainty_reason='2023 öncesi ara tüzük değişiklikleri ve seçim tutanağı araştırılmaktadır.',comparison_row_id='04-03-v3-0309-emep-html-031-0-row'))
records['practice_event'].append(dict(id=eid,common_event_key='emep-2023-12-24-10-kongre-genel-baskan',event_at='2023-12-24',date_precision='day',date_unknown_reason=None,scope_context='EMEP 10. Kongresinde genel başkan seçimi',title='10. Kongrede genel başkan seçimi',occurrence_basis='26 Aralık Cumhuriyet haberinin önceki gün ifadesi kongre tarihini, haber ve parti yayını sonucu bildirir.'))
for stage in ('action','result'):
    records['practice_event_evidence'].append(dict(event_id=eid,passage_id=event_passage,supported_point='Cumhuriyet, Seyit Aslan’ın genel başkan seçildiğini bildirir.',stage=stage,concrete_basis='Cumhuriyet kongre ve genel başkan seçimini aktarır.',limitation='Seçim tutanağı ve oy sayıları görülmedi.',epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=event_passage,stage=stage,basis_kind='independent_report'))
records['practice_relation'].append(dict(id=rid,statement_id=sid,event_id=eid,party_id='emep',topic_id=topic,scope_id=scopes['event']['cell_id'],comparability_reason='Tüzük hükmü ve kongredeki seçim genel başkan seçimiyle ilgilidir.',target_finding_id=summary,result_finding_id=result,explanation_finding_id=relation,temporal_context='2019/2020 tarihli parti yayını ile 24 Aralık 2023 kongresi ayrı tarihlerdir.',authority_context='Tüzük metninde seçim yetkisi genel kongreye verilir.',uncertainty_reason='Ara tüzük sürümü ve seçim tutanağı görülmedi.'))
records['practice_candidate'].append(dict(id='0410-kongre-candidate',scope_id=scopes['event']['cell_id'],event_id=eid,relation_id=rid,state='eligible',reason='Genel kongrede genel başkan seçimi, genel kongrenin görev alanıyla ilgilidir.',passage_ids=json.dumps([event_passage])))
for kind,version,url,section in [('statement','0208-emep-program-charter-v1','https://www.emep.org/emek-partisi-program-ve-tuzugu','Tüzük 31 ve 32'),('event','04010-emep-2023-cumhuriyet-v1','https://www.cumhuriyet.com.tr/turkiye/yeni-emep-genel-baskani-seyit-aslan-cumhuriyete-konustu-karanliga-2155888','2023 kongre ve seçim')]:
    scope=scopes[kind]['cell_id']; aid='0410-'+kind+'-reading'
    records['practice_scope_source'].append(dict(scope_id=scope,version_id=version,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])))
    records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=section+' okundu; kapsam açıktır.',source_version_id=version))
data=copy.deepcopy(base)
for e in entries: data.setdefault(e['kind'],[]).append(e['values'])
for k,v in records.items():
    target=data.setdefault(k,[])
    target.extend(row for row in v if row not in target)
rules.validate_practices(data)
targets=rules.practice_review_targets(data,records)
passages={p['id']:p for p in data['passage']}
reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
    if 'emep' not in parties: continue
    ps=[passages[p] for p in sorted(pids)]
    claim={'practice_statement':'Tüzük genel kongreye genel başkanı ve merkez kurullarını seçme görevi verir.', 'practice_statement.quote_finding_id':'Madde 31 seçim yetkisini alıntıdaki ifadeyle belirtir.', 'practice_relation':'Tüzükteki kongre yetkisi ve 2023 genel başkan seçimi aynı konudadır.', 'practice_relation.target_finding_id':'Tüzüğün ilgili paragrafı genel kongrenin seçim yetkisini düzenler.', 'practice_relation.result_finding_id':'Cumhuriyet Seyit Aslan’ın genel başkan seçildiğini bildirir.', 'practice_event_evidence':'Cumhuriyet genel başkan seçimi sonucunu haberleştirir.'}.get(kind,kind+' hedefinde gösterilen pasajlar incelendi.')
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in ps})),passage_ids=json.dumps([p['id'] for p in ps]),inspected_sections=json.dumps(sorted({p['section'] for p in ps}),ensure_ascii=False),supported_claim=claim,limitations='2023 ara tüzük ve resmî seçim tutanağı görülmedi.',result='reviewed',reason=identity+' için ilgili metin ve dönemsellik incelendi.'))
rules.validate_practice_source_review(data,reviews,require_coverage=False,party_id='emep')
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]
package=dict(contract_version=1,base_release=inventory['base_release'],party_id='emep',taxonomy_version=4,stage='tracer',entries=entries,practice_records=records,scope_inventory=template['scope_inventory'],tranches=[],source_review_refs=refs)
review=dict(practice_source_review=reviews,source_review_refs=refs)
for name,obj in [('institution-tracer-draft.json',package),('institution-review-draft.json',review)]:
    with (D/name).open('x') as f: f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('SEMANTIC_PASS',len(reviews))
