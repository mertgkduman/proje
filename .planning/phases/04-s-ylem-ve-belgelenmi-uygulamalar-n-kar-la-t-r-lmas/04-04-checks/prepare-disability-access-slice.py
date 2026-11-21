import json
from datetime import datetime, timezone
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
source = json.loads((p/'housing-access-records-draft.json').read_text())['entries']
prefix = '0404-tbmm-housing-access-752416'
entries = [e for e in source if any(str(e['values'].get(k, '')).startswith(prefix) for k in ('id', 'version_id', 'document_id'))]
r = {k: [] for k in ('practice_statement', 'practice_event', 'practice_event_evidence', 'practice_evidence_assessment', 'practice_relation')}
ev, fid, sid = '0404-engelli-erisim-752416-event', '0404-engelli-erisim-752416-iliski', '0404-engelli-erisim-program-statement'
program, summary, quote = '0303-epm-program-engellilik-p1', '0303-epm-program-engellilik-summary', '0303-epm-program-engellilik-quote'
proposal, owner, date, recipient = prefix+'-p', prefix+'-owner-p', prefix+'-date-p', prefix+'-recipient-p'
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
raw = Path('/tmp/gsd-0404-752416.html').read_text()
for ident, exact, section in [(owner, 'Diyarbak&#x131;r Milletvekili Mustafa Sezgin TANRIKULU', 'Önerge sahibi'), (date, '03.11.2026', 'Başkanlığa geliş tarihi'), (recipient, 'Aile Ve Sosyal Hizmetler Bakan&#x131; Mahinur &#xD6;ZDEM&#x130;R G&#xD6;KTA&#x15E;', 'Önerge muhatabı')]:
    assert exact in raw
    entries.append(dict(kind='passage', values=dict(id=ident, version_id=prefix+'-v1', exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=None, printed_page=None)))
for finding in (summary, quote):
    entries.append(dict(kind='verification', values=dict(finding_id=finding, passage_id=program, checked_at=now, result='confirmed', reason='Programın erişilebilirlik hükmü özgün pasajda okundu.')))
entries.append(dict(kind='finding', values=dict(id=fid, party_id='yeni-parti', heading='Söylem ve uygulama', pair_id=fid, text='Kurucu program engelli bireyler için ulusal erişilebilirlik seferberliği ve kamusal alanların erişilebilirliğini öngörür. Diyarbakır Milletvekili Mustafa Sezgin Tanrıkulu 3 Kasım’da Diyarbakır’da engelli bireylere sunulan hizmetlerin erişilebilirlik düzeyi hakkında Aile ve Sosyal Hizmetler Bakanına yazılı soru yöneltti. Soru yanıt veya erişilebilirliğin sağlandığını göstermez.', provenance='summary', epistemic_type='claim')))
for ref in (program, proposal, owner, date, recipient):
    entries.append(dict(kind='finding_evidence', values=dict(finding_id=fid, passage_id=ref, role='support')))
    entries.append(dict(kind='verification', values=dict(finding_id=fid, passage_id=ref, checked_at=now, result='confirmed', reason='Program ve TBMM sorusunun konusu, sahibi, tarihi ve muhatabı okundu.')))
entries.append(dict(kind='review', values=dict(id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program hedefi ve yazılı soru aşaması ayrıldı.')))
r['practice_statement'].append(dict(id=sid, party_id='yeni-parti', topic_id='engellilik', taxonomy_version=4, summary_finding_id=summary, quote_finding_id=quote, statement_at='2026-07-24', date_precision='day', version_id='epm-program-v1', period_basis='24 Temmuz 2026 kurucu programı.', uncertainty_reason='Program hükmü erişilebilirlik seferberliği için takvim belirtmiyor.', comparison_row_id='04-03-v3-0303-epm-program-engellilik-row'))
r['practice_event'].append(dict(id=ev, common_event_key='tbmm-28-7-52416', event_at='2026-11-03', date_precision='day', date_unknown_reason=None, scope_context='Diyarbakır engelli hizmetleri hakkında TBMM yazılı soru önergesi 7/52416', title='Engelli hizmetlerinde erişilebilirlik yazılı sorusu', occurrence_basis='TBMM kaydında soru özeti, sahibi, muhatabı ve geliş tarihi.'))
for ref, point in ((proposal, 'Yazılı soru konusu'), (owner, 'Önerge sahibi'), (date, 'Başkanlığa geliş tarihi'), (recipient, 'Önerge muhatabı')):
    r['practice_event_evidence'].append(dict(event_id=ev, passage_id=ref, supported_point=point, stage='initiative', concrete_basis='TBMM soru kayıt sayfası.', limitation='Yazılı soru yanıt veya erişilebilirlik sonucu değildir.', epistemic_type='claim'))
    r['practice_evidence_assessment'].append(dict(event_id=ev, passage_id=ref, stage='initiative', basis_kind='document'))
r['practice_relation'].append(dict(id=fid+'-id', statement_id=sid, event_id=ev, party_id='yeni-parti', topic_id='engellilik', scope_id=None, comparability_reason='Programın erişilebilirlik hedefi ve hizmetlerin erişilebilirliğine ilişkin soru ilişkilidir.', target_finding_id=summary, result_finding_id=None, explanation_finding_id=fid, temporal_context='Program 24 Temmuz, yazılı soru 3 Kasım 2026 tarihlidir.', authority_context='Milletvekilinin yazılı sorusu bakanlık yanıtı veya uygulama sonucu değildir.', uncertainty_reason='Kesim anındaki yanıt durumu ayrıca incelenmeli; sonuç çıkarılmaz.'))
(p/'disability-access-slice-draft.json').write_text(json.dumps(dict(status='draft_unvalidated', entries=entries, practice_records=r), ensure_ascii=False, indent=2)+'\n')
