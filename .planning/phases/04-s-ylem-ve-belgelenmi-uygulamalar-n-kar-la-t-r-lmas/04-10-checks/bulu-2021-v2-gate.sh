#!/bin/bash
#SBATCH --job-name=gsd0410-bulu
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
project=/hpc/group/pfisterlab/mg551/storage/proje
checks=$project/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks
stage=/work/mg551/gsd-phase04-previews.sgFrq4/gsd-0410-bulu-v2-$SLURM_JOB_ID
base=f67ca0a35e634035bf3aa83a46571f50
package=$checks/bulu-2021-v2-union-draft.json
review=$checks/bulu-2021-v2-union-review-draft.json
cd "$project"
printf '%s  %s\n' 96952766613f911fd46b06507d4b3758e561aceb4ac0be2fb92b0118e8a89307 "$project/data/.staging/gsd-0410-institution-62400681/check/src/arsiv.py" ece0d2238b97c6d1634d894fea5c19596e8291f955a9c746bf8fb360057e1fb3 "$project/data/.staging/gsd-0410-institution-62400681/check/src/uygulamalar.py" 0f668e6146cfb957723a0e342761638d336b07d7d9626191583cb30b1e4483f5 "$project/data/.staging/gsd-0410-institution-62400681/check/src/rapor.py" | sha256sum -c -
printf '%s  %s\n' fb6941933e1b9fca92106f1ae4e77cda969d5955386a41b07041dd19424eda7c "$package" a027ca31ef67dedd6e1c502cdba7494dd55bbce1aa7930624215d8f11523246b "$review" | sha256sum -c -
mkdir "$stage"
cp -a "$project/data/.staging/gsd-0410-institution-62400681/check" "$stage/check"
python3 -c 'from pathlib import Path; import shutil,sys; source,target=map(Path,sys.argv[1:]); files=[p for p in source.rglob("*") if p.is_file()]; exec("for p in files:\n for dest in (target/p.relative_to(source),target/\"practices/sources/emep\"/p.relative_to(source)):\n  dest.parent.mkdir(parents=True,exist_ok=True)\n  if dest.exists():\n   assert dest.read_bytes()==p.read_bytes(),dest\n  else:\n   shutil.copyfile(p,dest)")' "$project/data/practices/sources/emep" "$stage/check/data"
printf '%s  %s\n' 5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7 "$stage/check/data/current.json" | sha256sum -c -
python3 "$stage/check/src/arsiv.py" practice-check --input "$package" --inventory "$stage/check/data/practices/04-inventory.json" --base-release "$base"
python3 "$stage/check/src/arsiv.py" practice-source-check --input "$package" --review "$review"
python3 "$stage/check/src/arsiv.py" practice-preview --input "$package" --inventory "$stage/check/data/practices/04-inventory.json" --base-release "$base" --source-root "$stage/check/data/practices/sources/emep" --out "$stage/preview"
PYTHONPATH="$stage/check/src" python3 "$checks/bulu-2021-audit.py" "$stage/preview" "$package"
