import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
pkg=json.loads((p/'package-afyon-draft.json').read_text())
extra=json.loads((p/'october-referral-records-draft.json').read_text())['entries']
pkg['entries'] += [x for x in extra if any(str(x['values'].get(k,'')).startswith('0404-samsun-kongre-objektif') for k in ('id','version_id','document_id'))]
e=pkg['entries'];r=pkg['practice_records'];event='0404-samsun-kongre-event';fid='0404-samsun-kongre-iliski';ref='0404-samsun-kongre-objektif-p';speech='0105-speech-p';now='2026-11-21T22:25:03+00:00'
e.append(dict(kind='finding',values=dict(id=fid,party_id='yeni-parti',heading='Söylem ve uygulama',pair_id=fid,text='Samsun Objektif, 25 Ekim il kongresinde Mehmet Özdağ’ın geçerli 278 oyun 276’sını alarak il başkanı seçildiğini bildirdi. Kongre ve üyelerin ön seçimi ayrı aşamalardır; kongre tutanağı görülmedi.',provenance='summary',epistemic_type='claim')))
for x in (speech,ref):
    e.append(dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=x,role='support')))
    e.append(dict(kind='verification',values=dict(finding_id=fid,passage_id=x,checked_at=now,result='confirmed',reason='Beyan ve kongrenin yerel haberindeki sonuç okundu; ön seçimle ayrıldı.')))
e.append(dict(kind='review',values=dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Kongre haberi ve üyeler ön seçimi aşamaları ayrı değerlendirildi.')))
r['practice_event'].append(dict(id=event,common_event_key='yeni-parti-samsun-2026-il-kongre',event_at='2026-10-25',date_precision='day',date_unknown_reason=None,scope_context='Samsun il kongresinde delegelerin il başkanı seçimi',title='Samsun il kongresi',occurrence_basis='25 Ekim saat 22.23 yerel haber kongre sonucunu bildiriyor.'))
r['practice_event_evidence'].append(dict(event_id=event,passage_id=ref,supported_point='Haber Özdağ’ın kongrede 276 oyla seçildiğini aktarıyor.',stage='action',concrete_basis='Samsun Objektif kongre sonuç haberi.',limitation='Kongre tutanağı görülmedi; ön seçim itirazları ayrı araştırılır.',epistemic_type='claim'))
r['practice_evidence_assessment'].append(dict(event_id=event,passage_id=ref,stage='action',basis_kind='independent_report'))
r['practice_relation'].append(dict(id=fid+'-id',statement_id='tracer-statement',event_id=event,party_id='yeni-parti',topic_id='organ-secim-yontemi',scope_id=None,comparability_reason='İl başkanı belirleme sürecinin kongre aşaması üyelerin rolüne dair beyanın bağlamında gösterilir.',target_finding_id='0105-statement',result_finding_id=None,explanation_finding_id=fid,temporal_context='Beyan 4 Ağustos, üyeler ön seçimi 18 Ekim, kongre 25 Ekim 2026 tarihlidir.',authority_context='Ön seçim ile delegelerin kongre seçimi farklı işlemlerdir.',uncertainty_reason='Özgün kongre tutanağı görülmedi; ön seçim itirazları bu sonuçla çözülmüş sayılmaz.'))
(p/'package-samsun-congress-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
