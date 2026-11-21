import json
from datetime import datetime, timezone
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
all_source = json.loads((p/'housing-access-records-draft.json').read_text())['entries']
program = ['0303-epm-program-barinma-konut-p1', '0303-epm-program-detail-barinma-konut-p2']
summary, sid = '0303-epm-program-barinma-konut-summary', '0404-barinma-program-statement'
specs = [
    ('3952', '2-3952', '2026-10-15', '15/10/2026', 'Evrim KARAKOZ', 'Öğrenci barınma desteği kanun teklifi', 'Aydın Milletvekili Evrim Karakoz 15 Ekim’de yurt kapasitesi nedeniyle yerleşemeyen ihtiyaç sahibi öğrencilere barınma desteği ile ilk kira ve depozito giderinin karşılanmasını öngören kanun teklifini verdi.', 'Teklif kanunlaştığını veya öğrencilere ödeme yapıldığını göstermez.'),
    ('104686', '10-4686', '2026-10-12', '12/10/2026', 'Sakarya Milletvekili Ay&#xE7;a Ta&#x15F;kent ve 19 Milletvekili', 'Kira etkileri araştırma önergesi', 'Sakarya Milletvekili Ayça Taşkent ve 19 milletvekili 12 Ekim’de konut kiralarının hane gelirleri ve yaşam koşulları üzerindeki etkilerinin araştırılmasını istedi.', 'Araştırma talebi komisyon kurulduğunu veya kira desteği sağlandığını göstermez.'),
]
entries = []
records = {k: [] for k in ('practice_event', 'practice_event_evidence', 'practice_evidence_assessment', 'practice_relation')}
reviews = []
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
for num, common, day, date_exact, owner_exact, title, action, limit in specs:
    prefix = '0404-tbmm-housing-access-'+num
    entries += [e for e in all_source if any(str(e['values'].get(k, '')).startswith(prefix) for k in ('id', 'version_id', 'document_id'))]
    raw = Path('/tmp/gsd-0404-'+num+'.html').read_text()
    ev, fid = '0404-housing-'+num+'-event', '0404-housing-'+num+'-relation'
    proposal, owner, date = prefix+'-p', prefix+'-owner-p', prefix+'-date-p'
    for ident, exact, section in [(owner, owner_exact, 'İlk imza veya önerge sahibi'), (date, date_exact, 'Başkanlığa geliş tarihi')]:
        assert exact in raw
        entries.append(dict(kind='passage', values=dict(id=ident, version_id=prefix+'-v1', exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=None, printed_page=None)))
    intro = 'Kurucu program sosyal konutu, kiralık sosyal konutu ve öğrenciler dahil kırılgan gruplara özel barınma programlarını öngörür. '
    entries.append(dict(kind='finding', values=dict(id=fid, party_id='yeni-parti', heading='Söylem ve uygulama', pair_id=fid, text=intro+action+' '+limit, provenance='summary', epistemic_type='claim')))
    refs = program+[proposal, owner, date]
    for ref in refs:
        entries.append(dict(kind='finding_evidence', values=dict(finding_id=fid, passage_id=ref, role='support')))
        entries.append(dict(kind='verification', values=dict(finding_id=fid, passage_id=ref, checked_at=now, result='confirmed', reason='Program ve TBMM kaydında amaç, sahip ve geliş tarihi okundu.')))
    entries.append(dict(kind='review', values=dict(id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program hedefiyle teklifin veya araştırma talebinin aşaması ayrıldı.')))
    records['practice_event'].append(dict(id=ev, common_event_key='tbmm-28-'+common, event_at=day, date_precision='day', date_unknown_reason=None, scope_context='TBMM '+common.replace('-', '/')+' kaydı', title=title, occurrence_basis='TBMM kaydındaki özet, sahip ve geliş tarihi.'))
    for ref, point in ((proposal, 'Kayıt konusu'), (owner, 'Önerge veya teklif sahibi'), (date, 'Başkanlığa geliş tarihi')):
        records['practice_event_evidence'].append(dict(event_id=ev, passage_id=ref, supported_point=point, stage='initiative', concrete_basis='TBMM kayıt sayfası.', limitation=limit, epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=ev, passage_id=ref, stage='initiative', basis_kind='document'))
    records['practice_relation'].append(dict(id=fid+'-id', statement_id=sid, event_id=ev, party_id='yeni-parti', topic_id='barinma-konut', scope_id=None, comparability_reason='Programın barınma hedefi ile barınma konulu yasama girişimi ilişkilidir.', target_finding_id=summary, result_finding_id=None, explanation_finding_id=fid, temporal_context='Program 24 Temmuz 2026, girişim '+day+' tarihlidir.', authority_context='Milletvekili girişimi uygulama veya kanun sonucu değildir.', uncertainty_reason='Kesim tarihindeki daha sonraki işlem ayrıca incelenmeli; sonuç çıkarılmaz.'))
    items = [('practice_event_evidence', ev+'|'+ref+'|initiative', [ref], point) for ref, point in ((proposal, 'Kayıt konusu'), (owner, 'Kayıt sahibi'), (date, 'Geliş tarihi'))]
    items += [('practice_event', ev, refs[2:], title), ('practice_relation', fid+'-id', refs, 'Program ve girişim barınma konusundadır.'), ('practice_relation.target_finding_id', fid+'-id', [program[0]], 'Hedef programın konut hükmüdür.'), ('practice_relation.explanation_finding_id', fid+'-id', refs, 'Girişim fiili sonuç sayılmaz.')]
    for kind, subject, evidence, claim in items:
        versions = ['epm-program-v1' if x in program else prefix+'-v1' for x in evidence]
        reviews.append(dict(subject_kind=kind, subject_id=subject, reviewer_kind='agent', reviewed_at=now, source_version_ids=json.dumps(list(dict.fromkeys(versions)), ensure_ascii=False), passage_ids=json.dumps(evidence, ensure_ascii=False), inspected_sections=json.dumps(['Program barınma hükmü' if x in program else title+' TBMM künyesi' for x in evidence], ensure_ascii=False), supported_claim=claim, limitations=limit, result='reviewed', reason='Kurucu program ve TBMM kaydı karşılaştırıldı.'))
(p/'housing-extra-slices-draft.json').write_text(json.dumps(dict(status='draft_unvalidated', requires_statement=sid, entries=entries, practice_records=records), ensure_ascii=False, indent=2)+'\n')
(p/'housing-extra-review-draft.json').write_text(json.dumps(dict(status='draft_unvalidated', practice_source_review=reviews), ensure_ascii=False, indent=2)+'\n')
