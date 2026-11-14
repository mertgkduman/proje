"""Create an intentionally invalid, mechanical v3 lineage scaffold.

Blank reasons and unchanged definitions make this unsuitable for reconcile.
Source review and new topic decisions must be authored separately.
"""
import json
import sqlite3
from pathlib import Path

root = Path.cwd()
release = json.loads((root / 'data/current.json').read_text(encoding='utf-8'))['release_id']
if release != 'ae42ae1897864fda810b033ce3ac1e8f':
    raise SystemExit('Beklenen temel sürüm değişti; taslak üretilmedi')
database = root / 'data/releases' / release / 'records.sqlite3'
db = sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True)
db.row_factory = sqlite3.Row
try:
    old = db.execute('SELECT taxonomy_version FROM comparison_contract').fetchone()[0]
    if old != 2:
        raise SystemExit('Beklenen kaynak sözlüğü sürüm 2 değil')
    records = []
    for table in ('topic', 'topic_basis', 'comparison_topic'):
        for row in db.execute(f'SELECT * FROM {table} WHERE taxonomy_version=?', (old,)):
            values = dict(row)
            values['taxonomy_version'] = 3
            records.append(dict(kind=table, values=values))
    mappings = []
    for row in db.execute('SELECT * FROM comparison_row WHERE taxonomy_version=?', (old,)).fetchall():
        fields = [dict(old_id=f['id'], new_id='03-v3-' + f['id']) for f in db.execute('SELECT id FROM comparison_field WHERE row_id=?', (row['id'],))]
        changes = [dict(old_id=c['id'], new_id='03-v3-' + c['id']) for c in db.execute('SELECT id FROM comparison_change WHERE row_id=?', (row['id'],))]
        mappings.append(dict(old_row_id=row['id'], new_row_id='03-v3-' + row['id'], topic_id=row['topic_id'], reason='', fields=fields, changes=changes))
finally:
    db.close()
draft = dict(contract_version=1, taxonomy_version=3, stage='partial', status='in_progress', note='Mekanik taslak; boş gerekçeler ve değişmemiş tanımlar kabulü engeller. Kaynak incelemesi ve yeni konular eksiktir.', base_release=release, records=records, row_mappings=mappings, superseded_rows=[])
output = root / '.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-14-checks/taxonomy-mapping-draft.json'
output.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('DRAFT_ONLY', len(records), len(mappings), output)
