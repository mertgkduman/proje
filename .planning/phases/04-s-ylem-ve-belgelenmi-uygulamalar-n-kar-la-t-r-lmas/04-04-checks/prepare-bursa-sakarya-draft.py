import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks'); pkg=json.loads((p/'package-national-locals-draft.json').read_text()); extra=json.loads((p/'october-referral-records-draft.json').read_text())['entries']; ids=('0404-bursa-onsecim','0404-sakarya-onsecim','0404-sakarya-ozkoc')
pkg['entries'] += [e for e in extra if any(str(e['values'].get(k,'')).startswith(i) for k in ('id','version_id','document_id') for i in ids)]
e=pkg['entries'];r=pkg['practice_records'];now='2026-11-21T21:07:17+00:00'; speech='0105-speech-p'
items=[
 ('bursa','Bursa','0404-bursa-onsecim-p','Başka Gazete 18 Ekim Bursa il başkanlığı ön seçiminde 17 ilçede sandık kurulduğunu ve iki adayın yarıştığını aktarıyor.','Bursa ön seçimi haberinde belirtilen yerel oylama'),
 ('sakarya','Sakarya','0404-sakarya-onsecim-p','Haberlisin 18 Ekim Sakarya il başkanlığı ön seçiminin tamamlandığını bildiriyor; haber sonraki il kongresini ayrı bir aşama olarak belirtiyor.','Sakarya ön seçiminin tamamlandığı haber kaydı'),
]
for slug,city,ref,body,point in items:
 ev='0404-'+slug+'-onsecim-event'; fid='0404-'+slug+'-iliski'; text='Başkanların üyelerce belirlenmesine ilişkin 4 Ağustos beyanından sonra '+body
 e.append(dict(kind='finding',values=dict(id=fid,party_id='yeni-parti',heading='Söylem ve uygulama',pair_id=fid,text=text,provenance='summary',epistemic_type='claim')))
 for passage in (speech,ref):
  e.append(dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=passage,role='support')))
  e.append(dict(kind='verification',values=dict(finding_id=fid,passage_id=passage,checked_at=now,result='confirmed',reason='4 Ağustos beyanı ile yerel ön seçim haberi okundu; kongre aşaması ve sandık tutanakları ayrı tutuldu.')))
 e.append(dict(kind='review',values=dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Beyan ve yerel ön seçim haberi karşılaştırıldı; sonuç kaynak sınırlarıyla aktarıldı.')))
 r['practice_event'].append(dict(id=ev,common_event_key='yeni-parti-'+slug+'-2026-il-on-secim',event_at='2026-10-18',date_precision='day',date_unknown_reason=None,scope_context=city+' il başkanlığı ön seçimi',title=city+' il başkanlığı ön seçimi',occurrence_basis='18 Ekim tarihli yerel haber il başkanlığı ön seçimini aktarıyor.'))
 r['practice_event_evidence'].append(dict(event_id=ev,passage_id=ref,supported_point=point,stage='action',concrete_basis='Yerel haber il ön seçimine ilişkin gözlem ve açıklamaları aktarıyor.',limitation='Sandık tutanakları görülmedi; sonraki il kongresi ve haberlerdeki sayısal ayrıntılar ayrıca inceleniyor.',epistemic_type='claim'))
 r['practice_evidence_assessment'].append(dict(event_id=ev,passage_id=ref,stage='action',basis_kind='independent_report'))
 r['practice_relation'].append(dict(id=fid+'-id',statement_id='tracer-statement',event_id=ev,party_id='yeni-parti',topic_id='organ-secim-yontemi',scope_id=None,comparability_reason='Beyan il başkanlarının üyelerce belirlenmesini kapsar; yerel haber il başkanlığı ön seçimini bildirir.',target_finding_id='0105-statement',result_finding_id=None,explanation_finding_id=fid,temporal_context='Beyan 4 Ağustos, yerel ön seçim 18 Ekim 2026 tarihlidir.',authority_context='Üye ön seçimi ile sonraki il kongresi ayrı işlemlerdir.',uncertainty_reason='Sandık tutanakları ve ön seçim sonrasındaki tüm işlemler bu kaynaklardan doğrulanmadı.'))
(p/'package-bursa-sakarya-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n');print('BURSA_SAKARYA_DRAFT pending checks')
