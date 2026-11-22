#!/bin/bash
#SBATCH --job-name=gsd0410-may-institutions
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
project=/hpc/group/pfisterlab/mg551/storage/proje
checks=$project/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks
stage=$project/data/.staging/gsd-0410-may-$SLURM_JOB_ID
base=f67ca0a35e634035bf3aa83a46571f50
package=$checks/may-institutions-draft.json
review=$checks/may-institutions-review-draft.json
cd "$project"
printf '%s  %s\n' 96952766613f911fd46b06507d4b3758e561aceb4ac0be2fb92b0118e8a89307 "$project/data/.staging/gsd-0410-institution-62400681/check/src/arsiv.py" ece0d2238b97c6d1634d894fea5c19596e8291f955a9c746bf8fb360057e1fb3 "$project/data/.staging/gsd-0410-institution-62400681/check/src/uygulamalar.py" 0f668e6146cfb957723a0e342761638d336b07d7d9626191583cb30b1e4483f5 "$project/data/.staging/gsd-0410-institution-62400681/check/src/rapor.py" | sha256sum -c -
printf '%s  %s\n' 2747632b9a85b4b06d4978db89ada4f500585d333f0df00d77552dfa9f973276 "$package" b46694490ec909d19ea36292bc4184896828f40ae64895989b75c6cd3b892523 "$review" | sha256sum -c -
mkdir -p "$stage"
cp -al "$project/data/.staging/gsd-0410-institution-62400681/check" "$stage/check"
python3 - "$project/data/practices/sources/emep" "$stage/check/data" <<'PY'
from pathlib import Path
import shutil,sys
source,target=map(Path,sys.argv[1:])
for path in source.rglob('*'):
    if not path.is_file(): continue
    for dest in (target/path.relative_to(source),target/'practices/sources/emep'/path.relative_to(source)):
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists(): assert dest.read_bytes()==path.read_bytes(),dest
        else: shutil.copyfile(path,dest)
PY
printf '%s  %s\n' 5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7 "$stage/check/data/current.json" | sha256sum -c -
python3 "$stage/check/src/arsiv.py" practice-check --input "$package" --inventory "$stage/check/data/practices/04-inventory.json" --base-release "$base"
python3 "$stage/check/src/arsiv.py" practice-source-check --input "$package" --review "$review"
tmp=$(mktemp -d /tmp/gsd0410-may-institutions.XXXXXXXX)
trap 'rm -rf -- "$tmp"' EXIT
python3 "$stage/check/src/arsiv.py" practice-preview --input "$package" --inventory data/practices/04-inventory.json --base-release "$base" --source-root "$stage/check/data/practices/sources/emep" --out "$tmp/preview"
cp -a "$tmp/preview" "$stage/preview"
PYTHONPATH="$stage/check/src" python3 - "$stage/preview" "$package" <<'PY'
from pathlib import Path
from hashlib import sha256
import json,sqlite3,sys
import arsiv
root=Path(sys.argv[1]); folder,=(root/'releases').iterdir()
package=json.loads(Path(sys.argv[2]).read_text()); records=package['practice_records']
assert json.loads((folder/'manifest.json').read_text())['preview']
export=json.loads((folder/'records.json').read_text())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    for table in ('practice_event','practice_statement','practice_relation'):
        for row in records[table]:
            assert dict(db.execute('select * from '+table+' where id=?',(row['id'],)).fetchone())==row
            assert row in export[table]
html=(folder/'index.html').read_text()
for prefix in ('party','comparison'):
    assert html.count('id="'+prefix+'-practice-0410-2023-kongre-relation"')==1
for row in records['practice_relation']:
    for prefix in ('party','comparison'):
        assert html.count('id="'+prefix+'-practice-'+row['id']+'"')==1
assert html.count('data-finding-id="0410-kongre-statement-quote"')==2
assert html.count('data-finding-id="0410-kongre-election-result"')==2
assert arsiv.audit_release(folder.name,storage_root=root)==folder.name
assert sha256(Path('data/current.json').read_bytes()).hexdigest()=='5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7'
print('EMEP_PREVIEW_DB_JSON_BOTH_VIEWS_AND_INDEPENDENT_AUDIT_OK',folder)
PY
