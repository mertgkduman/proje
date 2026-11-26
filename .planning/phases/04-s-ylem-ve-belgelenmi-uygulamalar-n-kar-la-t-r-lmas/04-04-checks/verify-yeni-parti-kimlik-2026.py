"""Check the isolated Yeni Parti identity preview before accepting the draft."""
from hashlib import file_digest
from pathlib import Path
import json
import re
import sqlite3
import sys

from uygulamalar import practice_coverage_states, validate_practice_closure

scratch, job = Path(sys.argv[1]), sys.argv[2]
case = 'yeni-parti-kimlik-2026'
prefix = '0404-yeni-kimlik-2026'
statement = 'practice-efcecaa0915230b240585109772983b0737267707db445251fcf30f32b119020'
event = 'practice-e673654ec7b038837263bb4aa572ca8889122963e97546aad6c09d846fae71af'
stem = scratch / f'{case}-{job}'
candidate = Path(sys.argv[3])
canonical = Path('data')
inv_path = canonical / 'practices/04-inventory.json'


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    with path.open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def verify_files(directory, entries):
    for name, expected in entries.items():
        assert digest(directory / name) == expected, name


receipt = read(stem.with_suffix('.json'))
assert receipt['job'] == job and receipt['scope'] == case
assert digest(inv_path) == receipt['inventory_sha256']
package, review = [candidate / f'{case}{suffix}-draft.json' for suffix in ('', '-review')]
assert digest(package) == receipt['package_sha256']
assert digest(review) == receipt['review_sha256']
for step, marker in (('input', 'PRACTICE_INPUT_OK'), ('source', 'PRACTICE_SOURCE_REVIEW_OK'),
                     ('preview', 'PRACTICE_PREVIEW_OK')):
    assert Path(f'{stem}-{step}.exit').read_text().strip() == '0', step
    assert Path(f'{stem}-{step}.log').read_text().startswith(marker), step

base = receipt['canonical']
assert base['release'] == 'f67ca0a35e634035bf3aa83a46571f50'
assert base['pointer'] == '5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7'
assert digest(canonical / 'current.json') == base['pointer']
assert not (canonical / '.write.lock').exists()
base_release = canonical / 'releases' / base['release']
assert digest(base_release / 'manifest.json') == base['manifest']
verify_files(base_release, base['files'])

release = Path(receipt['preview'])
manifest = read(release / 'manifest.json')
assert digest(release / 'manifest.json') == receipt['preview_manifest_sha256']
assert manifest['preview'] and manifest['base_release'] == base['release']
assert manifest['renderer_version'] == 32
verify_files(release, manifest['files'])
verify_files(release.parents[1], manifest['asset_files'])

records = read(release / 'records.json')
wanted = read(package)['practice_records']
closures = wanted['practice_closure']
assert len(closures) == 1 and closures[0]['id'] == prefix + '-statement-closure'
assert closures[0]['scope_id'] == statement and json.loads(closures[0]['residual_lead_ids']) == []
assert validate_practice_closure(records, read(inv_path))
states = {row['cell_id']: row['state'] for row in practice_coverage_states(records, read(inv_path))}
assert len(states) == 5490
assert {sid for sid, state in states.items() if state == 'closed'} == {statement}
assert states[event] == 'open'

counts = {'practice_event': 148, 'practice_relation': 142, 'practice_closure': 1}
new_days = {'kurulus': '2026-07-24', 'savunma': '2026-09-29', 'ret': '2026-10-21'}
with sqlite3.connect((release / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert db.execute('PRAGMA foreign_key_check').fetchall() == []
    db.row_factory = sqlite3.Row
    for table, count in counts.items():
        expected = {row['id']: row for row in wanted[table]}
        assert len(expected) == count
        assert expected == {row['id']: row for row in records[table] if row['id'] in expected}
        assert expected == {row['id']: dict(row) for row in db.execute(f'SELECT * FROM {table}') if row['id'] in expected}
    found = db.execute(
        'SELECT c.id, c.state, c.scope_id, c.relation_id, e.event_at FROM practice_candidate c '
        'JOIN practice_event e ON e.id=c.event_id WHERE c.id LIKE ?', (prefix + '%',))
    assert {tuple(row) for row in found} == {
        (f'{prefix}-{key}-unmatched', 'unmatched', event, None, day) for key, day in new_days.items()}

html = (release / 'index.html').read_text()
for view in ('party', 'comparison'):
    statement_anchor = f'{view}-statement-{prefix}-statement'
    assert html.count(f'id="{statement_anchor}"') == 1
    assert f'href="#{statement_anchor}"' in html
    for key in new_days:
        anchor = f'{view}-unmatched-{prefix}-{key}-unmatched'
        assert html.count(f'id="{anchor}"') == 1 and f'href="#{anchor}"' in html, anchor
    for scope, label in ((statement, 'Belirtilen kapsam incelendi'), (event, 'Araştırma sürüyor')):
        target = re.search(rf'<p\b[^>]*id="{view}-scope-{scope}"[^>]*>([^<]*)</p>', html)
        assert target and label in target.group(1), (view, scope)
proof = {'job': str(job), 'preview': receipt['preview'], 'preview_manifest_sha256': receipt['preview_manifest_sha256'],
         'package_sha256': receipt['package_sha256'], 'review_sha256': receipt['review_sha256'],
         'canonical_pointer': base['pointer'], 'verified_assets': len(manifest['asset_files']),
         'validated_renderer': manifest['renderer_version'], **counts,
         'statement_scope': statement, 'statement_state': states[statement],
         'event_scope': event, 'event_state': states[event], 'unclosed_inventory_cells': 5489}
print(json.dumps(proof, ensure_ascii=False, indent=2))
