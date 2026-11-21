import json
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
r = json.loads((p/'accessibility-review-draft.json').read_text())
speech='0105-speech-p'
versions={speech:'0105-speech-v1','0404-aydin-sonuc-p':'0404-aydin-sonuc-v1','0404-aydin-onsecim-ihbar-p':'0404-aydin-onsecim-ihbar-v1','0404-aydin-kongre-bulten-p':'0404-aydin-kongre-bulten-v1','0404-aydin-kongre-gunaydin-p':'0404-aydin-kongre-gunaydin-v1'}
sections={speech:'4 Ağustos il başkanı seçimi beyanı','0404-aydin-sonuc-p':'18 Ekim ön seçim haberi, 22 Ekim güncellemesi','0404-aydin-onsecim-ihbar-p':'19 Ekim ön seçim haberindeki sayı','0404-aydin-kongre-bulten-p':'26 Ekim il kongresi haberindeki seçim bildirimi','0404-aydin-kongre-gunaydin-p':'26 Ekim kongrede beklenen oy verme bitiş saati'}
for kind, refs in [('onsecim',['0404-aydin-sonuc-p','0404-aydin-onsecim-ihbar-p']),('kongre',['0404-aydin-kongre-bulten-p','0404-aydin-kongre-gunaydin-p'])]:
    ev='0404-aydin-'+kind+'-event'; rel='0404-aydin-'+kind+'-iliski-id'
    items=[('practice_event_evidence',ev+'|'+x+'|action',[x]) for x in refs]
    items += [('practice_event',ev,refs),('practice_relation',rel,[speech]+refs),('practice_relation.target_finding_id',rel,[speech]),('practice_relation.explanation_finding_id',rel,[speech]+refs)]
    for subject, ident, passages in items:
        r['practice_source_review'].append(dict(subject_kind=subject,subject_id=ident,reviewer_kind='agent',reviewed_at='2026-11-21T22:04:32+00:00',source_version_ids=json.dumps([versions[x] for x in passages],ensure_ascii=False),passage_ids=json.dumps(passages,ensure_ascii=False),inspected_sections=json.dumps([sections[x] for x in passages],ensure_ascii=False),supported_claim='Beyan ve Aydın yerel basınında ilgili aşamaya dair bildirim kaynak pasajlarında okundu.',limitations='Ön seçim sayıları farklı; kongre sonuç haberinin zamanlaması ve tutanak ayrıca araştırılıyor.',result='reviewed',reason='Ön seçim ile kongreyi ayırarak yayınları ve açıklamayı karşılaştırdım.'))
r['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in r['practice_source_review']]
(p/'aydin-review-draft.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
