"""Cross-link the genuine prior risk reading; add only the separately read SR25.

Expected risk classes below are authored from the phase decisions and SOURCE
corpus. They do not disappear if a submitted review deletes its sample.
"""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
PHASE = ROOT / '.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas'
PRE = PHASE / '03-16-precheck'
source = json.loads((PRE / 'source-second-reading.json').read_text())
basis = json.loads((OUT / 'source-basis.json').read_text())
cell_by_row = {c['fulfilment_locator_only']: c for c in basis['cells']}
assertions = basis['source_assertions']
decisions = []
groups = []
for check in source['checks']:
    ids = []
    for row in check['selected_rows']:
        cell = cell_by_row[row['id']]
        if not row['fields']:
            ident = check['id'] + ':scope:' + row['id']
            decisions.append({'id': ident, 'group_id': check['id'], 'kind': 'scope_or_document_gap',
                'cell_id': cell['id'], 'row_id': row['id'], 'scope_id': row['scope_id'],
                'missing_id': row['missing_id'], 'basis_ids': cell['basis_ids'],
                'party_id': row['party_id'], 'version_id': row['version_id'], 'source_role': row['source_role'],
                'decision': check['result'], 'judgment': check['judgment'], 'source_reading': check['source_reading'],
                'recorded_at': check['recorded_at'], 'reviewer_kind': 'agent', 'reading_origin': 'inherited_actual_second_reading'})
            ids.append(ident)
        for change in row.get('changes', []):
            ident = check['id'] + ':change:' + change['id']
            decisions.append({'id': ident, 'group_id': check['id'], 'kind': 'change_support',
                'row_id': row['id'], 'cell_id': cell['id'], 'change_id': change['id'],
                'before_passage_id': change['before_passage_id'], 'after_passage_id': change['after_passage_id'],
                'order_basis': change['order_basis'], 'judgment': check['judgment'],
                'source_reading': check['source_reading'], 'recorded_at': check['recorded_at'],
                'reviewer_kind': 'agent', 'reading_origin': 'inherited_actual_second_reading'})
            ids.append(ident)
        for field in row['fields']:
            found = [a for a in cell['basis_ids'] if assertions[a]['kind'] == 'supported_field'
                     and (assertions[a]['summary_finding_id'], assertions[a]['quote_finding_id']) ==
                         (field['summary_finding_id'], field['quote_finding_id'])]
            if not found:
                raise ValueError('Inspected field not traceable to original source judgment: ' + field['id'])
            ident = check['id'] + ':field:' + field['id']
            decisions.append({'id': ident, 'group_id': check['id'], 'kind': 'field_support',
                'cell_id': cell['id'], 'basis_ids': found, 'row_id': row['id'], 'field_id': field['id'],
                'party_id': row['party_id'], 'version_id': row['version_id'], 'source_role': row['source_role'],
                'field': field['field'], 'condition_key': field['condition_key'],
                'summary_finding_id': field['summary_finding_id'], 'quote_finding_id': field['quote_finding_id'],
                'summary_passage_ids': field['summary_passage_ids'], 'quote_passage_ids': field['quote_passage_ids'],
                'decision': check['result'], 'judgment': check['judgment'], 'source_reading': check['source_reading'],
                'recorded_at': check['recorded_at'], 'reviewer_kind': 'agent',
                'reading_origin': 'inherited_actual_second_reading', 'original_field_review': field['review_provenance']})
            ids.append(ident)
    for synthesis in check['inspected_synthesis']:
        ident = check['id'] + ':synthesis:' + synthesis['id']
        decisions.append({'id': ident, 'group_id': check['id'], 'kind': 'synthesis_support',
            'synthesis_id': synthesis['id'], 'topic_id': synthesis['topic_id'],
            'claim_type': synthesis['typed_proof']['claim_type'], 'sides': synthesis['typed_proof']['sides'],
            'explanation': synthesis['typed_proof']['explanation'],
            'judgment': check['judgment'], 'source_reading': check['source_reading'],
            'recorded_at': check['recorded_at'], 'reviewer_kind': 'agent',
            'reading_origin': 'inherited_actual_second_reading',
            'original_semantic_review': synthesis['original_semantic_review']})
        ids.append(ident)
    if check['id'] == 'SR22':
        ident = 'SR22:physical-page-gap'
        decisions.append({'id': ident, 'group_id': 'SR22', 'kind': 'physical_page_gap',
            'missing_id': '0314-dyp-1985-income-pages-missing', 'attempt_id': '0314-dyp-1985-income-page-check',
            'version_id': '0210-demokrat-old1985-v1', 'pdf_page_indexes': [102, 103],
            'printed_pages_observed': ['98', '101'], 'unavailable_printed_pages': ['99', '100'],
            'judgment': check['judgment'], 'source_reading': check['source_reading'],
            'recorded_at': check['recorded_at'], 'reviewer_kind': 'agent',
            'reading_origin': 'inherited_actual_second_reading'})
        ids.append(ident)
    groups.append({'id': check['id'], 'title': check['title'], 'decision_ids': ids,
                   'expansion': check['expansion'], 'source_pointer': '/checks/' + str(source['checks'].index(check))})

# This narrowly bounded original-HTML reading was performed in this method task.
# It fills a genuine omitted risk class; it neither rewrites source content nor
# pretends that the previous 24 checks inspected a principle field.
cell = cell_by_row['04-03-v3-0304-tip-program-kapitalizm-row']
principle_basis = next(b for b in cell['basis_ids'] if assertions[b].get('field') == 'principle')
decisions.append({'id': 'SR25:field:tip-kapitalizm-principle', 'group_id': 'SR25',
    'kind': 'field_support', 'cell_id': cell['id'], 'basis_ids': [principle_basis],
    'row_id': cell['fulfilment_locator_only'], 'field_id': '04-03-v3-0304-tip-program-kapitalizm-field',
    'party_id': 'tip', 'version_id': '0203-tip-program-v1', 'source_role': 'program',
    'field': 'principle', 'condition_key': None,
    'summary_finding_id': '0304-tip-program-kapitalizm-summary',
    'quote_finding_id': '0304-tip-program-kapitalizm-quote',
    'summary_passage_ids': ['0304-tip-program-kapitalizm-p1', '0304-tip-program-kapitalizm-p2', '0304-tip-program-kapitalizm-q'],
    'quote_passage_ids': ['0304-tip-program-kapitalizm-q'],
    'decision': 'supported_with_stated_scope', 'reviewer_kind': 'agent',
    'recorded_at': '2026-11-15T16:52:28Z', 'reading_origin': 'new_bounded_original_html_reading',
    'source_reading': 'Original HTML heading KAPİTALİZM BÜTÜNSEL BİR BUNALIM İÇİNDE; preceding paragraph and first three complete following paragraphs read, rather than quote-only verification.',
    'judgment': 'İki tam paragraf kapitalizmin bunalımını ekonomik, siyasal, ideolojik, toplumsal ve ekolojik boyutlarıyla anlatır ve kendiliğinden yıkılış sonucunu açıkça reddeder. Özet her iki unsuru korur. Bu programatik çözümleme ilke alanında kaynaklı aktarılabilir; bu bağlam tek başına ölçülebilir bir hedef veya idari uygulama aracı belirtmez. Sosyalist iktidar mücadelesi ifadesinden yeni tutar, kurum veya uygulama takvimi üretilmez.',
    'original_path': 'data/objects/6aa8a0087e2426e808defbc8e427281f08862b1206fdad2ae847fd294854c7e0/original.html.bin',
    'source_sha256': '6aa8a0087e2426e808defbc8e427281f08862b1206fdad2ae847fd294854c7e0',
    'limit': 'One source-context principle decision, not a new whole-programme review or a claim that all targets/instruments are absent.'})
groups.append({'id': 'SR25', 'title': 'TİP programı: ilke/çözümleme ile somut araç ayrımı',
               'decision_ids': ['SR25:field:tip-kapitalizm-principle'],
               'expansion': 'Both support paragraphs and their immediate source context read; no defect found.'})
for i, fact in enumerate(source['same_hash_copy_facts'], 1):
    decisions.append({'id': f'COPY0{i}:same-content', 'group_id': f'COPY0{i}',
        'kind': 'same_hash_copy', 'versions': fact['versions'],
        'reading_origin': 'inherited_recorded_copy_fact',
        'recorded_at': source['actual_reading_time']['packaged_at'], 'reviewer_kind': 'agent',
        'judgment': 'Farklı URL aynı özgün baytları taşır; yeni içerik, maddi değişiklik, kabul sırası veya hukuki yürürlük kanıtı değildir.'})

# Explicit applicability decisions from D-01..D-16 and the original corpus.
# "rule" is the executor's independently reproducible applicability selector.
risks = []
def risk(ident, rule, groups_, rationale):
    applicable = [d['id'] for d in decisions if d['group_id'] in groups_]
    if not applicable:
        raise ValueError('Risk has no substantive witness: ' + ident)
    risks.append({'id': ident, 'applicability_rule': rule, 'required': True,
                  'witness_decision_ids': applicable, 'selection_rationale': rationale})

party_groups = {'yeni-parti': ['SR01'], 'tip': ['SR02', 'SR25'], 'dem': ['SR03', 'SR18'],
    'iyi': ['SR04', 'SR05'], 'yeni-yol': ['SR24'], 'dbp': ['SR09', 'SR15'],
    'emep': ['SR16', 'SR17'], 'saadet': ['SR10', 'SR13'], 'demokrat': ['SR06', 'SR07', 'SR21']}
for party, group in party_groups.items():
    risk('party:' + party, {'source_universe_party': party}, group,
         'Each scoped party requires its own source-linked meaning or documentary-gap decision; documentary gaps do not manufacture fields.')
for label, group in {'charter': ['SR01', 'SR08'], 'program': ['SR13', 'SR25'],
                     'supplement': ['SR17', 'SR18'], 'historical': ['SR09', 'SR15', 'SR23']}.items():
    risk('role:' + label, {'source_cell_role_exists': label}, group,
         'Different document roles can change the interpretation even when wording is similar; source role is verified through version and attribution.')
for label, group in {'html': ['SR01', 'SR09', 'SR25'], 'pdf': ['SR02', 'SR07', 'SR17', 'SR21']}.items():
    risk('format:' + label, {'source_original_format_exists': label}, group,
         'Original HTML text and PDF page/printed-page conventions need different checks; MIME is checked against document_version.')
for label, group in {'charter_answer': ['SR01', 'SR07'], 'principle': ['SR25'],
                     'target': ['SR16', 'SR21'], 'instrument': ['SR13', 'SR18']}.items():
    risk('field:' + label, {'source_supported_field_exists': label}, group,
         'A supported field family needs an actual inspected field/finding/passage chain; a party-only row witness cannot satisfy it.')
for label, group in {'centre': ['SR01', 'SR02'], 'province': ['SR07'],
                     'district': ['SR05', 'SR07'], 'other_organ': ['SR06', 'SR10', 'SR11'],
                     'party_membership': ['SR01', 'SR05', 'SR09'],
                     'national_local_policy': ['SR18', 'SR23']}.items():
    risk('tier:' + label, {'source_research_tier_class': label}, group,
         'Use the explicit source jurisdiction and organ described by the cited judgment; broad applicable_levels prose is not a Cartesian product of all tiers.')
for label, group in {'congress': ['SR07', 'SR08'], 'executive': ['SR01', 'SR02'],
                     'discipline_appeal': ['SR03', 'SR09'], 'audit': ['SR08'],
                     'auxiliary_consultative': ['SR06', 'SR10', 'SR11']}.items():
    risk('organ:' + label, {'source_research_organ_class': label}, group,
         'Organ classes are kept distinct; financial congress commissions, organisational audit boards and disciplinary appeals cannot witness one another.')
special = [
 ('rights_limits_appeals', ['SR03', 'SR09'], 'D-01/D-03 rights, safeguards, discipline and appeal are present in the source research.'),
 ('conditional_scope', ['SR05', 'SR13', 'SR18', 'SR21'], 'D-07/D-08 conditional clauses and denominators occur in the authored source judgments.'),
 ('multiple_evidence', ['SR18', 'SR21', 'SR25'], 'Source assertion has multiple supporting passages, including wider context; every support link is preserved.'),
 ('uncertain_alternatives', ['SR02', 'SR03', 'SR09', 'SR16'], 'D-15 distinct same-party versions with unestablished order/adoption exist.'),
 ('before_after', ['SR04', 'SR05'], 'D-14 İYİ Madde48 has genuine distinct old/new source passages; a date or hash alone is insufficient.'),
 ('historical_identity', ['SR15', 'SR23'], 'D-13/D-16 BDP and DYP historical source identities are documented, rather than assumed current-party programmes.'),
 ('supplement_with_programme_gap', ['SR15', 'SR16', 'SR18'], 'D-16 DEM/DBP full current programme gaps coexist with positive supplemental/historical content.'),
 ('real_document_gap', ['SR24'], 'Two actual Yeni Yol searches cover the missing charter/programme without per-cell fabricated searches.'),
 ('narrow_negative_scope', ['SR10', 'SR11', 'SR14'], 'D-06 explicit bounded scopes must not become opposition or whole-document absence.'),
 ('minority_topic', ['SR10', 'SR11'], 'D-06 Saadet disability coordination and İYİ optional ethics board have whole nine-party backscan obligations.'),
 ('manual_pdf_locator', ['SR02', 'SR17'], 'Source research has manually checked image locators; original indices and corrected education locator matter.'),
 ('image_only_text', ['SR20'], 'Demokrat programme printed14 exists despite an empty PDF text layer.'),
 ('physical_page_gap', ['SR22'], 'DYP1985 printed99–100 are physically absent in this copy, not merely absent from extracted text.'),
 ('same_hash_copy', ['COPY01', 'COPY02'], 'Saadet original charter/programme copies share hashes across URLs and cannot support a before/after claim.'),
 ('proposal_body_distinction', ['SR16', 'SR17', 'SR18'], 'EMEP congress proposal/body order or adoption is not established by their coexistence.'),
 ('no_party_or_legal_status_inference', ['SR24', 'SR23'], 'Sicil identity, founding news, source content, legal force and current policy remain separate claims.'),
]
for label, group, why in special:
    risk('semantic:' + label, {'independent_source_research_condition': label}, group, why)
for label, group in {'multi_positive': ['SR08', 'SR13'], 'one_positive': ['SR10', 'SR11'],
                     'status_only': ['SR12', 'SR14']}.items():
    risk('synthesis:' + label, {'source_authored_synthesis_claim_type_exists': label}, group,
         'A real inspected synthesis of this applicable typed claim class, with every positive passage and negative scope/missing side checked, is required.')

# Tighten broad group annotations into typed witnesses. A field family must not
# be satisfied by some other field or by a synthesis that happens to share a case.
for r in risks:
    prefix, label = r['id'].split(':', 1)
    candidates = [d for d in decisions if d['id'] in r['witness_decision_ids']]
    if prefix == 'field':
        candidates = [d for d in candidates if d['kind'] == 'field_support' and d['field'] == label]
    elif prefix == 'party':
        candidates = [d for d in candidates if d.get('party_id') == label]
    elif prefix == 'role':
        candidates = [d for d in candidates if d.get('source_role') == label]
    elif prefix == 'synthesis':
        candidates = [d for d in candidates if d['kind'] == 'synthesis_support' and d['claim_type'] == label]
    elif r['id'] == 'semantic:before_after':
        candidates = [d for d in candidates if d['kind'] == 'change_support']
    if not candidates:
        raise ValueError('Risk lacks correct typed witness: ' + r['id'])
    r['witness_decision_ids'] = [d['id'] for d in candidates]
    r['witness_constraints'] = {
        'allowed_decision_kinds': sorted({d['kind'] for d in candidates}),
        'source_cell_ids': sorted({d['cell_id'] for d in candidates if d.get('cell_id')}),
        'source_assertion_ids': sorted({a for d in candidates for a in d.get('basis_ids', [])}),
        'synthesis_ids': sorted({d['synthesis_id'] for d in candidates if d.get('synthesis_id')}),
        'require_actual_typed_links': True,
        'accept_group_title_or_party_name_alone': False,
        'additional_eligible_witness_policy': 'A newly authored source-linked witness can be added in a new immutable review revision; a submitted sample cannot edit this applicable risk universe.'}

result = {'artifact_version': 1, 'completion_contract_target': 2, 'reviewer_kind': 'agent',
    'not_human_acceptance': True, 'original_reading_provenance': source['actual_reading_time'],
    'basis_sha256': hashlib.sha256((OUT / 'source-basis.json').read_bytes()).hexdigest(),
    'risk_universe_origin': 'Locked phase decisions plus original source research and typed authored claims, independent of submitted sample membership.',
    'expected_risk_universe': risks, 'groups': groups, 'decisions': decisions,
    'sampling_policy': 'Cover applicable source/meaning risk classes; do not enforce 24/25 cases, 93 fields or another fixed sample quota. Same decision may witness multiple classes only when its links actually demonstrate them.',
    'uncovered_applicable_risks': [],
    'limits': ['Existing original dates retain their meaning; no re-dating inherited judgments.',
               'SR25 is a new bounded programme-principle reading only.',
               'Field gaps need bounded source dispositions, not invented evidence or three mandatory positive fields.',
               'Structural coverage and source hashes do not mechanically prove semantic truth.']}
(OUT / 'risk-decisions.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'expected_risks': len(risks), 'groups': len(groups),
                  'decision_kinds': dict(collections.Counter(d['kind'] for d in decisions)),
                  'uncovered': []}, indent=2))
