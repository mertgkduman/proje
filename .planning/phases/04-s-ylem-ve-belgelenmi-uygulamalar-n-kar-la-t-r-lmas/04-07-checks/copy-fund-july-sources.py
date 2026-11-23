"""Reuse the unchanged 10/4343 source files in the İYİ scope."""

from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv_gorunum import validate_view

here=Path(sys.argv[1])
inputs=json.loads((here.parent/'04-08-checks'/'fund-july-source-records.json').read_bytes())['entries']
src=Path('data/practices/sources/yeni-yol')
dest=src.with_name('iyi')
entries,paths=[],set()
selected={'floor','detail','summary'}


def save(relative):
    path=dest/relative
    body=(src/relative).read_bytes()
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes()==body
    else:
        path.write_bytes(body)
    paths.add(path)
    return body


for entry in inputs:
    kind=entry['kind']
    row=entry['values'].copy()
    identity=row.get('id',row.get('version_id',''))
    if not any(identity.removeprefix('0408-fund-july-') in (key,key+'-v1') for key in selected) and not (
            kind=='passage' and any(identity.startswith('0408-fund-july-'+key+'-') for key in selected)):
        continue
    for key in ('id','document_id','version_id'):
        if key in row:
            row[key]=row[key].replace('0408-fund-july-','0407-fund-july-')
    if kind=='document':
        row['party_id']='iyi'
    if kind=='document_version':
        assert sha256(save(row['original_path'])).hexdigest()==row['sha256']
        save(row['readable_path'])
    if kind=='archive_view':
        manifest=Path(row['manifest_path'])
        for name in json.loads(save(manifest))['files']:
            save(manifest.parent/name)
        validate_view(dest,row)
    entries.append(dict(kind=kind,values=row))
assert len([e for e in entries if e['kind']=='document_version'])==3
(here/'fund-july-source-records.json').write_text(json.dumps(dict(party_id='iyi',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0407-fund-july-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
