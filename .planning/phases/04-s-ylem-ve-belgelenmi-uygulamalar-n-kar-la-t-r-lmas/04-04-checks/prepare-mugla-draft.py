"""Build an attributed Muğla draft; source and decision documents stay distinct."""
import json
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
package = json.loads((p / 'package-gaziantep-draft.json').read_text())
source = json.loads((p / 'source-records-draft-v7.json').read_text())['entries']
new = ('0404-tuzuk-9kasim', '0404-mugla-itiraz', '0404-mugla-onsecim')
for entry in source:
    v = entry['values']
    if any(v.get(k, '').startswith(prefix) for k in ('id', 'version_id', 'document_id') for prefix in new):
        package['entries'].append(entry)

entries, records = package['entries'], package['practice_records']
event = '0404-mugla-onsecim-itiraz'
a, b = '0404-mugla-onsecim-p', '0404-mugla-itiraz-p'
findings = [
    ('0404-mugla-relation', 'Muğla il başkanlığı ön seçimi hakkında itiraz ve genel merkez yanıtı haberleştirildi; ön seçim, delegelerin resmî kongre oylamasından ayrı bir aşamadır.'),
    ('0404-mugla-dispute', 'Marmaris Haber iki ilçedeki sonuçlara itirazı ve başka üyelerin yerine oy kullanıldığı iddialarını aktardı; Muğla Gazetesi genel merkezin Girgin itirazını reddettiğini yazdı. İtiraz ve kararın asılları görülmedi.')
]
for identity, text in findings:
    entries.append(dict(kind='finding', values=dict(id=identity, party_id='yeni-parti', heading='Söylem ve uygulama', pair_id=identity, text=text, provenance='summary', epistemic_type='claim')))
    for ref in (a, b):
        entries.append(dict(kind='finding_evidence', values=dict(finding_id=identity, passage_id=ref, role='support')))
        entries.append(dict(kind='verification', values=dict(finding_id=identity, passage_id=ref, checked_at='2026-11-21T19:10:05+00:00', result='confirmed', reason='Kaynak haber okundu; itiraz ve karar belgelerinin asılları görülmedi.')))
    entries.append(dict(kind='review', values=dict(id='review-'+identity, kind='finding', subject_id=identity, reviewer_kind='agent', reviewed_at='2026-11-21T19:10:05+00:00', result='reviewed', reason='Ön seçim hakkındaki iki tarihli haber karşılaştırıldı; iddia ve cevap kaynaklarına atfedildi.')))

records['practice_event'].append(dict(id=event, common_event_key='mugla-2026-onsecim-itiraz', event_at='2026-10-21', date_precision='day', date_unknown_reason=None, scope_context='Muğla il başkanlığı ön seçim itirazı', title='Muğla ön seçim itirazına ilişkin haberler', occurrence_basis='18 ve 21 Ekim haberleri itiraz ve genel merkezce ret anlatımlarını yayımladı.'))
for ref, point, basis, limitation in [
    (a, 'İki ilçedeki sonuçlara itiraz ve başkası yerine oy kullanıldığı iddiası', '18 Ekim haberi itirazı ve iddiaları aktarıyor.', 'İtiraz dilekçesi ve oy tutanakları görülmedi.'),
    (b, 'Girgin itirazına genel merkezce ret yanıtı verildiğinin aktarılması', '21 Ekim haberi ret yanıtını ve genel merkez incelemesini aktarıyor.', 'Genel merkez yazısı ve incelendiği belirtilen tutanaklar görülmedi.')
]:
    records['practice_event_evidence'].append(dict(event_id=event, passage_id=ref, supported_point=point, stage='initiative', concrete_basis=basis, limitation=limitation, epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=event, passage_id=ref, stage='initiative', basis_kind='independent_report'))
records['practice_relation'].append(dict(id='0404-mugla-relation-id', statement_id='tracer-statement', event_id=event, party_id='yeni-parti', topic_id='organ-secim-yontemi', scope_id=None, comparability_reason='Beyan parti örgütü başkanlarının üyelerce seçimini anlatır; Muğla haberleri il başkanlığı ön seçimi ve bu sürece itirazla ilgilidir.', target_finding_id='0105-statement', result_finding_id=None, explanation_finding_id='0404-mugla-relation', temporal_context='Beyan 4 Ağustos; haberler 18 ve 21 Ekim tarihlidir.', authority_context='Üye ön seçimi ve delege kongresinin farklı aşamaları birbirine karıştırılmadı.', uncertainty_reason='İtiraz ve parti yanıtının asılları, sonuç tutanakları ve aktarılan oy sayıları doğrulanmadı.'))
records['practice_dispute'].append(dict(id='0404-mugla-dispute-id', event_id=event, supported_points='Haberler itirazı ve genel merkez yanıtını aktarıyor.', disputed_points='İki ilçede başkası yerine oy kullanıldığı iddiaları ve bunların seçim sonucuna etkisi.', unresolved_points='İtiraz dilekçesi, karar ve tutanakların asılları görülmedi; 7.574 ve 7.584 oy aktarımları farklıdır.', summary_finding_id='0404-mugla-dispute'))
records['practice_dispute_evidence'] += [dict(dispute_id='0404-mugla-dispute-id', passage_id=a, point='İtiraz ve oy kullanma iddiaları', source_position='İki ilçedeki sonuçlara itiraz edildiği haberde aktarılıyor.', role='support'), dict(dispute_id='0404-mugla-dispute-id', passage_id=b, point='Genel merkezin ret yanıtı', source_position='Haber, sonucu değiştirecek usulsüzlük tespit edilmediği yanıtını aktarıyor.', role='conflict')]
(p / 'package-mugla-draft.json').write_text(json.dumps(package, ensure_ascii=False, indent=2)+'\n')
print('MUGLA_DRAFT: sourced claims; no scope closure')
