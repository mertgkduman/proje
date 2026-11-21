import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
r=json.loads((p/'aydin-review-draft-v2.json').read_text())
event='0404-afyon-onsecim-event';rel='0404-afyon-onsecim-iliski-id';speech='0105-speech-p';ref='0404-afyon-onsecim-sehir-p';plan='0404-afyon-kongre-plan-p'
versions={speech:'0105-speech-v1',ref:'0404-afyon-onsecim-sehir-v1',plan:'0404-afyon-onsecim-sehir-v1'}
sections={speech:'4 Ağustos il başkanı belirleme beyanı',ref:'19 Ekim ön seçim sonucu haberi',plan:'19 Ekim haberinde planlanan 25 Ekim kongresi'}
items=[('practice_event_evidence',event+'|'+ref+'|action',[ref]),('practice_event_evidence',event+'|'+plan+'|action',[plan]),('practice_event',event,[ref,plan]),('practice_relation',rel,[speech,ref,plan]),('practice_relation.target_finding_id',rel,[speech]),('practice_relation.explanation_finding_id',rel,[speech,ref,plan])]
for kind,identity,refs in items:
    claim=({'0404-afyon-onsecim-sehir-p':'Yerel haber Erhan’ın ön seçimde birinci olduğunu aktarıyor.','0404-afyon-kongre-plan-p':'Aynı haber sonraki kongreyi beklenti olarak bildiriyor.'}[refs[0]] if kind=='practice_event_evidence' else {'practice_event':'Afyon ön seçimi ve daha sonraki kongre beklentisi ayrı aktarılıyor.','practice_relation':'Üyelerin rolüne ilişkin beyan ile Afyon ön seçim haberi ilişkilidir.','practice_relation.target_finding_id':'Hedef üyelerin başkan belirlemesine ilişkin beyandır.','practice_relation.explanation_finding_id':'Afyon açıklaması gerçekleşen ön seçimi planlanan kongreden ayırır.'}[kind])
    r['practice_source_review'].append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at='2026-11-21T22:15:17+00:00',source_version_ids=json.dumps(list(dict.fromkeys(versions[x] for x in refs)),ensure_ascii=False),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps([sections[x] for x in refs],ensure_ascii=False),supported_claim=claim,limitations='Kongre haberde gelecek zamandadır; tutanak görülmedi.',result='reviewed',reason='İl ön seçimi ile sonraki kongre aşaması ayırt edildi.'))
r['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in r['practice_source_review']]
(p/'afyon-review-draft-v2.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
