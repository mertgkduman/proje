"""İklim son diliminden sonra 8/153 gündemindeki DEM konuşmasını hazırlar."""
import datetime, hashlib, json
from pathlib import Path

c = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
package, review = c / '4114-tail-draft.json', c / '4114-tail-review-draft.json'
assert sha(package) == 'e1d815c485448981c7e4dc5be340a5e96fab3e620958edb5ba58622130bcbe35'
assert sha(review) == '301dbb41ab3fae5e18dfbdb297c681c490b484a38f506c9ea4b172928aa69603'
pkg, rev = json.loads(package.read_text()), json.loads(review.read_text())
entries = json.loads((c / 'nov03-dem-source-records.json').read_text())['entries']
passages = {x['values']['id']: x['values'] for x in entries if x['kind'] == 'passage'}
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
q = lambda x: '0406-nov03-genelgorusme-' + x
event, finding = q('event'), q('finding')
contribution, candidate = q('contribution'), q('candidate')
scope = 'practice-eef45ed112da730d31f83015964c900d73e2f2a0bd64ee6694e03dacdad1839e'
points = [('signed-number', 'initiative'), ('register-number', 'initiative'), ('register-date', 'initiative'),
          ('register-status', 'result'), ('floor-call', 'initiative'), ('floor-dem-role', 'action'),
          ('floor-dem-call', 'action'), ('floor-vote', 'result')]
ids = [q(x) for x, _ in points]
def add(kind, **values): pkg['practice_records'].setdefault(kind, []).append(values)
entries.append({'kind': 'finding', 'values': {'id': finding, 'party_id': 'dem', 'heading': 'Belgelenmiş uygulamalar', 'pair_id': finding,
    'text': '3 Kasım 2026 Genel Kurulunda DEM Parti Grubu adına İbrahim Akın, fon piyasasına ilişkin konuşmasında denetlenebilir ve katılımlı bir karar yapısı çağrısı yaptı. Yeni Yol’un 8/153 genel görüşme önergesinin ön görüşmesinin aynı gün yapılması yönündeki grup önerisi kabul edilmedi. Esas dosyasındaki Gündemde durumu ve isimli oy, bu gündem kararından ayrıdır.',
    'provenance': 'summary', 'epistemic_type': 'claim'}})
for suffix, stage in points:
    pid = q(suffix); passage = passages[pid]
    entries.extend([{'kind': 'finding_evidence', 'values': {'finding_id': finding, 'passage_id': pid, 'role': 'support'}},
        {'kind': 'verification', 'values': {'finding_id': finding, 'passage_id': pid, 'checked_at': now, 'result': 'confirmed', 'reason': 'İmzalı dosya, esas sicili ve Genel Kurul ilgili bölümleri okundu.'}}])
    add('practice_event_evidence', event_id=event, passage_id=pid, supported_point=passage['section'], stage=stage,
        concrete_basis='TBMM imzalı 8/153 önergesi, esas sicili ve 3 Kasım birleşim tutanağı.',
        limitation='Konuşma, gündem kararı, esas dosyası ve isimli oy farklıdır.', epistemic_type='claim')
    add('practice_evidence_assessment', event_id=event, passage_id=pid, stage=stage, basis_kind='document')
entries.append({'kind': 'review', 'values': {'id': 'review-' + finding, 'kind': 'finding', 'subject_id': finding,
    'reviewer_kind': 'agent', 'reviewed_at': now, 'result': 'reviewed', 'reason': 'Konuşmacı aidiyeti ve iki ayrı işlem sonucu kontrol edildi.'}})
add('practice_event', id=event, common_event_key='tbmm-28-5-012-yeni-yol-genel-gorusme-fon-gundem', event_at='2026-11-03', date_precision='day', date_unknown_reason=None,
    title='Fonların ekonomik etkileri için genel görüşme ön görüşme talebinin reddi',
    scope_context='Yeni Yol Grubu, 3 Kasım 2026’da verdiği fonların ekonomik etkileri konulu genel görüşme önergesinin ön görüşmesinin aynı birleşimde yapılmasını istedi. Genel Kurul bu gündem talebini reddetti.',
    occurrence_basis='TBMM 28. Dönem 5. Yasama Yılı 12. Birleşim ham tutanağındaki grup önerisi, görüşmeler ve başkanın oylama sonucu.')
add('practice_contribution', id=contribution, event_id=event, party_id='dem', actor_id='0406-dem-institution', contribution_kind='unknown', finding_id=finding, authority_passage_id=None, membership_passage_id=None,
    responsibility_limit='DEM grubu adına konuşma; önergeye açık destek, isimli oy veya esas önergenin sonucu çıkarılmadı.')
add('practice_candidate', id=candidate, scope_id=scope, event_id=event, relation_id=None, state='unmatched',
    reason='Fon piyasası özelinde bağımsız önceki parti söylemi araştırması açık; konuşma, gündem oyu ve esas önerge sonucu ayrıdır.', passage_ids=json.dumps(ids, ensure_ascii=False))
targets = [('practice_event_evidence', event+'|'+q(n)+'|'+stage, [q(n)], passages[q(n)]['section']) for n, stage in points]
targets += [('practice_event', event, ids, '8/153 ve ayrı gündem kararı.'), ('practice_contribution', contribution, ids, 'DEM grubu adına konuşma.'),
            ('practice_contribution.finding_id', contribution, ids, 'Konuşma ve karar sınırı.'), ('practice_candidate', candidate, ids, 'Önceki söylem araştırması açık.')]
for typ, ident, refs, description in targets:
    versions = list(dict.fromkeys(passages[x]['version_id'] for x in refs))
    rev['practice_source_review'].append(dict(subject_kind=typ, subject_id=ident, reviewer_kind='agent', reviewed_at=now,
        source_version_ids=json.dumps(versions, ensure_ascii=False), passage_ids=json.dumps(refs, ensure_ascii=False),
        inspected_sections=json.dumps([passages[x]['section'] for x in refs], ensure_ascii=False), supported_claim=description,
        limitations='İsimli oy, açık destek ve esas önergenin kabul veya reddi çıkarılmaz.', result='reviewed', reason=('İmzalı 8/153 belgesinin ilk sayfasındaki esas numarası incelendi.' if 'genelgorusme-signed-number|initiative' in ident else 'TBMM 8/153 esas kaydındaki numara incelendi.' if 'genelgorusme-register-number|initiative' in ident else 'TBMM 10/4961 esas kaydındaki numara incelendi.' if '4961-register-number|initiative' in ident else 'İlgili sicil, imzalı dosya ve tutanak okundu.')))
urls = {'floor-v1': 'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/12/Ham/0643059d-54b7-4950-980d-f3f86843df5e.html',
        'register-v1': 'https://tbmm.gov.tr/Denetim/Genel-Gorusme-Onergesi-Detay/da5cdaed-c494-42c2-a5c5-01a1a69d2f81',
        'signed-v1': 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T8/WebOnergeMetni/3623d77f-a15f-48e9-8751-18ca1a5d7c94.pdf'}
for suffix, url in urls.items():
    version = q(suffix); refs = [x for x in ids if passages[x]['version_id'] == version]
    add('practice_scope_source', scope_id=scope, version_id=version, inspected_sections=json.dumps([passages[x]['section'] for x in refs], ensure_ascii=False), inspected_at=now)
    add('practice_attempt_v2', id=q(suffix+'-reading'), scope_id=scope, attempted_at=now, query='3 Kasım 2026 8/153 fonlar genel görüşme ve DEM grup konuşması', url=url,
        result='examined', reason='İlgili bölüm okundu; imzalı PDF iki sayfası görsel olarak incelendi.', source_version_id=version)
pkg['entries'] += entries
rev['source_review_refs'] = [dict(subject_kind=x['subject_kind'], subject_id=x['subject_id']) for x in rev['practice_source_review']]
for name, obj in [('nov03-dem-draft.json', pkg), ('nov03-dem-review-draft.json', rev)]:
    path = c/name; path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n'); print(name, sha(path))
