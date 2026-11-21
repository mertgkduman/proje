import json
from datetime import datetime, timezone
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
entries = json.loads((p/'child-labor-question-records-draft.json').read_text())['entries']
r = {k: [] for k in ('practice_event', 'practice_event_evidence', 'practice_evidence_assessment', 'practice_relation')}
ev, fid, sid = '0404-cocuk-soru-51913-event', '0404-cocuk-soru-51913-iliski', '0404-cocuk-isciligi-statement'
program, summary = '0303-epm-program-cocuk-isciligi-p1', '0303-epm-program-cocuk-isciligi-summary'
proposal, owner, date, recipient = '0404-tbmm-cocuk-soru-51913-p', '0404-tbmm-cocuk-soru-51913-owner-p', '0404-tbmm-cocuk-soru-51913-date-p', '0404-tbmm-cocuk-soru-51913-recipient-p'
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
for ident, exact, section in [(owner, '&#x130;stanbul Milletvekili Ay&#x15F;e Sibel YANIK&#xD6;MERO&#x11E;LU', 'Önerge sahibi'), (date, '23.10.2026', 'Başkanlığa geliş tarihi'), (recipient, '&#xC7;al&#x131;&#x15F;ma Ve Sosyal G&#xFC;venlik Bakan&#x131; Vedat I&#x15E;IKHAN', 'Önerge muhatabı')]:
    assert exact in Path('/tmp/gsd-0404-751913.html').read_text()
    entries.append(dict(kind='passage', values=dict(id=ident, version_id='0404-tbmm-cocuk-soru-51913-v1', exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=None, printed_page=None)))
entries.append(dict(kind='finding', values=dict(id=fid, party_id='yeni-parti', heading='Söylem ve uygulama', pair_id=fid, text='Kurucu program çocuk işçiliğini ve çocuk emeğinin ucuz iş gücü olarak kullanımını ortadan kaldırmayı öngörür. İstanbul Milletvekili Ayşe Sibel Yanıkömeroğlu 23 Ekim’de çocuk işçiliğiyle mücadele konusunda Çalışma ve Sosyal Güvenlik Bakanına yazılı soru yöneltti. Soru, yanıt veya çocuk işçiliğinin giderildiğini göstermez.', provenance='summary', epistemic_type='claim')))
for ref in (program, proposal, owner, date, recipient):
    entries.append(dict(kind='finding_evidence', values=dict(finding_id=fid, passage_id=ref, role='support')))
    entries.append(dict(kind='verification', values=dict(finding_id=fid, passage_id=ref, checked_at=now, result='confirmed', reason='Program ve TBMM soru konusu, sahibi ve geliş tarihi okundu.')))
entries.append(dict(kind='review', values=dict(id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program hedefi ile yazılı soru aşaması ayrıldı.')))
r['practice_event'].append(dict(id=ev, common_event_key='tbmm-28-7-51913', event_at='2026-10-23', date_precision='day', date_unknown_reason=None, scope_context='Çocuk işçiliği konusunda TBMM yazılı soru önergesi 7/51913', title='Çocuk işçiliği yazılı soru önergesi', occurrence_basis='TBMM kayıt sayfasında soru özeti, sahibi ve geliş tarihi.'))
for ref, point in ((proposal, 'Yazılı soru konusu'), (owner, 'Önerge sahibi'), (date, 'Başkanlığa geliş tarihi'), (recipient, 'Önerge muhatabı')):
    r['practice_event_evidence'].append(dict(event_id=ev, passage_id=ref, supported_point=point, stage='initiative', concrete_basis='TBMM soru kayıt sayfası.', limitation='Soru yanıt veya fiili sonuç kanıtı değildir.', epistemic_type='claim'))
    r['practice_evidence_assessment'].append(dict(event_id=ev, passage_id=ref, stage='initiative', basis_kind='document'))
r['practice_relation'].append(dict(id=fid+'-id', statement_id=sid, event_id=ev, party_id='yeni-parti', topic_id='cocuk-isciligi', scope_id=None, comparability_reason='Programdaki çocuk işçiliği hedefi ve aynı konuya ilişkin yazılı soru ilişkilidir.', target_finding_id=summary, result_finding_id=None, explanation_finding_id=fid, temporal_context='Program 24 Temmuz, soru 23 Ekim 2026 tarihlidir.', authority_context='Milletvekilinin yazılı sorusu bakanlık yanıtı veya uygulama sonucu değildir.', uncertainty_reason='Kesim tarihindeki yanıt durumu ayrıca incelenmeli; sonuç çıkarılmaz.'))
(p/'child-labor-question-slice-draft.json').write_text(json.dumps(dict(status='draft_unvalidated', requires_statement=sid, entries=entries, practice_records=r), ensure_ascii=False, indent=2)+'\n')
