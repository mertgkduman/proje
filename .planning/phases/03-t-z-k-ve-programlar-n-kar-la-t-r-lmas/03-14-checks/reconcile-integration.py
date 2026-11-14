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
        mappings = []
        for row in rows:
            fields = [{'old_id': r['id'], 'new_id': 'test-v3-' + r['id']} for r in db.execute('SELECT id FROM comparison_field WHERE row_id=?', (row['id'],))]
            changes = [{'old_id': r['id'], 'new_id': 'test-v3-' + r['id']} for r in db.execute('SELECT id FROM comparison_change WHERE row_id=?', (row['id'],))]
            mappings.append(dict(old_row_id=row['id'], new_row_id='test-v3-' + row['id'], topic_id=row['topic_id'], reason='Yalıtılmış test', fields=fields, changes=changes))
    finally:
        db.close()
    for item in topics + dictionary + bases:
        item['taxonomy_version'] = 3
    topics[0]['definition'] += ' Yalıtılmış test kapsamı.'
    taxonomy = dict(taxonomy_version=3, records=([dict(kind='topic', values=t) for t in dictionary] + [dict(kind='topic_basis', values=b) for b in bases] + [dict(kind='comparison_topic', values=t) for t in topics]), row_mappings=mappings)
    inventory = json.loads((Path.cwd() / 'data/comparisons/03-source-inventory.json').read_text(encoding='utf-8'))
    inventory['taxonomy_version'] = 3
    payload = dict(contract_version=1, taxonomy_version=3, stage='partial', records=[])
    arsiv.comparison_reconcile(work, taxonomy, inventory, payload)
    snapshot = arsiv.export_db(work / 'records.sqlite3', 'isolated-test', strict_identity=True)
    assert snapshot['comparison_contract'][0]['taxonomy_version'] == 3
    assert len([r for r in snapshot['comparison_row'] if r['taxonomy_version'] == 2]) == len(rows)
    assert len([r for r in snapshot['comparison_row'] if r['taxonomy_version'] == 3]) == len(rows)
    print('RECONCILE_REAL_EXPORT_OK', len(rows), flush=True)
