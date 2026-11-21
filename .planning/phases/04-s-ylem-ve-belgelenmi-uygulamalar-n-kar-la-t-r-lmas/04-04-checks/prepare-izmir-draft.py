import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');pkg=json.loads((p/'package-bursa-sakarya-draft.json').read_text());extra=json.loads((p/'october-referral-records-draft.json').read_text())['entries'];ids=('0404-izmir-onsecim','0404-izmir-kongre-tire','0404-izmir-kongre-anka')
pkg['entries'] += [e for e in extra if any(str(e['values'].get(k,'')).startswith(i) for k in ('id','version_id','document_id') for i in ids)]
e=pkg['entries'];r=pkg['practice_records'];speech='0105-speech-p';now='2026-11-21T21:15:33+00:00'
items=[
 ('onsecim','2026-10-18','0404-izmir-onsecim-p','İzmir il başkanlığı ön seçimi','Sözcü 18 Ekim İzmir ön seçiminde Çağatay Güçün kesin olmayan sonuçlara göre ilk sırada olduğunu aktardı.','Üyelerin il başkanı ön seçimine ilişkin kesin olmayan sonuç','Bu haber ön seçime ilişkindir; kongre sonucu veya sandık tutanakları değildir.'),
 ('kongre','2026-10-25','0404-izmir-kongre-tire-p','İzmir il kongresi','Haber Tire 25 Ekim il kongresinde Çağatay Güçün il başkanı seçildiğini aktardı; bu oylama bir hafta önceki üye ön seçiminden ayrıdır.','25 Ekim il kongresindeki il başkanlığı seçimi','İl kongresindeki oylama üye ön seçimi değildir; özgün kongre tutanağı görülmedi.'),
]
for slug,date,ref,title,body,point,limit in items:
 ev='0404-izmir-'+slug+'-event';fid='0404-izmir-'+slug+'-iliski'; text='Başkanların üyelerce belirlenmesine ilişkin 4 Ağustos beyanının ardından '+body
 e.append(dict(kind='finding',values=dict(id=fid,party_id='yeni-parti',heading='Söylem ve uygulama',pair_id=fid,text=text,provenance='summary',epistemic_type='claim')))
 for x in (speech,ref):
  e.append(dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=x,role='support')))
  e.append(dict(kind='verification',values=dict(finding_id=fid,passage_id=x,checked_at=now,result='confirmed',reason='4 Ağustos beyanı ve İzmirde ilgili aşamaya dair haber okundu; ön seçim ve kongre birbirinden ayrıldı.')))
 e.append(dict(kind='review',values=dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Kaynaklardaki beyan ve İzmir olayının kendi aşaması karşılaştırıldı.')))
 r['practice_event'].append(dict(id=ev,common_event_key='yeni-parti-izmir-2026-'+slug,event_at=date,date_precision='day',date_unknown_reason=None,scope_context=title,title=title,occurrence_basis='İlgili tarihteki İzmir olayı haberleştirildi.'))
 r['practice_event_evidence'].append(dict(event_id=ev,passage_id=ref,supported_point=point,stage='action',concrete_basis='Tarihli haber olayın ilgili aşamasını aktarıyor.',limitation=limit,epistemic_type='claim'))
 r['practice_evidence_assessment'].append(dict(event_id=ev,passage_id=ref,stage='action',basis_kind='independent_report'))
 r['practice_relation'].append(dict(id=fid+'-id',statement_id='tracer-statement',event_id=ev,party_id='yeni-parti',topic_id='organ-secim-yontemi',scope_id=None,comparability_reason='İl başkanının belirlenmesi sürecinin ilgili aşaması, üyelerin seçime katılımı beyanı bağlamında ayrı gösterilir.',target_finding_id='0105-statement',result_finding_id=None,explanation_finding_id=fid,temporal_context='Beyan 4 Ağustos, ilgili olay '+date+' tarihindedir.',authority_context='Üye ön seçimi ile delegelerin il kongresindeki oylaması ayrı işlemlerdir.',uncertainty_reason=limit))
(p/'package-izmir-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n');print('IZMIR_DRAFT pending checks')
