import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text
import uygulamalar as rules

D = Path(__file__).parent
read = lambda p: json.loads(Path(p).read_text())
package = read(D/'school-meal-16207-union-draft.json')
previous = read(D/'school-meal-16207-union-review-draft.json')
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries, records = package['entries'], package['practice_records']
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
pid = '0410-emep-school-meal-16207-detail-topic-p'
exact = '&#xD6;&#x11F;rencilere okullarda bir &#xF6;&#x11F;&#xFC;n &#xFC;cretsiz yemek verilmesi amac&#x131;yla toplanarak Bakanl&#x131;&#x11F;a iletilen dilek&#xE7;elerin ak&#x131;betine ili&#x15F;kin'
assert exact in html_source_text((D/'school-meal-16207-detail.html').read_bytes())
def add(k, **v): entries.append(dict(kind=k, values=v))
add('passage', id=pid, version_id='0410-emep-school-meal-16207-detail-v1', exact=exact, prefix=None, suffix=None, article=None, section='Soru ve cevap bildirimi', pdf_page_index=None, printed_page=None)
fid='0410-school-meal-16207-explanation'; eid='0410-school-meal-16207-event'
add('finding_evidence', finding_id=fid, passage_id=pid, role='support')
add('verification', finding_id=fid, passage_id=pid, checked_at=now, result='confirmed', reason='TBMM ayrıntısındaki soru özeti okundu.')
records['practice_event_evidence'].append(dict(event_id=eid, passage_id=pid, supported_point='Soru ücretsiz okul yemeği dilekçelerinin akıbetine ilişkindir.', stage='action', concrete_basis='TBMM resmi soru özeti.', limitation='Özet, dilekçelerin akıbeti veya evrensel yemek uygulaması sonucu göstermez.', epistemic_type='claim'))
records['practice_evidence_assessment'].append(dict(event_id=eid, passage_id=pid, stage='action', basis_kind='document'))
data=copy.deepcopy(base)
for e in entries:
    if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items(): data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='emep')
passages={p['id']:p for p in data['passage']}; old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']}; reviews=[]; changed=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
    prior=old.get((kind,identity)); oldids=set(json.loads(prior['passage_ids'])) if prior else set()
    if prior and oldids==ids: reviews.append(prior); continue
    assert oldids <= ids
    inspected=[passages[x] for x in sorted(ids)]; changed.append([kind,identity])
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program ve TBMM kayıt pasajları incelendi.',limitations='Yanıt bildirimi dilekçelerin akıbeti veya tüm öğrencilere yemek sağlanması sonucu değildir.',result='reviewed',reason=kind+' / '+identity+' için önceki pasajlar ve resmi konu özeti yeniden okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets))
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs
for name,obj in [('school-meal-16207-topic-union-draft.json',package),('school-meal-16207-topic-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('SCHOOL_MEAL_TOPIC_SEMANTIC_PASS',len(reviews),'CHANGED',changed)
