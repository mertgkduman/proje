#!/bin/bash
#SBATCH --job-name=gsd0410-1231
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-previews.sgFrq4
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/tezkere-1231-validation.py e79652bf1adf586f493e744d7b02416ba72ff15beecff3ed50a3c0bd9246d795 6128af3919bdce252a1808d78fa47768c15931c3bbfb7c5fd0dddd772805bab0
