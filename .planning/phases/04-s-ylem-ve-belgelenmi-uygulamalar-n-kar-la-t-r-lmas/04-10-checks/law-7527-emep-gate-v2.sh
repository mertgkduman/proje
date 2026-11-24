#!/bin/bash
#SBATCH --job-name=gsd0410-7527v2
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-previews.sgFrq4
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/law-7527-emep-validation-v2.py 7aa6b60caa5b2adb5aeefd97acb7490f63dce40f9746d1a576c35b827538d7ae dcc1bee4e23cd700ef7f31239ffa45db5a02d00813378a45b1000c9a6d89bd19
