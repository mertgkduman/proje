#!/bin/bash
#SBATCH --job-name=gsd0410-institution
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
project=/hpc/group/pfisterlab/mg551/storage/proje
checks=$project/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks
stage=$project/data/.staging/gsd-0410-institution-$SLURM_JOB_ID
base=f67ca0a35e634035bf3aa83a46571f50
package=$checks/institution-tracer-draft.json
review=$checks/institution-review-draft.json
cd "$project"
printf '%s  %s\n' c51c7903664c1e2bbf88a57365b258eec4ec2634311e0747db867e0d5c67e77b "$package" 15213c7bdc38c7902e658ca3447fad376937b7e1ba0feeaa621e3c622bdb6b88 "$review" | sha256sum -c -
mkdir -p "$stage"
cp -al "$project/data/.staging/gsd-0407-institution-62397211/check" "$stage/check"
python3 - "$project/data/practices/sources/emep" "$stage/check/data" <<'PY'
from pathlib import Path
import shutil,sys
source,target=map(Path,sys.argv[1:])
for path in source.rglob('*'):
    if not path.is_file(): continue
    dest=target/path.relative_to(source)
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists(): assert dest.read_bytes()==path.read_bytes(),dest
    else: shutil.copyfile(path,dest)
PY
printf '%s  %s\n' 5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7 "$stage/check/data/current.json" | sha256sum -c -
python3 "$stage/check/src/arsiv.py" practice-check --input "$package" --inventory "$stage/check/data/practices/04-inventory.json" --base-release "$base"
python3 "$stage/check/src/arsiv.py" practice-source-check --input "$package" --review "$review"
tmp=$(mktemp -d /tmp/gsd0410-institution.XXXXXXXX)
trap 'rm -rf -- "$tmp"' EXIT
python3 src/arsiv.py practice-preview --input "$package" --inventory data/practices/04-inventory.json --base-release "$base" --source-root data/practices/sources/emep --out "$tmp/preview"
cp -a "$tmp/preview" "$stage/preview"
PYTHONPATH=src python3 - "$stage/preview" "$package" <<'PY'
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
assert html.count('data-finding-id="0410-kongre-statement-quote"')==2
assert html.count('data-finding-id="0410-kongre-election-result"')==2
assert arsiv.audit_release(folder.name,storage_root=root)==folder.name
assert sha256(Path('data/current.json').read_bytes()).hexdigest()=='5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7'
print('EMEP_PREVIEW_DB_JSON_BOTH_VIEWS_AND_INDEPENDENT_AUDIT_OK',folder)
PY
