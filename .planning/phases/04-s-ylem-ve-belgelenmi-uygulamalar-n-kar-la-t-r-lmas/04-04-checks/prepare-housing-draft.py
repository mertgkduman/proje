import json
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
pkg=json.loads((p/'package-national-draft.json').read_text())
pkg['entries'] += json.loads((p/'housing-transcript-records-draft.json').read_text())['entries']
e=pkg['entries']; rec=pkg['practice_records']; now='2026-11-21T20:46:19+00:00'
program='0303-epm-program-barinma-konut-p1'; target='0303-epm-program-barinma-konut-summary'; quote='0303-epm-program-barinma-konut-quote'; proposal='0404-barinma-grup-oneri-p'; result='0404-barinma-grup-oylama-p'; fid='0404-barinma-iliski'; event='0404-barinma-grup-onerisi'
for finding in (target,quote):
 e.append(dict(kind='verification',values=dict(finding_id=finding,passage_id=program,checked_at=now,result='confirmed',reason='Kurucu programın sosyal konut hükmü özgün pasajla karşılaştırıldı.')))
e.append(dict(kind='finding',values=dict(id=fid,party_id='yeni-parti',heading='Söylem ve uygulama',pair_id=fid,text='Program sosyal konut stokunu artırmayı ve kiralık sosyal konut modellerini geliştirmeyi önerir. Yeni Parti grubu, barınma krizinin araştırılmasına yönelik önergenin 7 Ağustos birleşiminde öne alınmasını istedi; grup önerisi kabul edilmedi. Bu girişim sosyal konut üretildiğini göstermez.',provenance='summary',epistemic_type='claim')))
for ref in (program,proposal,result):
 e.append(dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=ref,role='support')))
 e.append(dict(kind='verification',values=dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='Program ve TBMM tutanağında grup önerisi ile oylama ayrı okundu; temel önergenin sonraki sonucu ve konut üretimi çıkarılmadı.')))
e.append(dict(kind='review',values=dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program ve Genel Kurul tutanağı karşılaştırıldı; girişim ile sonuç ayrıldı.')))
rec['practice_event'].append(dict(id=event,common_event_key='tbmm-122-yeni-parti-barinma-grup-onerisi',event_at='2026-08-07',date_precision='day',date_unknown_reason=None,scope_context='TBMM 122. birleşim grup önerisi',title='Barınma araştırması grup önerisi',occurrence_basis='TBMM ham tutanağı grup önerisi ve oylamayı kaydediyor.'))
for ref,point in [(proposal,'Araştırma önergesinin öne alınması ve görüşülmesi talebi'),(result,'Grup önerisinin kabul edilmemesi')]:
 rec['practice_event_evidence'].append(dict(event_id=event,passage_id=ref,supported_point=point,stage='initiative',concrete_basis='TBMM tutanağında öneri ile görüşme sonrası başkanın oylama sonucu kaydedilmiştir.',limitation='Temel araştırma önergesinin sonraki işlemleri ve sosyal konut üretimi bu oylamadan çıkarılamaz.',epistemic_type='claim'))
 rec['practice_evidence_assessment'].append(dict(event_id=event,passage_id=ref,stage='initiative',basis_kind='document'))
sid='0404-barinma-program-statement'; rec['practice_statement'].append(dict(id=sid,party_id='yeni-parti',topic_id='barinma-konut',taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2026-07-24',date_precision='day',version_id='epm-program-v1',period_basis='24 Temmuz 2026 kurucu programı.',uncertainty_reason='Program sosyal konut artışı için sayısal hedef ve süre belirtmiyor.',comparison_row_id='04-03-v3-0303-epm-program-barinma-konut-row'))
scope='practice-ce3d1cd2c77ff817ea05687582fd828fcd16f2b48803faad5a4a1dff07669b28'; rec['practice_scope_v2'].append(dict(id=scope,party_id='yeni-parti',topic_id='barinma-konut',taxonomy_version=4,period_start='2026-07-24',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='Grup önerisi ve diğer somut barınma uygulamaları araştırılıyor; kapsam açık.'))
rec['practice_relation'].append(dict(id='0404-barinma-iliski-id',statement_id=sid,event_id=event,party_id='yeni-parti',topic_id='barinma-konut',scope_id=scope,comparability_reason='Programın sosyal konut önerisi ile TBMM araştırma önergesi barınma sorununa ilişkindir; amaç ve araçları farklıdır.',target_finding_id=target,result_finding_id=None,explanation_finding_id=fid,temporal_context='Program 24 Temmuz; grup önerisi 7 Ağustos 2026 tarihlidir.',authority_context='Grup önerisi bir TBMM araştırması talebinin öne alınmasını ister; sosyal konut yapımına karar vermez.',uncertainty_reason='Reddedilen grup önerisidir; asıl araştırma önergesinin sonraki aşaması ve sosyal konut üretimi ayrıca incelenmelidir.'))
(p/'package-housing-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
print('HOUSING_DRAFT scope open; pending checks')
