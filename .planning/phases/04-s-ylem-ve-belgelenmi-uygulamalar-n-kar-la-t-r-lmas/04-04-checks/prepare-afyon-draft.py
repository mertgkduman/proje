import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
pkg=json.loads((p/'package-aydin-draft-v2.json').read_text())
extra=json.loads((p/'october-referral-records-draft.json').read_text())['entries']
pkg['entries'] += [x for x in extra if any(str(x['values'].get(k,'')).startswith('0404-afyon-onsecim-sehir') for k in ('id','version_id','document_id'))]
e=pkg['entries']; r=pkg['practice_records']; event='0404-afyon-onsecim-event'; fid='0404-afyon-onsecim-iliski'; ref='0404-afyon-onsecim-sehir-p'; plan='0404-afyon-kongre-plan-p'; speech='0105-speech-p'; now='2026-11-21T22:15:17+00:00'
e.append(dict(kind='passage',values=dict(id=plan,version_id='0404-afyon-onsecim-sehir-v1',exact='Yeni Parti Afyon İl Kongresi 25 Ekim Pazar günü Fuar Düğün Salonu&#8217;nda, ön seçimin galibi Faruk Duha Erhan&#8217;ın tek aday olarak katılmasıyla yapılması bekleniyor.',prefix=None,suffix=None,article=None,section='19 Ekim haberinde planlanan kongre',pdf_page_index=None,printed_page=None)))
e.append(dict(kind='finding',values=dict(id=fid,party_id='yeni-parti',heading='Söylem ve uygulama',pair_id=fid,text='Afyon Şehir, 18 Ekim Afyonkarahisar il başkanlığı ön seçiminde Faruk Duha Erhan’ın Hasan Karadeniz’in önünde birinci olduğunu bildirdi. Haberde 25 Ekim il kongresi sonraki ve henüz planlanan bir işlem olarak yer alıyor.',provenance='summary',epistemic_type='claim')))
for x in (speech,ref,plan):
    e.append(dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=x,role='support')))
    e.append(dict(kind='verification',values=dict(finding_id=fid,passage_id=x,checked_at=now,result='confirmed',reason='Beyan ile yerel haberin ön seçim ve planlanan kongre anlatımı ayrı okundu.')))
e.append(dict(kind='review',values=dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Ön seçim ile sonraki kongre ayırt edildi; resmî tutanak görülmedi.')))
r['practice_event'].append(dict(id=event,common_event_key='yeni-parti-afyon-2026-onsecim',event_at='2026-10-18',date_precision='day',date_unknown_reason=None,scope_context='Afyonkarahisar il başkanlığı üyeler ön seçimi',title='Afyonkarahisar il başkanlığı ön seçimi',occurrence_basis='19 Ekim yerel haberi 18 Ekim sandığını bildiriyor.'))
r['practice_event_evidence'].append(dict(event_id=event,passage_id=ref,supported_point='Yerel haber ön seçimde Erhan’ın birinci olduğunu bildiriyor.',stage='action',concrete_basis='Afyon Şehir 19 Ekim haberindeki ön seçim bildirimi.',limitation='Kongre henüz haber tarihindeki plandır; resmî ön seçim tutanağı görülmedi.',epistemic_type='claim'))
r['practice_event_evidence'].append(dict(event_id=event,passage_id=plan,supported_point='Haberde kongre ileri tarihli bir beklentidir.',stage='action',concrete_basis='Afyon Şehir 19 Ekim haberindeki kongre beklentisi.',limitation='Bu pasaj kongrenin gerçekleştiğini göstermez.',epistemic_type='claim'))
r['practice_evidence_assessment'].append(dict(event_id=event,passage_id=ref,stage='action',basis_kind='independent_report'))
r['practice_evidence_assessment'].append(dict(event_id=event,passage_id=plan,stage='action',basis_kind='independent_report'))
r['practice_relation'].append(dict(id=fid+'-id',statement_id='tracer-statement',event_id=event,party_id='yeni-parti',topic_id='organ-secim-yontemi',scope_id=None,comparability_reason='Üyelerin katıldığı il ön seçimi başkan belirleme beyanının bir aşamasıdır.',target_finding_id='0105-statement',result_finding_id=None,explanation_finding_id=fid,temporal_context='Beyan 4 Ağustos, ön seçim 18 Ekim 2026 tarihlidir.',authority_context='Üyelerin ön seçimi ile kongredeki resmî seçim farklı işlemlerdir.',uncertainty_reason='Haber, sonraki kongreyi plan olarak anlatır; ön seçim tutanağı görülmedi.'))
(p/'package-afyon-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
