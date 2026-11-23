"""Doğrulanmış DEM çalışma çiftine 10/4625 gündem katkısını ekle."""
import datetime
import hashlib
import json
from pathlib import Path

c = Path(__file__).resolve().parent
root = c.parents[3]
package, review = (root / 'data/practices/04-dem.json', root / 'data/practices/04-dem-review.json')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(package) == '09a12448a4d727b21f9734d71aed688e8d2d7698b6602291cc18df269a00e8bf'
assert sha(review) == '190f924b8665c292dff6826fa738fa341f4b9f12237363540f3b8e84faeefa89'
pkg, rev = json.loads(package.read_text()), json.loads(review.read_text())
entries = json.loads((c / 'staj-agenda-source-records.json').read_text())['entries']
passages = {x['values']['id']: x['values'] for x in entries if x['kind'] == 'passage'}
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
scope = 'practice-5a881b0a216826a2360edc436182d8f5270ed950adef9e13b3f8072eed6e9365'
event, finding = '0406-staj-agenda-event', '0406-staj-agenda-finding'
contribution, candidate = '0406-staj-agenda-contribution', '0406-staj-agenda-candidate'
q = lambda x: '0406-staj-agenda-' + x
points = [('inquiry-id', 'initiative'), ('inquiry-models', 'initiative'),
          ('inquiry-register-filed', 'initiative'), ('inquiry-register-pending', 'result'),
          ('floor-call', 'initiative'), ('floor-dem-role', 'action'),
          ('floor-dem-call', 'action'), ('floor-decision', 'result')]
ids = [q(n) for n, _ in points]
def add(kind, **values): pkg['practice_records'].setdefault(kind, []).append(values)
entries.append({'kind': 'finding', 'values': {'id': finding, 'party_id': 'dem',
    'heading': 'Belgelenmiş uygulamalar', 'pair_id': finding,
    'text': '20 Ekim 2026 Genel Kurulunda DEM Parti Grubu adına Mehmet Zeki İrmez, staj ve çıraklıkta geçen sürelerin emeklilik hesabına katılmamasını eleştirdi ve araştırma komisyonu kurulması çağrısı yaptı. CHP’nin 10/4625 araştırma önergesinin o gün görüşülmesi için grup önerisi kabul edilmedi. TBMM esas kaydındaki Gündemde durumu, gündem önerisi kararıyla ve isimli oyla aynı değildir.',
    'provenance': 'summary', 'epistemic_type': 'claim'}})
for name, stage in points:
    pid = q(name); passage = passages[pid]
    entries.extend([{'kind': 'finding_evidence', 'values': {'finding_id': finding, 'passage_id': pid, 'role': 'support'}},
        {'kind': 'verification', 'values': {'finding_id': finding, 'passage_id': pid, 'checked_at': now, 'result': 'confirmed', 'reason': 'İmzalı önerge, esas kaydı ve birleşim tutanağının ilgili bölümleri okundu.'}}])
    add('practice_event_evidence', event_id=event, passage_id=pid, supported_point=passage['section'], stage=stage,
        concrete_basis='TBMM imzalı önergesi, esas kaydı ve 20 Ekim birleşim tutanağı.',
        limitation='Sözlü grup katkısı, gündem kararı, esas dosyası ve isimli oy ayrıdır.', epistemic_type='claim')
    add('practice_evidence_assessment', event_id=event, passage_id=pid, stage=stage, basis_kind='document')
entries.append({'kind': 'review', 'values': {'id': 'review-' + finding, 'kind': 'finding',
    'subject_id': finding, 'reviewer_kind': 'agent', 'reviewed_at': now, 'result': 'reviewed',
    'reason': 'Konuşmacı, araştırma önergesi, gündem kararı ve dosya durumu ayrı kontrol edildi.'}})
add('practice_event', id=event, common_event_key='tbmm-28-5-008-10-4625-gundem', event_at='2026-10-20', date_precision='day', date_unknown_reason=None,
    title='10/4625 araştırma önergesinin 20 Ekim’de görüşülmesi',
    scope_context='CHP Grubu 10/4625’in 20 Ekim birleşiminde ön görüşmeye alınmasını önerdi. Genel Kurul grup önerisini kabul etmedi.',
    occurrence_basis='TBMM önergesi, birleşim tutanağı ve ilgili işlem belgeleri.')
add('practice_contribution', id=contribution, event_id=event, party_id='dem', actor_id='0406-dem-institution', contribution_kind='support', finding_id=finding, authority_passage_id=None, membership_passage_id=None,
    responsibility_limit='Grup adına konuşma; isimli oy, araştırma komisyonunun kurulması veya yasalaşma değildir.')
add('practice_candidate', id=candidate, scope_id=scope, event_id=event, relation_id=None, state='unmatched',
    reason='Staj ve çıraklık özelinde önceki yayımlanmış parti söylemi araştırması açıktır.', passage_ids=json.dumps(ids, ensure_ascii=False))
targets = [('practice_event_evidence', event+'|'+q(n)+'|'+stage, [q(n)], passages[q(n)]['section']) for n, stage in points]
targets += [('practice_event', event, ids, 'Araştırma ve ayrı gündem kararı.'),
            ('practice_contribution', contribution, ids, 'DEM grubu adına sözlü katkı.'),
            ('practice_contribution.finding_id', contribution, ids, 'Görüş ve sonuç bulgusunun sınırı.'),
            ('practice_candidate', candidate, ids, 'Önceki söylem araştırması açık.')]
for typ, ident, refs, description in targets:
    versions = list(dict.fromkeys(passages[x]['version_id'] for x in refs))
    rev['practice_source_review'].append(dict(subject_kind=typ, subject_id=ident, reviewer_kind='agent', reviewed_at=now,
        source_version_ids=json.dumps(versions, ensure_ascii=False), passage_ids=json.dumps(refs, ensure_ascii=False),
        inspected_sections=json.dumps([passages[x]['section'] for x in refs], ensure_ascii=False),
        supported_claim=description+' 10/4625 ve 20 Ekim gündemi.',
        limitations='İsimli oy, araştırma kurulması ve yasalaşma bu kaynaklardan çıkarılmaz.',
        result='reviewed', reason='İlgili TBMM kaynakları ve dört sayfalık imzalı önerge incelendi.'))
for version in dict.fromkeys(passages[x]['version_id'] for x in ids):
    refs = [x for x in ids if passages[x]['version_id'] == version]
    add('practice_scope_source', scope_id=scope, version_id=version,
        inspected_sections=json.dumps([passages[x]['section'] for x in refs], ensure_ascii=False), inspected_at=now)
add('practice_attempt_v2', id='0406-staj-agenda-reading', scope_id=scope, attempted_at=now,
    query='20 Ekim 2026 10/4625 staj çıraklık araştırması DEM grup konuşması',
    url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/8/Ham/dcb831f7-1664-48cd-8209-d84d460415f8.html',
    result='examined', reason='İlgili konuşma ve gündem kararı okundu; tüm birleşim okunmadı.', source_version_id=q('floor-v1'))
for suffix, url, reason in (
    ('inquiry-v1', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T10/WebOnergeMetni/a3dbf238-6114-4857-b432-43f0639d7236.pdf', 'Dört sayfalık imzalı araştırma önergesi görüntüden okundu.'),
    ('inquiry-register-v1', 'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/bfbc23a8-bc6c-4c9b-bcb5-01a11b3356f9', 'TBMM esas numarası, geliş tarihi ve erişim durumu okundu.'),
):
    add('practice_attempt_v2', id='0406-staj-'+suffix+'-reading', scope_id=scope, attempted_at=now,
        query='10/4625 staj ve çıraklık araştırma önergesi', url=url,
        result='examined', reason=reason, source_version_id=q(suffix))
pkg['entries'] += entries
rev['source_review_refs'] = [dict(subject_kind=x['subject_kind'], subject_id=x['subject_id']) for x in rev['practice_source_review']]
for name, obj in [('staj-dem-v2-draft.json', pkg), ('staj-dem-v2-review-draft.json', rev)]:
    path = c/name; path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n'); print(name, sha(path))
