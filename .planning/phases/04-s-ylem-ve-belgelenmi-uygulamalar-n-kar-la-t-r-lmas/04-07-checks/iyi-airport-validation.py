"""Verify three airport motions and unpaired reader cards from a separate data tree."""

from hashlib import file_digest
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile

checks = Path(__file__).resolve().parent
root = checks.parents[3]
module = checks.parent / '04-04-checks' / 'samsun-reply-validation.py'
spec = importlib.util.spec_from_file_location('practice_validation', module)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
candidate = Path(os.environ['GSD0407_AIRPORT_CANDIDATE']).resolve()
package, review = (candidate / f'iyi-airport{suffix}-draft.json' for suffix in ('', '-review'))
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
before = harness.canonical_identity()
packages = json.loads(package.read_bytes())['practice_records']
case = 'iyi-airport'
prefix = '0407-iyi-airport'

with tempfile.TemporaryDirectory(prefix='gsd-0407-airport-base-', dir=candidate) as directory:
    stage = Path(directory)
    shutil.copytree(root / 'src', stage / 'src', ignore=harness.ignore)
    shutil.copytree(root / 'data', stage / 'data', ignore=harness.ignore)
    source_root = stage / 'data/practices/sources/iyi'
    for path in (candidate / 'sources').rglob('*'):
        if path.is_file():
            target = source_root / path.relative_to(candidate / 'sources')
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                assert harness.sha(path) == harness.sha(target)
            else:
                shutil.copyfile(path, target)
    harness.ROOT, harness.DATA = stage, stage / 'data'
    harness.INVENTORY, harness.SOURCE = harness.DATA / 'practices/04-inventory.json', source_root
    os.environ['GIT_DIR'] = str(root / '.git')
    os.environ['GIT_WORK_TREE'] = str(stage)
    assert harness.canonical_identity() == before
    receipt = harness.main(package, review, case, f'{prefix}-beyaz-event',
                           '0407-iyi-ozdag-2020-2021-court-relation', None,
                           expected_party='iyi', namespace='gsd-0407')
    harness.DATA = root / 'data'
    assert harness.canonical_identity() == before

folder = Path(receipt['preview'])
export = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory = sqlite3.Row
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert db.execute('PRAGMA foreign_key_check').fetchall() == []
    for table, count in (('practice_event',26),('practice_relation',15),('practice_closure',0)):
        assert len(packages[table]) == count
        assert all(row in export[table] for row in packages[table])
    dates = {'beyaz':'2018-09-20','ozdag':'2018-11-02','tatlioglu':'2019-02-15'}
    live = db.execute('SELECT c.id,c.state,c.relation_id,e.event_at FROM practice_candidate c '
                      'JOIN practice_event e ON c.event_id=e.id WHERE c.id LIKE ?', (prefix+'%',))
    assert {tuple(row) for row in live} == {(f'{prefix}-{key}-unmatched','unmatched',None,date) for key,date in dates.items()}
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
for rel, expected in manifest['asset_files'].items():
    with (folder.parents[1]/rel).open('rb') as stream:
        assert file_digest(stream,'sha256').hexdigest() == expected
html = (folder/'index.html').read_text()
for key, phrases in {
    'beyaz':('7/3166','25 Ekim','17 Ekim'),
    'ozdag':('8/3','2 Kasım','2 Ekim','hükümsüzlük'),
    'tatlioglu':('10/970','15 Şubat','hükümsüzlük'),
}.items():
    for view in ('party','comparison'):
        anchor = f'{view}-unmatched-{prefix}-{key}-unmatched'
        marker = f'id="{anchor}"'
        assert html.count(marker)==1 and f'href="#{anchor}"' in html
        card = html.split(marker,1)[1].split('</article>',1)[0].casefold()
        assert all(phrase.casefold() in card for phrase in phrases), (anchor,phrases)
print('IYI_AIRPORT_BOTH_VIEWS_OK',folder,flush=True)
