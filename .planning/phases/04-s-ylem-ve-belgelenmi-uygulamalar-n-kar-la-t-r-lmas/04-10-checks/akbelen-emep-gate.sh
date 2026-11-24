#!/bin/bash
#SBATCH --job-name=gsd0410-akbelen
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-previews.sgFrq4
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/akbelen-emep-validation.py 6d0f6c948e6a3b1e29f667baa02b5d521f8121d66e5de8cd01c5270622c894ad f49fe7c8c3bf04867b4e47d57c8c15dc97ed5665134d5c3573df050c1792acfc
