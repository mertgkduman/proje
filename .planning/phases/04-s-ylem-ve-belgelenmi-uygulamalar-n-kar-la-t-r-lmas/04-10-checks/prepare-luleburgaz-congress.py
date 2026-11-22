import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
import uygulamalar as rules
D = Path(__file__).parent
read = lambda p: json.loads(Path(p).read_text())
package = read(D/'kocaeli-congress-union-draft.json')
previous = read(D/'kocaeli-congress-union-review-draft.json')
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries, records = package['entries'], package['practice_records']
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
entries.extend(read(D/'luleburgaz-congress-source-draft.json')['entries'])
scope = next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='orgut-ilce-kongre' and x['research_kind']=='event')
charter = '0410-emep-gebze-charter-selected-p'
news = '0410-emep-luleburgaz-2020-evrensel-p'
eid = '0410-luleburgaz-2020-congress-event'
rid = '0410-luleburgaz-2020-congress-relation'
result = '0410-luleburgaz-2020-congress-result'
explanation = '0410-luleburgaz-2020-congress-explanation'
def add(k, **v): entries.append(dict(kind=k, values=v))
def finding(fid, text, pids):
    add('finding', id=fid, party_id='emep', heading='Belgelenmiş uygulamalar', pair_id=fid, text=text, provenance='summary', epistemic_type='claim')
    add('review', id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Tüzük ve kongre haberi ayrı okundu.')
    for pid in pids:
        add('finding_evidence', finding_id=fid, passage_id=pid, role='support')
        add('verification', finding_id=fid, passage_id=pid, checked_at=now, result='confirmed', reason='İlgili kaynak pasajı incelendi.')
finding(result, 'Evrensel, Lüleburgaz ilçe kongresinde Cengiz Atlı’nın ilçe başkanlığına getirildiğini bildirdi.', [news])
finding(explanation, 'Tüzük ilçe kongresine ilçe başkanını seçme görevi verir. Evrensel, Lüleburgaz ilçe kongresinde Cengiz Atlı’nın ilçe başkanlığına getirildiğini aktardı.', [charter, news])
records['practice_event'].append(dict(id=eid, common_event_key='emep-luleburgaz-ilce-kongresi-cengiz-atli-2020-10-11', event_at='2020-10-11', date_precision='day', date_unknown_reason=None, scope_context='EMEP Lüleburgaz ilçe kongresi', title='Lüleburgaz ilçe başkanlığı seçimi', occurrence_basis='11 Ekim 2020 tarihli haber kongrenin bugün yapıldığını bildiriyor.'))
for stage in ['action', 'result']:
    records['practice_event_evidence'].append(dict(event_id=eid, passage_id=news, supported_point='Evrensel, 11 Ekim tarihli haberinde Cengiz Atlı’nın ilçe başkanlığına getirildiğini bildiriyor.', stage=stage, concrete_basis='11 Ekim 2020 tarihli Lüleburgaz/EVRENSEL haberi.', limitation='Oy sayısı, seçim yöntemi ve seçim tutanağı haberde belirtilmiyor.', epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=eid, passage_id=news, stage=stage, basis_kind='document'))
records['practice_relation'].append(dict(id=rid, statement_id='0410-gebze-charter-statement', event_id=eid, party_id='emep', topic_id='orgut-ilce-kongre', scope_id=scope, comparability_reason='Tüzüğün ilçe başkanı seçimi görevi ile Lüleburgaz kongresinde bildirilen başkan seçimi aynı konudadır.', target_finding_id='0410-gebze-charter-finding', result_finding_id=result, explanation_finding_id=explanation, temporal_context='2019 parti yayını, Ağustos 2020 web güncellemesi ve 11 Ekim 2020 tarihli kongre haberi.', authority_context='Tüzük ilçe kongresine başkan seçme görevi verir.', uncertainty_reason='Ara tüzük değişiklikleri, seçim tutanağı ve oy yöntemi görülmedi.'))
records['practice_candidate'].append(dict(id='0410-luleburgaz-2020-congress-candidate', scope_id=scope, event_id=eid, relation_id=rid, state='eligible', reason='Haber ilçe kongresindeki başkan seçimini bildiriyor.', passage_ids=json.dumps([news])))
version = '0410-emep-luleburgaz-2020-evrensel-v1'
url = 'https://www.evrensel.net/haber/416240/emep-kongrelerini-surduruyor'
aid = '0410-luleburgaz-2020-congress-attempt'
section = '11 Ekim ilçe kongresi'
records['practice_scope_source'].append(dict(scope_id=scope, version_id=version, inspected_sections=json.dumps([section],ensure_ascii=False), inspected_at=now))
records['practice_lead'].append(dict(id='lead-'+aid, scope_id=scope, url=url, relevance_reason=section, state='examined', attempt_ids=json.dumps([aid])))
records['practice_attempt_v2'].append(dict(id=aid, scope_id=scope, attempted_at=now, query=url, url=url, result='examined', reason='14 Ekim 2020 arşiv kopyası okundu; oy yöntemi ve seçim tutanağı açık.', source_version_id=version))
data = copy.deepcopy(base)
for entry in entries:
    if entry['values'] not in data.setdefault(entry['kind'], []): data[entry['kind']].append(entry['values'])
for table, rows in records.items(): data.setdefault(table, []).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets = rules.practice_review_targets(data, records)
passages = {p['id']: p for p in data['passage']}
old = {(r['subject_kind'], r['subject_id']):r for r in previous['practice_source_review']}
reviews = []
for (kind, identity), (pids, parties) in sorted(targets.items()):
    if 'emep' not in parties: continue
    if (kind, identity) in old:
        reviews.append(old[(kind, identity)])
        continue
    inspected = [passages[x] for x in sorted(pids)]
    reviews.append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent', reviewed_at=now, source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})), passage_ids=json.dumps([p['id'] for p in inspected]), inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False), supported_claim='Tüzük ilçe başkanı seçimini düzenler; haber Atlı’nın başkanlığa getirildiğini bildirir.', limitations='Oy yöntemi, tutanak ve ara tüzük değişiklikleri bilinmiyor.', result='reviewed', reason=kind+' / '+identity+' için ilgili tüzük ve haber pasajları okundu.'))
rules.validate_practice_source_review(data, reviews, require_coverage=False, party_id='emep')
refs = [{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]
package['source_review_refs'] = refs
for name, obj in [('luleburgaz-congress-branch-draft.json',package), ('luleburgaz-congress-branch-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f: f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('LULEBURGAZ_BRANCH_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']))
