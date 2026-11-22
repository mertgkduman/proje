#!/bin/bash
#SBATCH --job-name=gsd0407-institution-v3
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail

project=/hpc/group/pfisterlab/mg551/storage/proje
checks=$project/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-07-checks
stage=$project/data/.staging/gsd-0407-institution-$SLURM_JOB_ID
base=f67ca0a35e634035bf3aa83a46571f50
package=$checks/institution-tracer-v3.json
review=$checks/institution-review-v3.json
mkdir -p "$stage"
cd "$project"
printf '%s  %s\n' \
  d6ab78b2725a62a29b5ef0cd98e6d94520fd13bb28acecbb5052750dbf07463b "$package" \
  b88bcf389c1435aba259e45e9c0ec727b97d70e7db7725cf96f1e14711dac188 "$review" | sha256sum -c -
rg -qx 'PRACTICE_INPUT_OK' "$checks/institution-v3-62397727.log"
rg -qx 'PRACTICE_SOURCE_REVIEW_OK' "$checks/institution-v3-62397727.log"
tmp=$(mktemp -d /tmp/gsd0407-institution-v3.XXXXXXXX)
trap 'rm -rf -- "$tmp"' EXIT
python3 src/arsiv.py practice-preview --input "$package" --inventory data/practices/04-inventory.json \
  --base-release "$base" --source-root data/practices/sources/iyi --out "$tmp/preview"
cp -a "$tmp/preview" "$stage/preview"
PYTHONPATH=src python3 - "$stage/preview" "$package" <<'PY'
from pathlib import Path
from hashlib import sha256
import json,sqlite3,sys
import arsiv

root=Path(sys.argv[1])
folder,= (root/'releases').iterdir()
entries=json.loads(Path(sys.argv[2]).read_text())['practice_records']
manifest=json.loads((folder/'manifest.json').read_text())
records=json.loads((folder/'records.json').read_text())
assert manifest['preview'] and manifest['renderer_version']==29
assert not entries['practice_closure']
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    for name in ('practice_event','practice_relation','practice_statement'):
        for row in entries[name]:
            got=db.execute('SELECT * FROM '+name+' WHERE id=?',(row['id'],)).fetchone()
            assert got and dict(got)==row and row in records[name]
html=(folder/'index.html').read_text()
for where in ('party','comparison'):
    assert html.count(f'id="{where}-practice-0407-2023-kurultay-relation"')==1
assert html.count('data-finding-id="0407-2020-kurultay-statement-quote"')==2
assert html.count('data-finding-id="0407-2023-kurultay-vote-result"')==2
assert arsiv.audit_release(folder.name,storage_root=root)==folder.name
assert sha256(Path('data/current.json').read_bytes()).hexdigest()=='5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7'
print('IYI_PREVIEW_DB_JSON_BOTH_VIEWS_AND_INDEPENDENT_AUDIT_OK',folder)
PY
