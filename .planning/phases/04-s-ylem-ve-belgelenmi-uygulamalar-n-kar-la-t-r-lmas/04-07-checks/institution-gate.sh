#!/bin/bash
#SBATCH --job-name=gsd0407-institution
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
project=/hpc/group/pfisterlab/mg551/storage/proje
checks=$project/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-07-checks
stage=$project/data/.staging/gsd-0407-institution-$SLURM_JOB_ID
mkdir -p "$stage/check/data/releases" "$stage/check/data/practices"
cp -a "$project/src" "$stage/check/src"
cp -a "$project/data/objects" "$stage/check/data/objects"
cp -a "$project/data/views" "$stage/check/data/views"
cp -a "$project/data/releases/f67ca0a35e634035bf3aa83a46571f50" "$stage/check/data/releases/"
cp -a "$project/data/current.json" "$stage/check/data/current.json"
cp -a "$project/data/practices/04-inventory.json" "$stage/check/data/practices/04-inventory.json"
cp -a "$checks/institution-tracer-draft.json" "$stage/package.json"
cp -a "$checks/institution-review-draft.json" "$stage/review.json"
printf "%s  %s\n" 44eae651c97979b3108e298b8ad0b9dd8d6614068d4b4925c85d620f176710e3 "$stage/package.json" | sha256sum -c -
printf "%s  %s\n" dd4a78e1d80e8d749a094ef05a223b370cc1b01901a443dcbff531df7e7c139e "$stage/review.json" | sha256sum -c -
python3 - "$project/data/practices/sources/iyi" "$stage/check/data" <<'PY'
import os, shutil, sys
from pathlib import Path
source, dest = map(Path,sys.argv[1:])
for tree in ('objects','views'):
    for path in (source/tree).rglob('*'):
        if not path.is_file(): continue
        target=dest/tree/path.relative_to(source/tree)
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():
            if path.read_bytes()!=target.read_bytes(): raise RuntimeError('archive collision: '+str(target))
        else: shutil.copy2(path,target)
PY
cd "$stage/check"
python3 src/arsiv.py practice-check --input "$stage/package.json" --inventory data/practices/04-inventory.json --base-release f67ca0a35e634035bf3aa83a46571f50
python3 src/arsiv.py practice-source-check --input "$stage/package.json" --review "$stage/review.json"
cd "$project"
python3 src/arsiv.py practice-preview --input "$stage/package.json" --inventory data/practices/04-inventory.json --base-release f67ca0a35e634035bf3aa83a46571f50 --source-root data/practices/sources/iyi --out "$stage/preview"
