#!/bin/bash
#SBATCH --job-name=gsd0410-joint20
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-previews.sgFrq4
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/joint-2020-emep-validation.py
