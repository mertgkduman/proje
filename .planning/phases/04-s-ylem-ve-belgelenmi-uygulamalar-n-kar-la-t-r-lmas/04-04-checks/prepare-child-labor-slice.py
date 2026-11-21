import json
from datetime import datetime, timezone
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
source = json.loads((p/'child-labor-research-records-draft.json').read_text())['entries']
entries = [e for e in source if any(str(e['values'].get(k, '')).startswith('0404-tbmm-cocuk-emegi-4687') for k in ('id', 'version_id', 'document_id'))]
r = {k: [] for k in ('practice_statement', 'practice_event', 'practice_event_evidence', 'practice_evidence_assessment', 'practice_relation')}
ev, fid, sid = '0404-cocuk-emegi-4687-event', '0404-cocuk-emegi-4687-iliski', '0404-cocuk-isciligi-statement'
program, summary, quote = '0303-epm-program-cocuk-isciligi-p1', '0303-epm-program-cocuk-isciligi-summary', '0303-epm-program-cocuk-isciligi-quote'
proposal, owner, date = '0404-tbmm-cocuk-emegi-4687-p', '0404-tbmm-cocuk-emegi-4687-owner-p', '0404-tbmm-cocuk-emegi-4687-date-p'
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
for ident, exact, section in [(owner, 'Sakarya Milletvekili Ay&#xE7;a Ta&#x15F;kent ve 19 Milletvekili', 'Önerge sahibi'), (date, '12/10/2026', 'Başkanlığa geliş tarihi')]:
    assert exact in Path('/tmp/gsd-0404-104687.html').read_text()
    entries.append(dict(kind='passage', values=dict(id=ident, version_id='0404-tbmm-cocuk-emegi-4687-v1', exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=None, printed_page=None)))
for f in (summary, quote):
    entries.append(dict(kind='verification', values=dict(finding_id=f, passage_id=program, checked_at=now, result='confirmed', reason='Programın çocuk işçiliği hükmü özgün pasajla karşılaştırıldı.')))
entries.append(dict(kind='finding', values=dict(id=fid, party_id='yeni-parti', heading='Söylem ve uygulama', pair_id=fid, text='Kurucu program çocuk işçiliğini ve çocuk emeğinin ucuz iş gücü olarak kullanımını ortadan kaldırmayı öngörür. Sakarya Milletvekili Ayça Taşkent ve 19 milletvekili 12 Ekim’de çocuk işçiliği, çocuk yoksulluğu ve MESEM kapsamındaki öğrenci istihdamı hakkında Meclis araştırması istedi. Araştırma talebi komisyon kurulduğunu veya çocuk işçiliğinin giderildiğini göstermez.', provenance='summary', epistemic_type='claim')))
for ref in (program, proposal, owner, date):
    entries.append(dict(kind='finding_evidence', values=dict(finding_id=fid, passage_id=ref, role='support')))
    entries.append(dict(kind='verification', values=dict(finding_id=fid, passage_id=ref, checked_at=now, result='confirmed', reason='Program ve TBMM önerge konusu, sahibi ve geliş tarihi okundu.')))
entries.append(dict(kind='review', values=dict(id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program hedefi ile milletvekillerinin araştırma isteği ve aşaması ayrıldı.')))
r['practice_statement'].append(dict(id=sid, party_id='yeni-parti', topic_id='cocuk-isciligi', taxonomy_version=4, summary_finding_id=summary, quote_finding_id=quote, statement_at='2026-07-24', date_precision='day', version_id='epm-program-v1', period_basis='24 Temmuz 2026 kurucu programı.', uncertainty_reason='Program hedefe ilişkin uygulama tarihi belirtmiyor.', comparison_row_id='04-03-v3-0303-epm-program-cocuk-isciligi-row'))
r['practice_event'].append(dict(id=ev, common_event_key='tbmm-28-10-4687', event_at='2026-10-12', date_precision='day', date_unknown_reason=None, scope_context='Çocuk işçiliği ve MESEM hakkında TBMM araştırma önergesi 10/4687', title='Çocuk işçiliği araştırma önergesi', occurrence_basis='TBMM kaydında önerge özeti, sahibi ve geliş tarihi.'))
for ref, point in ((proposal, 'Araştırma talebinin konusu'), (owner, 'Önerge sahibi ve diğer 19 milletvekili'), (date, 'Başkanlığa geliş tarihi')):
    r['practice_event_evidence'].append(dict(event_id=ev, passage_id=ref, supported_point=point, stage='initiative', concrete_basis='TBMM önerge kayıt sayfası.', limitation='Araştırma talebi komisyon kurulması veya toplumsal sonuç kanıtı değildir.', epistemic_type='claim'))
    r['practice_evidence_assessment'].append(dict(event_id=ev, passage_id=ref, stage='initiative', basis_kind='document'))
r['practice_relation'].append(dict(id=fid+'-id', statement_id=sid, event_id=ev, party_id='yeni-parti', topic_id='cocuk-isciligi', scope_id=None, comparability_reason='Programın çocuk işçiliği hedefi ile bu konuda araştırma talebi ilişkilidir.', target_finding_id=summary, result_finding_id=None, explanation_finding_id=fid, temporal_context='Program 24 Temmuz, önerge 12 Ekim 2026 tarihlidir.', authority_context='Milletvekillerinin araştırma isteği komisyon kararı veya uygulama sonucu değildir.', uncertainty_reason='Kesim tarihindeki sonraki işlem ayrıca incelenmeli; sonuç çıkarılmaz.'))
(p/'child-labor-slice-draft.json').write_text(json.dumps(dict(status='draft_unvalidated', entries=entries, practice_records=r), ensure_ascii=False, indent=2)+'\n')
