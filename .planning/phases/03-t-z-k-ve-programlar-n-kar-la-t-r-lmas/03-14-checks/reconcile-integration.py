"""Isolated integration test: real archive bytes, synthetic version transition."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / 'src'))
import arsiv

original = arsiv.DATA
base = arsiv.current()
with tempfile.TemporaryDirectory(prefix='proje-0314-integration-', dir='/tmp') as tmp:
    root = Path(tmp)
    isolated = root / 'data'
    isolated.mkdir()
    for name in ('objects', 'views'):
        shutil.copytree(original / name, isolated / name)
    arsiv.DATA = isolated
    work = root / 'work'
    work.mkdir()
    shutil.copyfile(original / 'releases' / base / 'records.sqlite3', work / 'records.sqlite3')
    (work / 'workspace.json').write_text(json.dumps({'base': base, 'token': 'isolated-test'}))
    (isolated / '.write.lock').write_text(json.dumps({'token': 'isolated-test'}))
    db = arsiv.connect_readonly(work / 'records.sqlite3')
    try:
        topics = [dict(r) for r in db.execute('SELECT * FROM comparison_topic WHERE taxonomy_version=2')]
        dictionary = [dict(r) for r in db.execute('SELECT * FROM topic WHERE taxonomy_version=2')]
        bases = [dict(r) for r in db.execute('SELECT * FROM topic_basis WHERE taxonomy_version=2')]
        rows = [dict(r) for r in db.execute('SELECT * FROM comparison_row WHERE taxonomy_version=2')]
        test_source_rows = [r for r in rows if r['topic_id'] == 'temel-yurttaslik-geliri']
        test_fields = [dict(f) for row in test_source_rows for f in db.execute('SELECT * FROM comparison_field WHERE row_id=?', (row['id'],))]
        row_refs = {}
        mappings = []
        for row in rows:
            fields = [{'old_id': r['id'], 'new_id': 'test-v3-' + r['id']} for r in db.execute('SELECT id FROM comparison_field WHERE row_id=?', (row['id'],))]
            changes = [{'old_id': r['id'], 'new_id': 'test-v3-' + r['id']} for r in db.execute('SELECT id FROM comparison_change WHERE row_id=?', (row['id'],))]
            mappings.append(dict(old_row_id=row['id'], new_row_id='test-v3-' + row['id'], topic_id=row['topic_id'], reason='Yalıtılmış test', fields=fields, changes=changes))
            if row['state'] == 'evidence':
                row_refs[row['id']] = sorted({r['passage_id'] for r in db.execute('SELECT e.passage_id FROM comparison_field f JOIN finding_evidence e ON e.finding_id IN (f.summary_finding_id, f.quote_finding_id) WHERE f.row_id=?', (row['id'],))})
            else:
                row_refs[row['id']] = [row['scope_id'] or row['missing_id']]
    finally:
        db.close()
    for item in topics + dictionary + bases:
        item['taxonomy_version'] = 3
    topics[0]['definition'] += ' Yalıtılmış test kapsamı.'
    source_topic = next(t for t in topics if t['topic_id'] == 'temel-yurttaslik-geliri')
    source_dictionary = next(t for t in dictionary if t['id'] == 'temel-yurttaslik-geliri')
    source_bases = [b for b in bases if b['topic_id'] == 'temel-yurttaslik-geliri']
    test_topic = dict(source_topic, topic_id='test-nine-party-topic', order_index=99999, definition='Yalıtılmış test: dokuz parti konusu.')
    test_dictionary = dict(source_dictionary, id='test-nine-party-topic', label='Yalıtılmış test konusu', change_reason='Yalıtılmış test')
    test_bases = [dict(b, topic_id='test-nine-party-topic') for b in source_bases]
    topics.append(test_topic)
    dictionary.append(test_dictionary)
    bases.extend(test_bases)
    taxonomy = dict(taxonomy_version=3, records=([dict(kind='topic', values=t) for t in dictionary] + [dict(kind='topic_basis', values=b) for b in bases] + [dict(kind='comparison_topic', values=t) for t in topics]), row_mappings=mappings)
    inventory = json.loads((Path.cwd() / 'data/comparisons/03-source-inventory.json').read_text(encoding='utf-8'))
    inventory['taxonomy_version'] = 3
    test_rows = [dict(row, id='test-new-' + row['id'], topic_id='test-nine-party-topic', taxonomy_version=3) for row in test_source_rows]
    test_fields = [dict(field, id='test-new-' + field['id'], row_id='test-new-' + field['row_id']) for field in test_fields]
    assert len({r['party_id'] for r in test_rows}) == 9
    payload = dict(contract_version=1, taxonomy_version=3, stage='partial', records=([dict(kind='comparison_row', values=r) for r in test_rows] + [dict(kind='comparison_field', values=f) for f in test_fields]))
    payload['row_reviews'] = []
    source_by_id = {r['id']: r for r in rows}
    selected = [(m['new_row_id'], source_by_id[m['old_row_id']], topics[0]) for m in mappings if m['topic_id'] == topics[0]['topic_id']]
    selected.extend((r['id'], source_by_id[r['id'].removeprefix('test-new-')], test_topic) for r in test_rows)
    for rid, old, topic in selected:
        payload['row_reviews'].append(dict(row_id=rid, topic_id=topic['topic_id'], party_id=old['party_id'], definition=topic['definition'], conditions='Yalıtılmış test koşulu', refs=row_refs[old['id']]))
        reason = topic['definition'] + ' Yalıtılmış test koşulu ' + ' '.join(row_refs[old['id']])
        payload['records'].append(dict(kind='comparison_semantic_review', values=dict(subject_kind='comparison_row', subject_id=rid, reviewer_kind='agent', reviewed_at='2026-11-14T00:00:00+00:00', result='reviewed', reason=reason)))
    arsiv.comparison_reconcile(work, taxonomy, inventory, payload)
    snapshot = arsiv.export_db(work / 'records.sqlite3', 'isolated-test', strict_identity=True)
    assert snapshot['comparison_contract'][0]['taxonomy_version'] == 3
    assert len([r for r in snapshot['comparison_row'] if r['taxonomy_version'] == 2]) == len(rows)
    assert len([r for r in snapshot['comparison_row'] if r['taxonomy_version'] == 3]) == len(rows) + len(test_rows)
    assert len({r['party_id'] for r in snapshot['comparison_row'] if r['topic_id'] == 'test-nine-party-topic'}) == 9
    assert arsiv.validate_changed_topic_reviews(snapshot)
    print('RECONCILE_REAL_EXPORT_OK', len(rows), 'NEW_TOPIC_NINE_PARTIES_OK', flush=True)
