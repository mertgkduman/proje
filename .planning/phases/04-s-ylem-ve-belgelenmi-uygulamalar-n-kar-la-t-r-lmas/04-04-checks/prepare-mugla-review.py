"""Record what was actually checked for the Muğla reports."""
import json
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
r = json.loads((p / 'gaziantep-review-draft.json').read_text())
a, b, speech = '0404-mugla-onsecim-p', '0404-mugla-itiraz-p', '0105-speech-p'
event = '0404-mugla-onsecim-itiraz'
items = [
    ('practice_event_evidence', event+'|'+a+'|initiative', [a], 'İki ilçede ön seçim itirazı ve başka üye yerine oy iddiaları haberleştiriliyor.'),
    ('practice_event_evidence', event+'|'+b+'|initiative', [b], 'Genel merkezin Girgin itirazını reddettiği haberleştiriliyor.'),
    ('practice_event', event, [a,b], '18 ve 21 Ekim haberleri itiraz ve yanıtı aktarıyor.'),
    ('practice_relation', '0404-mugla-relation-id', [speech,a,b], 'Beyan örgüt başkanlarının üyelerce seçimini; haberler Muğla il ön seçimi itirazını ilgilendiriyor.'),
    ('practice_relation.target_finding_id', '0404-mugla-relation-id', [speech], 'Hedef bulgu başkanların üyelerce seçilmesi beyanını aktarıyor.'),
    ('practice_relation.explanation_finding_id', '0404-mugla-relation-id', [speech,a,b], 'İlişki özeti ön seçim itirazını ve yanıt haberini ayrı tutuyor.'),
    ('practice_dispute', '0404-mugla-dispute-id', [a,b], 'İtiraz iddiaları ve genel merkez yanıtı haber olarak aktarıldı.'),
    ('practice_dispute.summary_finding_id', '0404-mugla-dispute-id', [a,b], 'İhtilaf özeti iddiaları ve ret haberini kaynaklarına bağlıyor.'),
    ('practice_dispute_evidence', '0404-mugla-dispute-id|'+a+'|İtiraz ve oy kullanma iddiaları|support', [a], 'Marmaris Haber iki ilçe sonucuna itirazı aktarıyor.'),
    ('practice_dispute_evidence', '0404-mugla-dispute-id|'+b+'|Genel merkezin ret yanıtı|conflict', [b], 'Muğla Gazetesi genel merkezin itirazı reddettiğini aktarıyor.')
]
versions = {a:'0404-mugla-onsecim-v1', b:'0404-mugla-itiraz-v1', speech:'0105-speech-v1'}
sections = {a:'Marmaris Haber, 18 Ekim, Fethiye ve Menteşe itirazları', b:'Muğla Gazetesi, 21 Ekim, genel merkez yanıtı haberi', speech:'Euronews, 4 Ağustos, başkanların doğrudan seçimi beyanı'}
for kind, identity, passages, claim in items:
    r['practice_source_review'].append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent', reviewed_at='2026-11-21T19:10:05+00:00', source_version_ids=json.dumps(list(dict.fromkeys(versions[x] for x in passages)), ensure_ascii=False), passage_ids=json.dumps(passages, ensure_ascii=False), inspected_sections=json.dumps([sections[x] for x in passages], ensure_ascii=False), supported_claim=claim, limitations='İtiraz dilekçesi, parti kararı ve seçim tutanaklarının asılları görülmedi; rakamlar kaynaklar arasında farklı.', result='reviewed', reason='Belirtilen haber ve ilgili beyanın yerel metni okundu; kaynak atfı ve olay aşaması kontrol edildi.'))
r['source_review_refs'] = [dict(subject_kind=x['subject_kind'], subject_id=x['subject_id']) for x in r['practice_source_review']]
(p / 'mugla-review-draft.json').write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n')
print('MUGLA_REVIEW_DRAFT', len(r['practice_source_review']))
