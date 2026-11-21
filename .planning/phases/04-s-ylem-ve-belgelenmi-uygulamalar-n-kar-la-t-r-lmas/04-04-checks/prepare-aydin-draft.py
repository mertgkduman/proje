import json
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
pkg = json.loads((p/'package-accessibility-draft.json').read_text())
for file, ids in [('local-elections-records-draft.json', ('0404-aydin-sonuc',)), ('october-referral-records-draft.json', ('0404-aydin-onsecim-ihbar', '0404-aydin-kongre-bulten'))]:
    extra = json.loads((p/file).read_text())['entries']
    pkg['entries'] += [x for x in extra if any(str(x['values'].get(k, '')).startswith(i) for k in ('id','version_id','document_id') for i in ids)]
e, r = pkg['entries'], pkg['practice_records']
speech = '0105-speech-p'
now = '2026-11-21T22:04:32+00:00'
cases = [
 ('onsecim','2026-10-18','Aydın il başkanlığı ön seçimi',['0404-aydin-sonuc-p','0404-aydin-onsecim-ihbar-p'], 'İki yerel haber 18 Ekim Aydın il başkanlığı ön seçiminde Dilaver Demir’in birinci olduğunu bildiriyor. Oy sayısını bir haber 4.152, diğeri 4.094 olarak aktarıyor; farklı sayılar uzlaştırılmadı.', 'İki haber farklı ön seçim sayıları bildiriyor; sandık tutanağı görülmedi.'),
 ('kongre','2026-10-26','Aydın il kongresi',['0404-aydin-kongre-bulten-p'], 'Bülten Aydın 26 Ekim il kongresinde Dilaver Demir’in il başkanlığına seçildiğini bildirdi. Sonuç haberinin zamanlaması ayrıca araştırılıyor.', '16.33 tarihli sonuç haberi ile başka haberde beklenen 17.00 sandık kapanışı arasındaki ilişki doğrulanmadı; kongre tutanağı görülmedi.'),
]
for key, date, title, refs, text, limitation in cases:
    event='0404-aydin-'+key+'-event'; fid='0404-aydin-'+key+'-iliski'
    e.append(dict(kind='finding',values=dict(id=fid,party_id='yeni-parti',heading='Söylem ve uygulama',pair_id=fid,text=text,provenance='summary',epistemic_type='claim')))
    for ref in [speech]+refs:
        e.append(dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=ref,role='support')))
        e.append(dict(kind='verification',values=dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='Beyan ve haberlerdeki olay aşaması ile sınırlılıklar incelendi.')))
    e.append(dict(kind='review',values=dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Ön seçim ve kongre ayrı tarihlerde ele alındı; sayısal ve zamansal belirsizlikler korundu.')))
    r['practice_event'].append(dict(id=event,common_event_key='yeni-parti-aydin-2026-'+key,event_at=date,date_precision='day',date_unknown_reason=None,scope_context=title,title=title,occurrence_basis='Haber kaynağının ilgili işlem hakkındaki bildirimi.'))
    for ref in refs:
        r['practice_event_evidence'].append(dict(event_id=event,passage_id=ref,supported_point='İlgili yerel yayının seçim veya kongre anlatımı',stage='action',concrete_basis='Kaynak kendi olay anlatımını bildiriyor.',limitation=limitation,epistemic_type='claim'))
        r['practice_evidence_assessment'].append(dict(event_id=event,passage_id=ref,stage='action',basis_kind='independent_report'))
    r['practice_relation'].append(dict(id=fid+'-id',statement_id='tracer-statement',event_id=event,party_id='yeni-parti',topic_id='organ-secim-yontemi',scope_id=None,comparability_reason='İl başkanı belirlenmesinin bu aşaması, üyelerin rolüne dair beyanın bağlamında gösterilir.',target_finding_id='0105-statement',result_finding_id=None,explanation_finding_id=fid,temporal_context='4 Ağustos beyanı; 18 Ekim ön seçim ve 26 Ekim il kongresi ayrı işlemlerdir.',authority_context='Üyelerin ön seçimi ile delegelerin kongredeki oylaması farklı işlemlerdir.',uncertainty_reason=limitation))
(p/'package-aydin-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
