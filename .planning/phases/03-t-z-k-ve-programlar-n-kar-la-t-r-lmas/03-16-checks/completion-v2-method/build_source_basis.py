"""Materialize inherited SOURCE judgments, never infer expectations from a candidate.

Run from the repository root. Writes only beside this file. This is a method
artifact generator, not an importer or a claim that code review is resolved.
"""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
PHASE = ROOT / '.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas'
COMP = ROOT / 'data/comparisons'
SKIP = {'03-source-review.json', '03-acceptance.json', '03-probe-record.json',
        '03-navigation-checks.json'}


def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def ref(path, pointer):
    return {'path': str(path.relative_to(ROOT)), 'pointer': pointer}


def referenced_value(reference):
    value = payloads[Path(reference['path']).name]
    for token in reference['pointer'].strip('/').split('/'):
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


payloads, documents, origins, by_kind = {}, [], {}, collections.defaultdict(dict)
multi = collections.defaultdict(list)
for path in sorted((ROOT / 'data/dossiers').glob('*.json')) + sorted(COMP.glob('*.json')):
    if path.name in SKIP:
        continue
    payload = json.loads(path.read_text())
    payloads[path.name] = payload
    documents.append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'role': 'source_research_or_mapping', 'original_status': payload.get('status')})
    entries = [('records', i, e['kind'], e['values']) for i, e in enumerate(payload.get('records', []))]
    entries += [('decisions', i, 'comparison_semantic_review', e) for i, e in enumerate(payload.get('decisions', []))]
    for group, i, kind, val in entries:
        pointer = ref(path, f'/{group}/{i}' + ('/values' if group == 'records' else ''))
        ident = val.get('id') or ((val.get('subject_kind'), val.get('subject_id'), val.get('reviewer_kind'))
                                if kind == 'comparison_semantic_review' else None)
        if ident is not None:
            by_kind[kind][ident] = val
            origins[kind, ident] = pointer
        multi[kind].append((val, pointer))

# All supplied research packages are indexed before constructing selected-taxonomy
# coverage. The release's submitted rows and completion proof are NOT read here.
source_rows = {}
rank = {'not_researched': 0, 'in_progress': 1, 'document_missing': 2,
        'no_explicit_statement': 2, 'evidence': 3}
for row, pointer in multi['comparison_row']:
    old = source_rows.get(row['id'])
    if old is None or rank[row['state']] >= rank[old['row']['state']]:
        source_rows[row['id']] = {'row': row, 'root': pointer, 'mapping': []}
fields = collections.defaultdict(list)
for field, pointer in multi['comparison_field']:
    fields[field['row_id']].append({'field': field, 'root': pointer})
for entry in source_rows.values():
    entry['fields'] = list({f['field']['id']: f for f in fields[entry['row']['id']]}.values())

errors = []
for name in ('03-taxonomy-v3.json', '03-taxonomy-v4.json'):
    payload = payloads[name]
    selected = {}
    for i, mapping in enumerate(payload['row_mappings']):
        old_id = mapping['old_row_id']
        if old_id not in source_rows:
            errors.append({'kind': 'unlocated_source_judgment', 'id': old_id})
            continue
        old = source_rows[old_id]
        row = dict(old['row'], id=mapping['new_row_id'], topic_id=mapping['topic_id'],
                   taxonomy_version=payload['taxonomy_version'])
        fs = {f['field']['id']: f for f in old['fields']}
        mapped_fields = []
        for fm in mapping['fields']:
            if fm['old_id'] not in fs:
                errors.append({'kind': 'unlocated_source_field', 'id': fm['old_id']})
                continue
            f = fs[fm['old_id']]
            mapped_fields.append(dict(f, field=dict(f['field'], id=fm['new_id'], row_id=row['id'])))
        selected[row['id']] = {'row': row, 'root': old['root'], 'fields': mapped_fields,
                              'mapping': old['mapping'] + [ref(COMP / name, f'/row_mappings/{i}')],
                              'original_judgment_id': old.get('original_judgment_id', old['row']['id'])}
    for ident, entry in source_rows.items():
        if entry['row']['taxonomy_version'] == payload['taxonomy_version']:
            selected[ident] = entry
    # The authored backfill also adds source-supported fields to inherited rows
    # without replacing the row itself. These are independent source judgments.
    for ident, entry in selected.items():
        merged = {f['field']['id']: f for f in entry['fields']}
        merged.update({f['field']['id']: f for f in fields[ident]})
        entry['fields'] = list(merged.values())
    source_rows.update(selected)
    if name.endswith('v4.json'):
        expected = selected

semantic_by_subject = collections.defaultdict(list)
for val, pointer in multi['comparison_semantic_review']:
    semantic_by_subject[val['subject_kind'], val['subject_id']].append({'record': val, 'source': pointer})
evidence = collections.defaultdict(set)
for e, _ in multi['finding_evidence']:
    evidence[e['finding_id']].add(e['passage_id'])
review_by_finding = collections.defaultdict(list)
for r, pointer in multi['review']:
    if r.get('kind') == 'finding':
        review_by_finding[r['subject_id']].append({'record': r, 'source': pointer})
inventory = payloads['03-source-inventory-v4.json']['sections']
topic_entries = [e['values'] for e in payloads['03-taxonomy-v4.json']['records'] if e['kind'] == 'comparison_topic']
topics = {t['topic_id']: t for t in topic_entries}
topic_bases = [e['values'] for e in payloads['03-taxonomy-v4.json']['records'] if e['kind'] == 'topic_basis']
cells, support_refs = [], {}
for ident, entry in sorted(expected.items()):
    row = entry['row']
    basis = []
    dispositions = []
    for fentry in entry['fields']:
        field = fentry['field']
        original_id = by_kind['comparison_field'].get(field['id'], {}).get('id')
        # Root pointer identifies the authored field even after two mechanical maps.
        root_path = ROOT / fentry['root']['path']
        root_index = int(fentry['root']['pointer'].split('/')[2])
        original_field = payloads[root_path.name]['records'][root_index]['values']
        original_id = original_field['id']
        passage_ids = sorted(evidence[field['summary_finding_id']] | evidence[field['quote_finding_id']])
        reviews = semantic_by_subject['comparison_field', original_id][-1:]
        finding_reviews = ([review_by_finding[k][-1] for k in (field['summary_finding_id'], field['quote_finding_id'])
                            if review_by_finding[k]] if not reviews else [])
        if not reviews and not finding_reviews:
            errors.append({'kind': 'missing_authored_field_reason', 'id': original_id})
        assertion = {'kind': 'supported_field', 'field': field['field'], 'condition_key': field['condition_key'],
                     'summary_finding_id': field['summary_finding_id'], 'quote_finding_id': field['quote_finding_id'],
                     'passage_ids': passage_ids, 'original_field': fentry['root'],
                     'semantic_reviews': reviews, 'finding_reviews': finding_reviews}
        basis_id = 'basis-' + hashlib.sha256(canon(assertion).encode()).hexdigest()[:24]
        support_refs[basis_id] = assertion
        basis.append(basis_id)
        dispositions.append({'field': field['field'], 'disposition': 'source_supported', 'basis_id': basis_id})
    if row['state'] == 'no_explicit_statement':
        scope = by_kind['comparison_review_scope'].get(row['scope_id'])
        if not scope:
            errors.append({'kind': 'missing_scope', 'id': row['scope_id']})
        assertion = {'kind': 'dated_source_scope', 'scope': scope,
                     'source': origins.get(('comparison_review_scope', row['scope_id'])),
                     'semantic_reviews': semantic_by_subject['comparison_review_scope', row['scope_id']]}
        basis_id = 'basis-' + hashlib.sha256(canon(assertion).encode()).hexdigest()[:24]
        support_refs[basis_id] = assertion
        basis.append(basis_id)
    if row['state'] == 'document_missing':
        missing = by_kind['missing'].get(row['missing_id'])
        # Some original Phase-2 missing/attempt records live in the closed source
        # packages, not comparison JSON. Resolve them from dossier source packages.
        if missing is None:
            errors.append({'kind': 'missing_documentary_origin', 'id': row['missing_id']})
        assertion = {'kind': 'documentary_gap', 'missing_id': row['missing_id'], 'missing': missing,
                     'attempt': by_kind['attempt'].get(missing['attempt_id']) if missing else None}
        basis_id = 'basis-' + hashlib.sha256(canon(assertion).encode()).hexdigest()[:24]
        support_refs[basis_id] = assertion
        basis.append(basis_id)
    if not basis:
        errors.append({'kind': 'unresolved_source_basis', 'id': ident, 'state': row['state']})
    domain = topics[row['topic_id']]['domain']
    wanted = ['principle', 'target', 'instrument'] if domain == 'program' else ['charter_answer']
    for field in wanted:
        if not any(d['field'] == field for d in dispositions):
            dispositions.append({'field': field,
                'disposition': ('documentary_gap' if row['state'] == 'document_missing' else
                                'no_explicit_statement_in_recorded_scope' if row['state'] == 'no_explicit_statement' else
                                'not_asserted_by_this_source_judgment'),
                'basis_ids': basis,
                'limit': 'This is the boundary of this cited judgment, not a newly performed whole-document search or an opposing party position.'})
    key = {'topic_id': row['topic_id'], 'party_id': row['party_id'], 'source_role': row['source_role'],
           'version_id': row['version_id'], 'level': row['level'], 'organ': row['organ'],
           'context_judgment': entry.get('original_judgment_id', row['id'])}
    cell_id = 'cell-' + hashlib.sha256(canon(key).encode()).hexdigest()[:24]
    inventory_ids = [i for i, s in enumerate(inventory) if s['party_id'] == row['party_id'] and
                     s['source_role'] == row['source_role'] and s['version_id'] == row['version_id'] and
                     row['topic_id'] in s['topic_ids']]
    cells.append({'id': cell_id, 'logical_key': key, 'disposition': row['state'],
                  'source_judgment': entry['root'], 'source_judgment_record': referenced_value(entry['root']),
                  'mapping_refs': entry['mapping'],
                  'mapping_records': [referenced_value(r) for r in entry['mapping']],
                  'basis_ids': basis, 'field_dispositions': dispositions,
                  'inventory_section_indexes': inventory_ids,
                  'fulfilment_locator_only': ident})

parties = ['yeni-parti', 'tip', 'dem', 'iyi', 'yeni-yol', 'dbp', 'emep', 'saadet', 'demokrat']
pairs = collections.defaultdict(list)
for cell in cells:
    k = cell['logical_key']
    pairs[k['topic_id'], k['party_id']].append(cell['id'])
universe = []
for tid in topics:
    for party in parties:
        found = pairs[tid, party]
        universe.append({'topic_id': tid, 'party_id': party, 'cell_ids': found,
                         'disposition': 'source_judgments_enumerated' if found else 'unresolved'})
        if not found:
            errors.append({'kind': 'topic_party_not_disposed', 'topic_id': tid, 'party_id': party})
synthesis_obligations = []
for synthesis, pointer in multi['comparison_synthesis']:
    if synthesis['taxonomy_version'] != 4:
        continue
    review = by_kind['comparison_semantic_review'].get(('comparison_synthesis', synthesis['id'], 'agent'))
    if not review:
        errors.append({'kind': 'missing_authored_synthesis_judgment', 'id': synthesis['id']})
        continue
    typed = json.loads(review['reason'])
    synthesis_obligations.append({'id': synthesis['id'], 'topic_id': synthesis['topic_id'],
        'source_authored_claim': synthesis, 'source': pointer, 'typed_source_judgment': typed,
        'original_review': review,
        'review_source': origins['comparison_semantic_review', ('comparison_synthesis', synthesis['id'], 'agent')]})
synthesis_obligations = list({s['id']: s for s in synthesis_obligations}.values())
write('source-basis.json', {'artifact_version': 1, 'completion_contract_target': 2,
    'artifact_kind': 'independently_persisted_inherited_source_expectations',
    'reviewer_kind': 'agent', 'taxonomy_version': 4,
    'origin_policy': 'Original authored scopes, source-linked field judgments and explicit semantic mappings; no candidate rows or completion proof are inputs.',
    'new_source_reading_claim': False, 'human_acceptance': False,
    'source_documents': documents, 'topics': topic_entries, 'topic_bases': topic_bases,
    'inventory_sections': inventory, 'source_assertions': support_refs,
    'synthesis_obligations': synthesis_obligations,
    'universe': universe, 'cells': cells, 'unresolved': errors})

# Candidate is read only AFTER expectation construction, solely for discrepancy
# detection. It cannot fill missing source judgments or change the expected set.
release = json.loads((ROOT / 'data/current.json').read_text())['release_id']
data = json.loads((ROOT / 'data/releases' / release / 'records.json').read_text())
selected_rows = {r['id']: r for r in data['comparison_row'] if r['taxonomy_version'] == 4}
selected_fields = [f for f in data['comparison_field'] if f['row_id'] in selected_rows]
expected_ids = {c['fulfilment_locator_only'] for c in cells}
differences = {'expected_without_candidate': sorted(expected_ids - selected_rows.keys()),
               'candidate_without_source_expectation': sorted(selected_rows.keys() - expected_ids),
               'logical_dimension_mismatches': []}
for cell in cells:
    row = selected_rows.get(cell['fulfilment_locator_only'])
    if row:
        for key in ('topic_id', 'party_id', 'source_role', 'version_id', 'level', 'organ'):
            if row[key] != cell['logical_key'][key]:
                differences['logical_dimension_mismatches'].append({'cell_id': cell['id'], 'dimension': key})
stats = {'topics': len(topics), 'parties': len(parties), 'topic_party_dispositions': len(universe),
         'source_cells': len(cells), 'source_assertions': len(support_refs),
         'source_authored_synthesis_obligations': len(synthesis_obligations),
         'field_supported_dispositions': sum(d['disposition'] == 'source_supported' for c in cells for d in c['field_dispositions']),
         'unresolved_source_items': len(errors), 'candidate_differences': differences}
write('construction-check.json', dict(stats, candidate_release=release,
    source_basis_sha256=hashlib.sha256((OUT / 'source-basis.json').read_bytes()).hexdigest(),
    note='Counts are diagnostics, not coverage requirements or semantic approval.'))
print(json.dumps(stats, ensure_ascii=False, indent=2))
