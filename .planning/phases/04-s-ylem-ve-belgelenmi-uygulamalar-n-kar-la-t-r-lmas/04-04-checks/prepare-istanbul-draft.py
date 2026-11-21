import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
pkg=json.loads((p/'package-samsun-congress-draft.json').read_text())
extra=json.loads((p/'october-referral-records-draft.json').read_text())['entries']
pkg['entries'] += [x for x in extra if any(str(x['values'].get(k,'')).startswith('0404-istanbul-onsecim-sozcu') for k in ('id','version_id','document_id'))]
e=pkg['entries'];r=pkg['practice_records'];event='0404-istanbul-onsecim-event';fid='0404-istanbul-onsecim-iliski';ref='0404-istanbul-onsecim-sozcu-p';speech='0105-speech-p';now='2026-11-21T22:27:52+00:00'
e.append(dict(kind='finding',values=dict(id=fid,party_id='yeni-parti',heading='Söylem ve uygulama',pair_id=fid,text='Sözcü’nün ANKA haberine göre, İstanbul il başkanlığı ön seçiminde Özgür Çelik tek aday olarak resmî olmayan sonuca göre birinci oldu. Ön seçim ile il kongresi ayrı aşamalardır; sandık tutanağı görülmedi.',provenance='summary',epistemic_type='claim')))
for x in (speech,ref):
    e.append(dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=x,role='support')))
    e.append(dict(kind='verification',values=dict(finding_id=fid,passage_id=x,checked_at=now,result='confirmed',reason='Beyan ve ANKA kaynaklı resmî olmayan ön seçim haberi okundu.')))
e.append(dict(kind='review',values=dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Yerel ön seçim, kongre ve resmî olmayan sonuç ayrımı korundu.')))
r['practice_event'].append(dict(id=event,common_event_key='yeni-parti-istanbul-2026-onsecim',event_at='2026-10-18',date_precision='day',date_unknown_reason=None,scope_context='İstanbul il başkanlığı ön seçimi',title='İstanbul il başkanlığı ön seçimi',occurrence_basis='18 Ekim Sözcü/ANKA haberi resmî olmayan sonucu bildiriyor.'))
r['practice_event_evidence'].append(dict(event_id=event,passage_id=ref,supported_point='Habere göre Çelik tek adaylı ön seçimi kazandı.',stage='action',concrete_basis='ANKA kaynaklı Sözcü ön seçim haberi.',limitation='Sonuç resmî olmayan olarak bildirildi; sandık tutanağı görülmedi.',epistemic_type='claim'))
r['practice_evidence_assessment'].append(dict(event_id=event,passage_id=ref,stage='action',basis_kind='independent_report'))
r['practice_relation'].append(dict(id=fid+'-id',statement_id='tracer-statement',event_id=event,party_id='yeni-parti',topic_id='organ-secim-yontemi',scope_id=None,comparability_reason='Üyelerin katıldığı il başkanlığı ön seçimi başkan belirleme beyanına ilişkindir.',target_finding_id='0105-statement',result_finding_id=None,explanation_finding_id=fid,temporal_context='Beyan 4 Ağustos, ön seçim 18 Ekim 2026 tarihlidir.',authority_context='Üyelerin ön seçimi ile kongre işlemleri ayrı gösterilir.',uncertainty_reason='Sonuç resmî olmayan olarak bildirildi; sandık tutanağı görülmedi.'))
(p/'package-istanbul-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
