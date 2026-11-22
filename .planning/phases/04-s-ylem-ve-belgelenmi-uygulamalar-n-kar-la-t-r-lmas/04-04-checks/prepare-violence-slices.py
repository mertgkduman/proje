import json
from datetime import datetime, timezone
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
entries = json.loads((p/'violence-records-draft.json').read_text())['entries']
r = {k: [] for k in ('practice_statement', 'practice_event', 'practice_event_evidence', 'practice_evidence_assessment', 'practice_relation')}
base = '0303-epm-program-detail2-toplumsal-cinsiyet-'
program = [base+'p'+str(i) for i in range(1,6)]; summary, quote = base+'summary', base+'quote'
sid = '0404-siddet-program-statement'; now = datetime.now(timezone.utc).isoformat(timespec='seconds')
for finding, refs in ((summary, program), (quote, program[:1])):
    for ref in refs: entries.append(dict(kind='verification', values=dict(finding_id=finding, passage_id=ref, checked_at=now, result='confirmed', reason='Kurucu programın toplumsal cinsiyet hükümleri özgün pasajlarla karşılaştırıldı.')))
r['practice_statement'].append(dict(id=sid, party_id='yeni-parti', topic_id='toplumsal-cinsiyet', taxonomy_version=4, summary_finding_id=summary, quote_finding_id=quote, statement_at='2026-07-24', date_precision='day', version_id='epm-program-v1', period_basis='24 Temmuz 2026 kurucu programı.', uncertainty_reason='Program şiddetle mücadele mekanizmaları için uygulama takvimi belirtmiyor.', comparison_row_id='04-03-v3-0303-epm-program-detail2-toplumsal-cinsiyet-row'))
specs = [
    ('104683', '10-4683', '2026-10-12', '12/10/2026', 'Sakarya Milletvekili Ay&#xE7;a Ta&#x15F;kent ve 19 Milletvekili', 'Kadına yönelik şiddet araştırma önergesi', 'Sakarya Milletvekili Ayça Taşkent ve 19 milletvekili 12 Ekim’de kadına yönelik şiddetin önlenmesi için Meclis araştırması istedi.', 'Araştırma talebi komisyon kurulması veya şiddetin önlenmesi sonucu değildir.'),
    ('749746', '7-49746', '2026-09-29', '29.09.2026', '&#x130;stanbul Milletvekili Ali G&#xD6;K&#xC7;EK', 'Kadına yönelik şiddet yazılı sorusu', 'İstanbul Milletvekili Ali Gökçek 29 Eylül’de kadına yönelik şiddet ve kadın cinayetlerinin önlenmesi hakkında yazılı soru yöneltti.', 'Yazılı soru yanıt veya fiili sonuç değildir.'),
]
reviews = []
def review(kind, subject, refs, claim, limit, prefix):
    versions = ['epm-program-v1' if ref in program else prefix+'-v1' for ref in refs]
    reviews.append(dict(subject_kind=kind, subject_id=subject, reviewer_kind='agent', reviewed_at=now, source_version_ids=json.dumps(list(dict.fromkeys(versions)), ensure_ascii=False), passage_ids=json.dumps(refs, ensure_ascii=False), inspected_sections=json.dumps(['Program toplumsal cinsiyet hükmü' if ref in program else 'TBMM önerge künyesi' for ref in refs], ensure_ascii=False), supported_claim=claim, limitations=limit, result='reviewed', reason='Kurucu program ve TBMM kaydı karşılaştırıldı.'))
for k, refs in (('practice_statement',program), ('practice_statement.summary_finding_id',program), ('practice_statement.quote_finding_id',program[:1])): review(k,sid,refs,'Program şiddetle mücadele ve eşitlik hükümlerini içerir.','Program uygulama sonucu değildir.','')
for num, common, day, date_exact, owner_exact, title, action, limit in specs:
    prefix='0404-tbmm-kadina-siddet-'+num; proposal, owner, date = prefix+'-p', prefix+'-owner-p', prefix+'-date-p'
    ev, fid = '0404-siddet-'+num+'-event', '0404-siddet-'+num+'-relation'; raw=Path('/tmp/gsd-0404-'+num+'.html').read_text()
    for ident, exact, section in ((owner,owner_exact,'Önerge sahibi'),(date,date_exact,'Başkanlığa geliş tarihi')):
        assert exact in raw
        entries.append(dict(kind='passage', values=dict(id=ident, version_id=prefix+'-v1', exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=None, printed_page=None)))
    entries.append(dict(kind='finding', values=dict(id=fid, party_id='yeni-parti', heading='Söylem ve uygulama', pair_id=fid, text='Kurucu program kadına yönelik şiddet ve kadın cinayetleriyle mücadele mekanizmaları öngörür. '+action+' '+limit, provenance='summary', epistemic_type='claim')))
    refs = [program[1],proposal,owner,date]
    for ref in refs:
        entries.append(dict(kind='finding_evidence', values=dict(finding_id=fid, passage_id=ref, role='support')))
        entries.append(dict(kind='verification', values=dict(finding_id=fid, passage_id=ref, checked_at=now, result='confirmed', reason='Program ve TBMM kaydındaki konu, sahip ve tarih okundu.')))
    entries.append(dict(kind='review', values=dict(id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program hedefi ve parlamenter girişimin aşaması ayrıldı.')))
    r['practice_event'].append(dict(id=ev, common_event_key='tbmm-28-'+common, event_at=day, date_precision='day', date_unknown_reason=None, scope_context='TBMM '+common.replace('-', '/')+' kaydı', title=title, occurrence_basis='TBMM kayıt sayfasında konu, sahip ve geliş tarihi.'))
    for ref, point in ((proposal,'Girişim konusu'),(owner,'Önerge sahibi'),(date,'Başkanlığa geliş tarihi')):
        r['practice_event_evidence'].append(dict(event_id=ev, passage_id=ref, supported_point=point, stage='initiative', concrete_basis='TBMM kayıt sayfası.', limitation=limit, epistemic_type='claim'))
        r['practice_evidence_assessment'].append(dict(event_id=ev, passage_id=ref, stage='initiative', basis_kind='document'))
        review('practice_event_evidence',ev+'|'+ref+'|initiative',[ref],point,limit,prefix)
    r['practice_relation'].append(dict(id=fid+'-id', statement_id=sid, event_id=ev, party_id='yeni-parti', topic_id='toplumsal-cinsiyet', scope_id=None, comparability_reason='Program hükmü ve parlamenter girişim kadına yönelik şiddetin önlenmesiyle ilişkilidir.', target_finding_id=summary, result_finding_id=None, explanation_finding_id=fid, temporal_context='Program 24 Temmuz 2026, girişim '+day+' tarihlidir.', authority_context='Milletvekili girişimi komisyon, yanıt veya uygulama sonucu değildir.', uncertainty_reason='Kesimde sonraki işlem ayrıca incelenmeli; sonuç çıkarılmaz.'))
    review('practice_event',ev,refs[1:],title,limit,prefix)
    review('practice_relation',fid+'-id',refs,'Program ve girişim şiddetin önlenmesi konusundadır.',limit,prefix)
    review('practice_relation.target_finding_id',fid+'-id',program,'Hedef programın toplumsal cinsiyet hükmüdür.',limit,prefix)
    review('practice_relation.explanation_finding_id',fid+'-id',refs,'Girişim gerçekleşmiş sonuç sayılmaz.',limit,prefix)
(p/'violence-slices-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries,practice_records=r),ensure_ascii=False,indent=2)+'\n')
(p/'violence-review-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',practice_source_review=reviews),ensure_ascii=False,indent=2)+'\n')
