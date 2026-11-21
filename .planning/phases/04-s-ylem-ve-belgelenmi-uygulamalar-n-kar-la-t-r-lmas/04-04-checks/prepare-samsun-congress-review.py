import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
r=json.loads((p/'afyon-review-draft-v2.json').read_text());ev='0404-samsun-kongre-event';rel='0404-samsun-kongre-iliski-id';speech='0105-speech-p';ref='0404-samsun-kongre-objektif-p';versions={speech:'0105-speech-v1',ref:'0404-samsun-kongre-objektif-v1'};sections={speech:'4 Ağustos il başkanı seçimi beyanı',ref:'25 Ekim Samsun il kongresi sonuç haberi'}
items=[('practice_event_evidence',ev+'|'+ref+'|action',[ref]),('practice_event',ev,[ref]),('practice_relation',rel,[speech,ref]),('practice_relation.target_finding_id',rel,[speech]),('practice_relation.explanation_finding_id',rel,[speech,ref])]
for kind,identity,refs in items:
    claim={'practice_event_evidence':'Haberde Özdağ’ın 276 oyla kongrede seçildiği aktarılıyor.','practice_event':'Yerel haber 25 Ekim Samsun kongre sonucunu bildiriyor.','practice_relation':'Üyelerin başkan belirleme beyanı ile sonraki kongre aşaması karşılaştırılıyor.','practice_relation.target_finding_id':'Samsun karşılaştırmasının hedefi üye iradesine dair beyandır.','practice_relation.explanation_finding_id':'Açıklama kongre sonucunu ön seçimden ayrı ele alıyor.'}[kind]
    r['practice_source_review'].append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at='2026-11-21T22:25:03+00:00',source_version_ids=json.dumps([versions[x] for x in refs],ensure_ascii=False),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps([sections[x] for x in refs],ensure_ascii=False),supported_claim=claim,limitations='Kongre tutanağı görülmedi; ön seçim itirazları ayrı konudur.',result='reviewed',reason='Beyan ile kongre haberi karşılaştırıldı.'))
r['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in r['practice_source_review']]
(p/'samsun-congress-review-draft-v2.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
