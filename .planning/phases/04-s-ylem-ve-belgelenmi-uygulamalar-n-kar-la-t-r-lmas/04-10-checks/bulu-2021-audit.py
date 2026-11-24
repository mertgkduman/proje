from pathlib import Path
from hashlib import sha256
import json, sqlite3, sys
import arsiv

root, package_path = map(Path, sys.argv[1:])
folder, = (root / 'releases').iterdir()
package = json.loads(package_path.read_text())
records = package['practice_records']
manifest = json.loads((folder/'manifest.json').read_text())
assert manifest['preview']
assert all(sha256((folder/name).read_bytes()).hexdigest()==digest for name,digest in manifest['files'].items())
export = json.loads((folder/'records.json').read_text())
with sqlite3.connect((folder/'records.sqlite3').resolve().as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_statement','practice_relation','practice_candidate','practice_dispute'):
        for row in records[table]:
            found = db.execute('select * from '+table+' where id=?',(row['id'],)).fetchone()
            assert found and dict(found)==row and row in export[table], (table,row['id'])
html = (folder/'index.html').read_text()
for row in records['practice_relation']:
    for prefix in ('party','comparison'):
        assert html.count('id="'+prefix+'-practice-'+row['id']+'"')==1
for prefix in ('party','comparison'):
    assert html.count('id="'+prefix+'-unmatched-0410-bulu-2021-unmatched"')==1
    assert html.count('href="#'+prefix+'-unmatched-0410-bulu-2021-unmatched"')>=1
assert html.count('data-finding-id="0410-bulu-2021-conflict-finding"')==2
assert 'EMEP MYK açıklaması aynı gelişmeyi istifa olarak adlandırır' in html
assert arsiv.audit_release(folder.name,storage_root=root)==folder.name
assert sha256(Path('data/current.json').read_bytes()).hexdigest()=='5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7'
print('EMEP_PREVIEW_DB_JSON_BOTH_VIEWS_AND_INDEPENDENT_AUDIT_OK',folder)
