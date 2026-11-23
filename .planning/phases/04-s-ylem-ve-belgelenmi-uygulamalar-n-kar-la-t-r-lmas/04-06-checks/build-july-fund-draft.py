"""10/4343 görüşmesini 7 Ekim adayına ayrı ve eklemeli bir olay olarak hazırla."""
import datetime
import hashlib
import json
from pathlib import Path

checks = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
sha = lambda b: hashlib.sha256(b).hexdigest()
package_bytes = (checks / 'fund-1007-draft.json').read_bytes()
review_bytes = (checks / 'fund-1007-review-draft.json').read_bytes()
assert sha(package_bytes) == '0a5cb2eda60615fe5ff3361e0c932597e2fdc42c885b787636f02f4ccfa36e77'
assert sha(review_bytes) == '14157683235d874ffade550639fce2757fd7e45de434931e9fd04420a2a066b7'
pkg, review = json.loads(package_bytes), json.loads(review_bytes)
entries = json.loads((checks / 'july-fund-source-records.json').read_text())['entries']
ps = {e['values']['id']: e['values'] for e in entries if e['kind'] == 'passage'}
q = lambda n: '0406-fund-july-floor-' + n
event = '0406-fund-july-4343-event'
finding = '0406-fund-july-4343-f'
contribution = '0406-fund-july-4343-contribution'
candidate = '0406-fund-july-4343-unmatched'
scope = 'practice-eef45ed112da730d31f83015964c900d73e2f2a0bd64ee6694e03dacdad1839e'
ver = '0406-fund-july-floor-v1'
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
ids = list(ps)
entries.append(dict(kind='finding', values=dict(id=finding, party_id='dem', heading='Belgelenmiş uygulamalar', pair_id=finding, text='1 Temmuz 2026 Genel Kurulunda DEM Parti grubu adına konuşan İbrahim Akın, sermaye piyasalarına ilişkin 10/4343 araştırma önergesinin aynı gün görüşülmesi için Yeni Yol grubunun önerisini sözlü olarak destekledi. Üçüncü elektronik oylama sonunda gündem önerisi kabul edilmedi. Tutanaktaki konuşma, isimli bir DEM oyunu veya araştırma komisyonu kurulduğunu göstermez.', provenance='summary', epistemic_type='claim')))
for passage in ids:
    entries.append(dict(kind='finding_evidence', values=dict(finding_id=finding, passage_id=passage, role='support')))
pkg['entries'] += entries
points = [(q('agenda'), 'initiative', 'Yeni Yol aynı gün görüşme önerisi'), (q('dem-role'), 'action', 'Akın DEM grubu adına konuştu'), (q('dem-support'), 'action', 'Akın öneriyi sözlü destekledi'), (q('quorum1'), 'result', 'İlk oylamada karar yeter sayısı yoktu'), (q('quorum2'), 'result', 'İkinci oylamada karar yeter sayısı yoktu'), (q('decision'), 'result', 'Üçüncü oylamada grup önerisi kabul edilmedi')]
records = {
 'practice_event': [dict(id=event, common_event_key='tbmm-28-4-108-10-4343-gundem', event_at='2026-07-01', date_precision='day', date_unknown_reason=None, scope_context='Yeni Yol Grubu 10/4343’ün 1 Temmuz birleşiminde görüşülmesini önerdi. Genel Kurul öneriyi kabul etmedi.', title='10/4343 araştırma önergesinin aynı gün görüşülmesi', occurrence_basis='TBMM önergesi, birleşim tutanağı ve ilgili işlem belgeleri.')],
 'practice_event_evidence': [dict(event_id=event, passage_id=p, supported_point=point, stage=stage, concrete_basis='1 Temmuz TBMM birleşim tutanağının ilgili sayfası.', limitation='Sözlü destek isimli oy değildir; gündem kararı araştırma önergesinin esasından ayrıdır.', epistemic_type='claim') for p, stage, point in points],
 'practice_evidence_assessment': [dict(event_id=event, passage_id=p, stage=stage, basis_kind='document') for p, stage, _ in points],
 'practice_contribution': [dict(id=contribution, event_id=event, party_id='dem', actor_id='0406-dem-institution', contribution_kind='support', finding_id=finding, authority_passage_id=None, membership_passage_id=None, responsibility_limit='Grup adına sözlü destek; isimli oy veya komisyon kurulması değil.')],
 'practice_attempt_v2': [dict(id='0406-fund-july-reading', scope_id=scope, attempted_at=now, query='1 Temmuz 2026 TBMM 108. birleşim 10/4343 İbrahim Akın', url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/108/Basilmis/8c78bb73-5fa2-43ca-965a-aa0deaac261e.pdf', result='examined', reason='İlgili gündem önerisi, grup konuşması ve oylama bölümleri okundu; birleşim tamamı okunmadı.', source_version_id=ver)],
 'practice_scope_source': [dict(scope_id=scope, version_id=ver, inspected_sections=json.dumps([v['section'] for v in ps.values()], ensure_ascii=False), inspected_at=now)],
 'practice_candidate': [dict(id=candidate, scope_id=scope, event_id=event, relation_id=None, state='unmatched', reason='Ayrı ve daha önce yayımlanmış parti söylemiyle eşleştirme araştırması açık; grup desteği isimli oy veya araştırmanın kurulması değildir.', passage_ids=json.dumps(ids, ensure_ascii=False))],
}
for kind, values in records.items():
    pkg['practice_records'].setdefault(kind, []).extend(values)
items = [('practice_event_evidence', event+'|'+p+'|'+stage, [p], point) for p, stage, point in points]
items += [('practice_event', event, ids, 'Aynı gün görüşme önerisi ve karar.'), ('practice_contribution', contribution, ids, 'DEM grubu adına sözlü destek.'), ('practice_contribution.finding_id', contribution, ids, 'Destek konuşması ile gündem kararının ayrılması.'), ('practice_candidate', candidate, ids, 'Önceki söylem araştırması açık.')]
for kind, ident, passages, claim in items:
    review['practice_source_review'].append(dict(subject_kind=kind, subject_id=ident, reviewer_kind='agent', reviewed_at=now, source_version_ids=json.dumps([ver]), passage_ids=json.dumps(passages, ensure_ascii=False), inspected_sections=json.dumps([ps[p]['section'] for p in passages], ensure_ascii=False), supported_claim=claim, limitations='Sözlü destek isimli oy değildir; gündem önerisi araştırma önergesinin esası değildir.', result='reviewed', reason='TBMM basılı tutanakta ilgili sayfalar okundu: '+claim))
review['source_review_refs'] = [dict(subject_kind=x['subject_kind'], subject_id=x['subject_id']) for x in review['practice_source_review']]
for name, obj in [('fund-july-draft.json', pkg), ('fund-july-review-draft.json', review)]:
    path = checks / name
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
    print(name, sha(path.read_bytes()))
