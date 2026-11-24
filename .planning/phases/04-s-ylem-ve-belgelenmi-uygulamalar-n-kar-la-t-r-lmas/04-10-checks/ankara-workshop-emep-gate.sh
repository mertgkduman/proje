#!/bin/bash
#SBATCH --job-name=gsd0410-ankara
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-previews.sgFrq4
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/ankara-workshop-emep-validation.py 7d63027d2dec7b9518ca86abae315e4306846ef2cdb8c5b3afc8972d3f110224 c87ddf95f097f750647140bf6f88d34d807fdb115346fadbe4fbc124b150b944
