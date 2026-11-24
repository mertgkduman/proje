#!/bin/bash
#SBATCH --job-name=gsd0410-1231v2
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-previews.sgFrq4
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/tezkere-1231-validation-v2.py 24edd50cf902d9dad5c4ff6c003e8798e0f5918242201c1e9809d1c70668dc8a fdce920645fc184fd2ec51b1b5e0b894fcd774b838c210119c69dcbbf3c566ec
