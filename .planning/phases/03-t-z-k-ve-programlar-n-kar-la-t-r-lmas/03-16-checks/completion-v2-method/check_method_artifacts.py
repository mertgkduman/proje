"""Check the handoff artifacts only; not a production acceptance test or audit."""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
basis = json.loads((OUT / 'source-basis.json').read_text())
risk = json.loads((OUT / 'risk-decisions.json').read_text())
release = json.loads((ROOT / 'data/current.json').read_text())['release_id']
data = json.loads((ROOT / 'data/releases' / release / 'records.json').read_text())


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


assert not basis['unresolved']
assert risk['basis_sha256'] == hashlib.sha256((OUT / 'source-basis.json').read_bytes()).hexdigest()
for source in basis['source_documents']:
    assert hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256'], source['path']
candidate_syntheses = {s['id']: s for s in data['comparison_synthesis'] if s['taxonomy_version'] == 4}
assert set(candidate_syntheses) == {s['id'] for s in basis['synthesis_obligations']}
for obligation in basis['synthesis_obligations']:
    assert obligation['source_authored_claim'] == candidate_syntheses[obligation['id']]
by_row = {r['id']: r for r in data['comparison_row'] if r['taxonomy_version'] == 4}
by_field = {f['id']: f for f in data['comparison_field']}
by_finding = {f['id']: f for f in data['finding']}
by_passage = {p['id']: p for p in data['passage']}
field_by_row = collections.defaultdict(list)
for f in by_field.values():
    field_by_row[f['row_id']].append(f)
assertions = basis['source_assertions']
for cell in basis['cells']:
    row = by_row[cell['fulfilment_locator_only']]
    for key in ('topic_id', 'party_id', 'source_role', 'version_id', 'level', 'organ'):
        assert row[key] == cell['logical_key'][key], (cell['id'], key)
    assert row['state'] == cell['disposition']
    for a_id in cell['basis_ids']:
        assertion = assertions[a_id]
        if assertion['kind'] == 'supported_field':
            matched = [f for f in field_by_row[row['id']] if all(f[k] == assertion[k] for k in
                ('field', 'condition_key', 'summary_finding_id', 'quote_finding_id'))]
            assert matched, (cell['id'], assertion['summary_finding_id'])
            assert assertion['passage_ids']
            assert all(by_passage[p]['version_id'] == row['version_id'] for p in assertion['passage_ids'])
        elif assertion['kind'] == 'dated_source_scope':
            scope = assertion['scope']
            assert all(scope.get(k) for k in ('sections', 'query_terms', 'reviewed_at', 'reason'))
            assert scope['id'] == row['scope_id'] and scope['version_id'] == row['version_id']
        else:
            assert assertion['missing']['id'] == row['missing_id']
            assert assertion['missing']['attempt_id'] == assertion['attempt']['id']
            assert assertion['missing']['party_id'] == row['party_id']

# Confirm the real section obligations, not merely their count.
actual_inventory = []
for raw in data['comparison_source_inventory']:
    if raw['taxonomy_version'] != 4:
        continue
    val = {k: raw[k] for k in basis['inventory_sections'][0]}
    for key in ('topic_ids', 'unmatched_headings'):
        if isinstance(val[key], str):
            val[key] = json.loads(val[key])
    val['full_text_available'] = bool(val['full_text_available'])
    actual_inventory.append(canonical(val))
assert collections.Counter(actual_inventory) == collections.Counter(canonical(v) for v in basis['inventory_sections'])

decisions = {d['id']: d for d in risk['decisions']}
for decision in decisions.values():
    if decision['kind'] == 'field_support':
        field = by_field[decision['field_id']]
        assert field['row_id'] == decision['row_id']
        assert all(field[k] == decision[k] for k in
            ('field', 'condition_key', 'summary_finding_id', 'quote_finding_id'))
        for kind in ('summary', 'quote'):
            expected = {e['passage_id'] for e in data['finding_evidence']
                        if e['finding_id'] == decision[kind + '_finding_id']}
            assert set(decision[kind + '_passage_ids']) <= expected, decision['id']
            assert all(by_passage[p]['version_id'] == decision['version_id'] for p in decision[kind + '_passage_ids'])
        if decision.get('original_path'):
            assert hashlib.sha256((ROOT / decision['original_path']).read_bytes()).hexdigest() == decision['source_sha256']
    elif decision['kind'] == 'synthesis_support':
        reviews = [r for r in data['comparison_semantic_review'] if r['subject_kind'] == 'comparison_synthesis'
                   and r['subject_id'] == decision['synthesis_id'] and r['reviewer_kind'] == 'agent']
        assert len(reviews) == 1
        typed = json.loads(reviews[0]['reason'])
        assert typed['claim_type'] == decision['claim_type'] and typed['sides'] == decision['sides']
    elif decision['kind'] == 'change_support':
        change = next(c for c in data['comparison_change'] if c['id'] == decision['change_id'])
        assert all(change[k] == decision[k] for k in ('row_id', 'before_passage_id', 'after_passage_id', 'order_basis'))
        assert by_passage[change['before_passage_id']]['version_id'] != by_passage[change['after_passage_id']]['version_id']
    assert decision.get('judgment') and decision.get('reviewer_kind') == 'agent'


def missing_risks(available):
    return [r['id'] for r in risk['expected_risk_universe']
            if not set(r['witness_decision_ids']).intersection(available)]


assert not missing_risks(decisions)
stripped = {k: v for k, v in decisions.items() if v['kind'] not in ('field_support', 'synthesis_support')}
stripped_missing = missing_risks(stripped)
assert all('field:' + f in stripped_missing for f in ('principle', 'target', 'instrument', 'charter_answer'))
assert all('synthesis:' + f in stripped_missing for f in ('multi_positive', 'one_positive', 'status_only'))

# This is a source-obligation demonstration, separate from the production REDs.
tip_id = '04-03-v3-0304-tip-charter-scope-aday-tanitim-html-row'
tip_cell = next(c for c in basis['cells'] if c['fulfilment_locator_only'] == tip_id)
coordinated_rows = set(by_row) - {tip_id}
missing_cell_ids = [c['id'] for c in basis['cells'] if c['fulfilment_locator_only'] not in coordinated_rows]
assert missing_cell_ids == [tip_cell['id']]

examples = {
    'artifact_version': 1,
    'tip_independent_dated_scope': dict(tip_cell, assertions=[assertions[a] for a in tip_cell['basis_ids']]),
    'programme_principle': decisions['SR25:field:tip-kapitalizm-principle'],
    'programme_conditioned_instrument': next(d for d in decisions.values() if d['group_id'] == 'SR13'
        and d.get('party_id') == 'saadet' and d['kind'] == 'field_support'),
    'programme_target': next(d for d in decisions.values() if d['group_id'] == 'SR16'
        and d.get('field') == 'target'),
    'synthesis_one_positive': next(d for d in decisions.values() if d['kind'] == 'synthesis_support'
        and d['group_id'] == 'SR10' and d['claim_type'] == 'one_positive'),
    'synthesis_multi_positive': next(d for d in decisions.values() if d['kind'] == 'synthesis_support'
        and d['group_id'] == 'SR13' and d['claim_type'] == 'multi_positive'),
    'synthesis_status_only': next(d for d in decisions.values() if d['kind'] == 'synthesis_support'
        and d['claim_type'] == 'status_only'),
    'physical_copy_gap': decisions['SR22:physical-page-gap'],
}
(OUT / 'decision-examples.json').write_text(json.dumps(examples, ensure_ascii=False, indent=2) + '\n')
result = {'artifact_version': 1, 'candidate_release_read_only': release,
    'source_expectations_constructed_without_candidate': True,
    'source_origins_unresolved': 0, 'all_expected_source_fields_matched': True,
    'all_original_inventory_sections_matched': True, 'risk_witness_links_matched': True,
    'all_source_authored_synthesis_obligations_matched': True,
    'coordinated_tip_candidate_deletion_missing_cells': missing_cell_ids,
    'stripped_field_synthesis_review_uncovered_risks': stripped_missing,
    'production_validator_status': 'not_implemented_by_this_task',
    'production_tests_audits_publish': 'not_run', 'human_acceptance': False}
(OUT / 'method-check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
