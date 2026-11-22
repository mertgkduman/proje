import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
import uygulamalar as rules
D = Path(__file__).parent
read = lambda p: json.loads(Path(p).read_text())
package = read(D / 'questions-union-draft.json')
previous = read(D / 'questions-union-review-draft.json')
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
inventory = read('data/practices/04-inventory.json')
entries, records = package['entries'], package['practice_records']
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
for name in ('mekke-question-source-draft.json', 'mekke-ballot-source-draft.json'):
    entries.extend(read(D / name)['entries'])
scopes = {c['research_kind']: c for c in inventory['cells'] if c['party_id'] == 'emep' and c['topic_id'] == 'dis-politika'}
assert set(scopes) == {'statement', 'event'}
for c in scopes.values():
    row = {k: c[k] for k in ('party_id', 'topic_id', 'taxonomy_version', 'period_start', 'cutoff_at', 'research_kind')}
    row.update(id=c['cell_id'], boundary_reason='Dış ilişkiler program ilkesi, bir milletvekilinin sorusu ve daha sonraki oyu incelendi; diğer kaynaklar açık.')
    records['practice_scope_v2'].append(row)
def add(k, **values): entries.append({'kind': k, 'values': values})
def finding(fid, text, pids, provenance='summary', pair=None):
    add('finding', id=fid, party_id='emep', heading='Belgelenmiş uygulamalar', pair_id=pair or fid, text=text, provenance=provenance, epistemic_type='claim')
    add('review', id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program ve TBMM kaynakları ayrı incelendi.')
    for pid in pids:
        add('finding_evidence', finding_id=fid, passage_id=pid, role='support')
        add('verification', finding_id=fid, passage_id=pid, checked_at=now, result='confirmed', reason='Program veya TBMM özgün pasajı incelendi.')
program = '0309-emep-program-016-0-passage'
qdate = '0410-emep-mekke-748173-register-date-p'
qowner = '0410-emep-mekke-748173-register-owner-p'
crit = '0410-emep-mekke-748173-pdf-criticism-p'
vote = '0410-emep-mekke-ballot-bayhan-p'
absent = '0410-emep-mekke-ballot-karaca-p'
sf, qf, statement = '0410-foreign-principles-finding', '0410-foreign-principles-quote', '0410-foreign-principles-statement'
finding(sf, 'Program, ülkeler arası ilişkilerin egemenliğe saygı, eşitlik ve barış temelinde kurulmasını savunur.', [program])
finding(qf, 'Başta komşu ülkeler\nolmak üzere, diğer ülkelerle ulusal bağımsızlık ve egemenliğe saygı, karşılıklı\nyarar, içişlerine karışmama, eşitlik, barış, dostluk temeline dayanan\nilişkiler.', [program], 'quote', sf)
records['practice_statement'].append(dict(id=statement, party_id='emep', topic_id='dis-politika', taxonomy_version=4, summary_finding_id=sf, quote_finding_id=qf, statement_at=None, date_precision='unknown', version_id='0208-emep-program-charter-v1', period_basis='2019 yayın ve 2020 site güncellemesi kabul tarihi değildir.', uncertainty_reason='2023 arşiv görüntüsü ara değişiklik veya hukuki yürürlük tarihi kanıtı değildir.', comparison_row_id='04-03-v3-0309-emep-program-016-0-row'))
cases = [
 ('question', '2026-08-24', 'tbmm-28-4-7-48173-mekke-soru', 'İskender Bayhan’ın Mekke anlaşması sorusu', [qdate, qowner, crit], 'Bayhan 24 Ağustos’ta anlaşmaya ilişkin eleştirisini ve sorularını Dışişleri Bakanına yöneltti.', 'Yazılı soru ve Bayhan’ın kendi değerlendirmesi; sorudaki iddialar doğrulanmış anlaşma hükmü değildir.'),
 ('vote', '2026-11-05', 'tbmm-28-5-014-2-3961-mekke-7597', 'Mekke anlaşmasının uygun bulunması oylaması', [vote, absent], '5 Kasım açık oylamasında İskender Bayhan ret oyu verdi; Sevda Karaca Demir katılmadı.', 'Cetvel Karaca Demir’in katılmama nedenini göstermiyor; Bayhan’ın kişisel oyu grup kararı kanıtı değildir.')]
for name, date, key, title, pids, summary, limit in cases:
    eid, rid, ef = '0410-mekke-'+name+'-event', '0410-mekke-'+name+'-relation', '0410-mekke-'+name+'-explanation'
    finding(ef, 'Program ülkeler arası barış ve egemenliğe saygıyı savunur. ' + summary, [program] + pids)
    records['practice_event'].append(dict(id=eid, common_event_key=key, event_at=date, date_precision='day', date_unknown_reason=None, scope_context='TBMM kayıtlarında Mekke anlaşması', title=title, occurrence_basis=limit))
    points = {qdate:'Soru 24 Ağustos 2026 tarihinde kaydedildi.', qowner:'Soru sahibi İskender Bayhan olarak kaydedildi.', crit:'Bayhan soru metninde anlaşmanın güvenliğe katkısını eleştirdi.', vote:'İskender Bayhan 5 Kasım açık oylamasında ret oyu kullandı.', absent:'Sevda Karaca Demir oylamada katılmadı olarak listelendi.'}
    for pid in pids:
        records['practice_event_evidence'].append(dict(event_id=eid, passage_id=pid, supported_point=points[pid], stage='action', concrete_basis='TBMM özgün belge veya kayıt satırı.', limitation=limit, epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid, passage_id=pid, stage='action', basis_kind='document'))
    records['practice_relation'].append(dict(id=rid, statement_id=statement, event_id=eid, party_id='emep', topic_id='dis-politika', scope_id=scopes['event']['cell_id'], comparability_reason='Dış ilişkilerde barış ve egemenlik ilkesi ile savunma anlaşmasına ilişkin TBMM işlemi aynı geniş politika alanındadır; belirli anlaşma programda adlandırılmamıştır.', target_finding_id=sf, result_finding_id=None, explanation_finding_id=ef, temporal_context='Program arşivi, Ağustos sorusu ve Kasım oylaması ayrı tarihlerdir.', authority_context='İşlem ve açıklamalar İskender Bayhan’a atfedilir.', uncertainty_reason=limit))
    records['practice_candidate'].append(dict(id='0410-mekke-'+name+'-candidate', scope_id=scopes['event']['cell_id'], event_id=eid, relation_id=rid, state='eligible', reason='Dış politika alanında tarihli TBMM işlemi.', passage_ids=json.dumps(pids)))
sources = [('statement', '0208-emep-program-charter-v1', 'https://www.emep.org/emek-partisi-program-ve-tuzugu', 'G/B/1 dış ilişkiler ilkeleri'), ('event', '0410-emep-mekke-748173-pdf-v1', 'https://tbmm.gov.tr', '7/48173 imzalı soru'), ('event', '0410-emep-mekke-748173-register-v1', 'https://tbmm.gov.tr', '7/48173 TBMM kaydı'), ('event', '0410-emep-mekke-ballot-v1', 'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/14/AcikOylamaSonuc/cbfb34cb-f290-4c39-a3b3-b902717425ea.html', '5 Kasım isimli açık oy cetveli')]
versions = {e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'}
for i, (typ, version, url, section) in enumerate(sources):
    if version in versions: url = versions[version]['original_url']
    scope, aid = scopes[typ]['cell_id'], '0410-mekke-attempt-'+str(i)
    records['practice_scope_source'].append(dict(scope_id=scope, version_id=version, inspected_sections=json.dumps([section], ensure_ascii=False), inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+aid, scope_id=scope, url=url, relevance_reason=section, state='examined', attempt_ids=json.dumps([aid])))
    records['practice_attempt_v2'].append(dict(id=aid, scope_id=scope, attempted_at=now, query=url, url=url, result='examined', reason=section+' okundu; kapsam açık.', source_version_id=version))
data=copy.deepcopy(base)
for entry in entries:
    if entry['values'] not in data.setdefault(entry['kind'], []): data[entry['kind']].append(entry['values'])
for table, rows in records.items(): data.setdefault(table, []).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_targets(data, records)
passages={p['id']:p for p in data['passage']}
old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']}
reviews=[]
for (kind, identity), (pids, parties) in sorted(targets.items()):
    if 'emep' not in parties: continue
    if (kind,identity) in old: reviews.append(old[(kind,identity)]); continue
    inspected=[passages[x] for x in sorted(pids)]
    reviews.append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent', reviewed_at=now, source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})), passage_ids=json.dumps([p['id'] for p in inspected]), inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False), supported_claim='Program genel dış ilişki ilkeleri, Bayhan’ın sorusu ve ayrı açık oyu özgün kaynaklardan incelendi.', limitations='Soru ve oy kişisel; katılmama nedeni bilinmez; program belirli anlaşmayı adlandırmaz.', result='reviewed', reason=kind+' / '+identity+' için bağlı program ve TBMM pasajları okundu.'))
rules.validate_practice_source_review(data, reviews, require_coverage=False, party_id='emep')
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]
package['source_review_refs']=refs
for name,obj in [('mekke-union-v3-draft.json',package),('mekke-union-v3-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f: f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('MEKKE_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']))
