"""7 Ekim ortak olay başlığını diğer parti kaynaklarıyla uyumla."""
import hashlib
import json
import datetime
from pathlib import Path
from arsiv import html_source_text

checks = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
raw = Path('data/practices/04-dem.json').read_bytes()
review = Path('data/practices/04-dem-review.json').read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'f7c549bb34a5888f61fd0bda088f4602cebdedc96a95f8dda73b4b427b4da191'
assert hashlib.sha256(review).hexdigest() == '34f22005f5f5281a84f3e8d77a9c37ac5dc78f43d708b5b996f6fd1ac6a0f893'
package = json.loads(raw)
rows = [x for x in package['practice_records']['practice_event'] if x['id'] == '0406-2026-fund-1007']
assert len(rows) == 1
row = rows[0]
assert row['common_event_key'] == 'tbmm-28-5-003-fon-piyasasi-bilgilendirme'
assert row['title'] == 'Fon piyasaları hakkında Genel Kurul bilgilendirmesi'
assert row['scope_context'] == 'TBMM 28. dönem 5. yasama yılı 3. birleşimde fon piyasaları gündem dışı bilgilendirmesi'
assert row['occurrence_basis'] == '7 Ekim 2026 TBMM birleşimi tam tutanağı ve özeti.'
row.update(title='TBMM 3. Birleşimde fon piyasası açıklaması ve görüşler', scope_context='Cumhurbaşkanı Yardımcısı Cevdet Yılmaz fon piyasalarına ilişkin Genel Kurulda açıklama yaptı. Siyasi parti grupları ve grubu bulunmayan bir milletvekili görüşlerini bildirdi.', occurrence_basis='TBMM birleşim tutanağı ve ilgili işlem belgeleri.')
text = html_source_text(Path('data/practices/sources/dem/objects/248d35a6070a1858effe9173b47f9a2824c090fa85f74fa1fb5ae2eab6631a1c/original.html.bin').read_bytes())
exact = 'grubu bulunmayan İstanbul Milletvekili İskender Bayhan’ın aynı konuda konuşmaları'
assert exact in text
pid = '0406-2026-10-07-bayhan-role-p'
version = '0406-2026-10-07-full-v1'
section = 'Grubu bulunmayan İskender Bayhan konuşması'
package['entries'].append(dict(kind='passage', values=dict(id=pid, version_id=version, exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=None, printed_page=None)))
package['practice_records']['practice_event_evidence'].append(dict(event_id=row['id'], passage_id=pid, supported_point='Grubu bulunmayan İskender Bayhan aynı konuda konuştu.', stage='action', concrete_basis='TBMM birleşiminin konuşmacı dökümü.', limitation='Konuşmacı kimliği, oy veya uygulama sonucu değildir.', epistemic_type='claim'))
package['practice_records']['practice_evidence_assessment'].append(dict(event_id=row['id'], passage_id=pid, stage='action', basis_kind='document'))
review_obj = json.loads(review)
for kind, ident in [('practice_event', row['id']), ('practice_dispute', '0406-2026-fund-1007-dispute')]:
    existing = next(x for x in review_obj['practice_source_review'] if x['subject_kind']==kind and x['subject_id']==ident)
    existing['passage_ids'] = json.dumps(json.loads(existing['passage_ids'])+[pid], ensure_ascii=False)
    existing['inspected_sections'] = json.dumps(json.loads(existing['inspected_sections'])+[section], ensure_ascii=False)
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
review_obj['practice_source_review'].append(dict(subject_kind='practice_event_evidence', subject_id=row['id']+'|'+pid+'|action', reviewer_kind='agent', reviewed_at=now, source_version_ids=json.dumps([version]), passage_ids=json.dumps([pid]), inspected_sections=json.dumps([section], ensure_ascii=False), supported_claim='Bayhan aynı konuda konuştu.', limitations='Konuşmacı kimliği oy veya uygulama sonucu değildir.', result='reviewed', reason='TBMM konuşmacı dökümündeki ifade karşılaştırıldı.'))
review_obj['source_review_refs'] = [dict(subject_kind=x['subject_kind'], subject_id=x['subject_id']) for x in review_obj['practice_source_review']]
out = checks / 'fund-event-alignment-draft.json'
out.write_text(json.dumps(package, ensure_ascii=False, indent=2)+'\n')
review_out = checks / 'fund-event-alignment-review.json'
review_out.write_text(json.dumps(review_obj, ensure_ascii=False, indent=2)+'\n')
print('ALIGNED_PACKAGE', hashlib.sha256(out.read_bytes()).hexdigest())
print('ALIGNED_REVIEW', hashlib.sha256(review_out.read_bytes()).hexdigest())
