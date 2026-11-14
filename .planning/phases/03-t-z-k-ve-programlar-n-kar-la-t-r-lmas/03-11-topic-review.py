"""Prepare the inspectable topic/field/source review, without mutating inputs."""
import json
from collections import defaultdict
from pathlib import Path

root = Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas')
packets = [json.loads(Path(f'data/comparisons/03-saadet-program-{n}.json').read_text()) for n in (1, 2)]
records = [r for p in packets for r in p['records']]
by_kind = defaultdict(dict)
for record in records:
    v = record['values']
    if 'id' in v:
        by_kind[record['kind']][v['id']] = v
semantic_path = Path('data/comparisons/03-saadet-program-semantic.json')
semantics = json.loads(semantic_path.read_text())['decisions']
if len(semantics) < sum(r['kind'] == 'comparison_semantic_review' for r in records):
    semantics = json.loads(Path('/tmp/03-11-final-semantic-combined.json').read_text())['decisions']
reviews = {(x['subject_kind'], x['subject_id']): x for x in semantics}
evidence = defaultdict(list)
for record in records:
    if record['kind'] == 'finding_evidence':
        evidence[record['values']['finding_id']].append(record['values']['passage_id'])
fields = defaultdict(list)
for f in by_kind['comparison_field'].values():
    summary, quote = by_kind['finding'][f['summary_finding_id']], by_kind['finding'][f['quote_finding_id']]
    ids = list(dict.fromkeys(evidence[summary['id']] + evidence[quote['id']]))
    fields[f['row_id']].append(dict(field_id=f['id'], type=f['field'], condition=f['condition_key'],
        summary=summary['text'], quote=quote['text'], source_ids=ids,
        sources=[dict(id=pid, section=by_kind['passage'][pid]['section'],
                      pdf_page=by_kind['passage'][pid]['pdf_page_index'] + 1,
                      printed_page=by_kind['passage'][pid]['printed_page']) for pid in ids],
        review=reviews['comparison_field', f['id']]['reason']))
result = []
for row in sorted(by_kind['comparison_row'].values(), key=lambda x: x['topic_id']):
    entry = dict(topic_id=row['topic_id'], row_id=row['id'], source_role=row['source_role'],
                 source_version=row['version_id'], state=row['state'], fields=fields[row['id']])
    if row['state'] == 'evidence':
        present = {field['type'] for field in entry['fields']}
        entry['unrepresented_field_types'] = sorted({'principle', 'target', 'instrument'} - present)
        entry['unrepresented_note'] = 'Bu listede kayıt olmaması tek başına alan için yokluk hükmü değildir; gösterim ve gerekirse kaynak kontrolü 03-15/16 içindir.'
    if row['scope_id']:
        scope = by_kind['comparison_review_scope'][row['scope_id']]
        review = reviews['comparison_review_scope', row['scope_id']]
        entry['scope'] = dict(id=scope['id'], question=scope['query_terms'], sections=scope['sections'],
                              result=scope['result'], reason=scope['reason'], context_passage_ids=review['passage_ids'])
    result.append(entry)
assert len(result) == 135
(root / '03-11-topic-review.json').write_text(json.dumps(dict(
    reviewer_kind='agent', note='Bağımsız insan kabulü değildir. Yokluk kapsamı olumlu politika sayılmaz.',
    topics=result), ensure_ascii=False, indent=2)+'\n')
print('TOPIC_REVIEW_OK', len(result), 'topics')
