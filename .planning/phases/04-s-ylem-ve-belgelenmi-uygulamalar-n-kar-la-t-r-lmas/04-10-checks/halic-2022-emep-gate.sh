#!/bin/bash
#SBATCH --job-name=gsd0410-halic22
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-previews.sgFrq4
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/halic-2022-emep-validation.py b16d14c2d0d180e92feb01ba554a0ba1dfeea3876ae49e71dca2662ec9e0949f 75b912d37b5498e22eca804d08d8b692823152d080087fc2f79a2d49c5529a60
