"""Run all gates and independently inspect both November events and views."""
import importlib.util, json, sqlite3, sys
from pathlib import Path

checks=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('practice_validation',checks.parent/'04-04-checks'/'samsun-reply-validation.py')
h=importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
h.HERE=checks; h.SOURCE=h.DATA/'practices/sources/demokrat'
case='six-leaders-november-dp-v2'; stem='0412-six-leaders-2022-11-28'
package=checks/f'{case}-draft.json'; review=checks/f'{case}-review-draft.json'
hashes = [h.sha(path) for path in (package, review)]
records = json.loads(package.read_bytes())['practice_records']
assert [len(records[key]) for key in ('practice_event', 'practice_relation', 'practice_closure')] == [83, 54, 0]
if len(sys.argv) == 3 and sys.argv[1] == '--recover':
    proof = Path(sys.argv[2])
    recovery = json.loads(proof.read_bytes())
    assert recovery['initial_job'] == '62714572' and recovery['initial_terminal'] == 'FAILED|1:0'
    assert hashes == [
        '83b02dd64c3791a8774cacfe788995c247a3263e4565e8fd913c74d2359ef736',
        '226698882d18a9a29565b44ff7c2c37749666e22c4cbf1c2a543117b6ad1059c',
    ]
    for gate, marker in (
        ('input', 'PRACTICE_INPUT_OK'), ('source', 'PRACTICE_SOURCE_REVIEW_OK'),
        ('preview', 'PRACTICE_PREVIEW_OK'),
    ):
        name = f"{case}-{recovery['initial_job']}-{gate}"
        assert (checks / f'{name}.exit').read_text().strip() == '0', gate
        assert (checks / f'{name}.log').read_text().startswith(marker), gate
    restored = Path(recovery['preview'])
    manifest_path = restored / 'manifest.json'
    assert h.sha(manifest_path) == recovery['manifest_sha256']
    assert recovery['manifest_sha256'] == 'ad3b0f12a2025a6fb760746815a9b41dccbdc73ede5b3a7bb2ab56158ee244e3'
    manifest = json.loads(manifest_path.read_bytes())
    assert manifest['preview'] and manifest['renderer_version'] == 31
    assert manifest['base_release'] == h.EXPECTED_RELEASE
    assert not recovery['assets_missing']
    assert len(manifest['asset_files']) == recovery['assets_expected'] == 1778
    assert len(recovery['assets_restored']) == 1559
    assert all(h.sha(restored / name) == value for name, value in manifest['files'].items())
    assert all(h.sha(restored.parents[1] / name) == value for name, value in manifest['asset_files'].items())
    receipt = dict(preview=str(restored), canonical=h.canonical_identity())
else:
    assert hashes == sys.argv[1:]
    receipt = h.main(package, review, case, f'{stem}-meeting-event', f'{stem}-meeting-relation',
                     None, expected_party='demokrat', namespace='gsd-0412')
folder=Path(receipt['preview']); data=json.loads((folder/'records.json').read_bytes()); report=(folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
 for table in ('practice_event', 'practice_relation'):
  expected = {row['id']: row for row in records[table]}
  assert {row['id']: row for row in data[table] if row['id'] in expected} == expected
  assert {row['id']: dict(row) for row in db.execute(f'SELECT * FROM {table}') if row['id'] in expected} == expected
 for name in ('meeting','presentation'):
  for table,suffix in (('practice_statement','statement'),('practice_event','event'),('practice_relation','relation'),('practice_candidate','candidate'),('practice_contribution','uysal-contribution')):
   ident=f'{stem}-{name}-{suffix}'; expected=next(r for r in records[table] if r['id']==ident)
   actual=db.execute(f'SELECT * FROM {table} WHERE id=?',(ident,)).fetchone()
   assert expected in data[table] and actual is not None and expected==dict(actual),ident
  for view in ('party','comparison'):
   anchor=f'{view}-practice-{stem}-{name}-relation'; marker=f'id="{anchor}"'
   assert report.count(marker)==1 and f'href="#{anchor}"' in report
   assert 'Uysal' in report.split(marker,1)[1].split('</article>',1)[0],anchor
assert h.canonical_identity()==receipt['canonical']
print('DEMOCRAT_NOVEMBER_BOTH_EVENTS_BOTH_VIEWS_OK',folder,flush=True)
