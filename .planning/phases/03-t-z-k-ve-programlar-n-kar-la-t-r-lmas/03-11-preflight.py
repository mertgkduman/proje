import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import pdf_page_text

root = Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas')
pdf = Path('data/objects/6718b7ca1b2997d0d1f0e52999c8c5ce852af648be7e83cb26c5a7eef060805c/original.pdf')
paths = sys.argv[1:]
assert len(paths) == 2
records = [r for path in paths for r in json.loads(Path(path).read_text())['records']]
by_kind = {}
for record in records:
    by_kind.setdefault(record['kind'], []).append(record['values'])
rows, fields = by_kind['comparison_row'], by_kind['comparison_field']
topics = {r['values']['topic_id'] for r in json.loads(Path('data/comparisons/03-taxonomy.json').read_text())['records']
          if r['kind'] == 'comparison_topic' and r['values']['domain'] == 'program'}
assert len(topics) == 135 and Counter(row['topic_id'] for row in rows) == Counter(topics)
assert set(row['id'] for row in rows) >= {'03-v2-saadet-demokrasi', '03-v2-saadet-temel-yurttaslik-geliri'}
for row in rows:
    ff = [f for f in fields if f['row_id'] == row['id']]
    if row['state'] == 'no_explicit_statement':
        assert not ff and any(s['id'] == row['scope_id'] and s['result'] == 'no_explicit_statement'
                              for s in by_kind['comparison_review_scope'])
    else:
        assert row['state'] == 'evidence' and ff and not row['scope_id']
passages = {p['id']: p for p in by_kind['passage']}
findings = {f['id']: f for f in by_kind['finding']}
assert len(passages) == len(by_kind['passage']) and len(findings) == len(by_kind['finding'])
pages = [pdf_page_text(pdf, n) for n in range(70)]
for passage in passages.values():
    assert passage['version_id'] == '0209-saadet-current-program-v1'
    assert passage['exact'] in pages[passage['pdf_page_index']]
    assert passage['printed_page'] == str(passage['pdf_page_index'] + 1)
for field in fields:
    for k in ('summary_finding_id', 'quote_finding_id'):
        assert field[k] in findings
        assert any(e['finding_id'] == field[k] and e['passage_id'] in passages for e in by_kind['finding_evidence'])
    assert any(x['subject_kind'] == 'comparison_field' and x['subject_id'] == field['id']
               and x['reviewer_kind'] == 'agent' for x in by_kind['comparison_semantic_review'])
    if field['condition_key']:
        assert field['row_id'] == '03-v2-saadet-temel-yurttaslik-geliri'
        assert field['condition_key'] == 'Ülkede doğmuş, ülke için çalışmış ve vergi ödemiş vatandaşlar'
for scope in by_kind['comparison_review_scope']:
    assert any(x['subject_kind'] == 'comparison_review_scope' and x['subject_id'] == scope['id']
               and x['reviewer_kind'] == 'agent' for x in by_kind['comparison_semantic_review'])
for path in paths:
    for candidate in json.loads(Path(path).read_text()).get('backfill_candidates', []):
        assert candidate['source_version'] == '0209-saadet-current-program-v1'
        assert candidate['backfill_plan'] == '03-14' and candidate['scope']
        assert all(pid in passages for pid in candidate['passage_ids'])
inv = json.loads((root / '03-11-line-inventory-draft.json').read_text())
assert len(inv['sections']) == 80 and len({s['id'] for s in inv['sections']}) == 80
assert {s['id'] for s in inv['sections']} <= {x['section_id'] for x in inv['lines']}
assert len({x['id'] for x in inv['lines']}) == len(inv['lines'])
assert all(x['owner'] in (1, 2) for x in inv['lines'])
assert {x['pdf_page_index'] for x in inv['lines']} == set(range(70))
owners = {section['id']: section['owner'] for section in inv['sections']}
assert all(line['owner'] == owners[line['section_id']] for line in inv['lines'] if line['section_id'] != 'FRONT-MATTER')
cross = json.loads((root / '03-11-cross-review-draft.json').read_text())
assert all(item['status'] == 'reviewed' and item['topic_owner'] != item['section_owner'] for item in cross)
for item in cross:
    expected = f"0311-saadet-p{item['topic_owner']}-{item['candidate_index']:03d}-{item['topic']}-f"
    assert any(field['id'] == expected for field in fields)
print('DRAFT_PREFLIGHT_OK', len(rows), 'topics,', len(fields), 'fields,',
      len(by_kind['comparison_review_scope']), 'scopes,', len(inv['lines']), 'source lines')
