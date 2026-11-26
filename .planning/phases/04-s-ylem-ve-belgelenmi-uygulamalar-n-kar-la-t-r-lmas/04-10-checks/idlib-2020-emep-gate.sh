#!/bin/bash
#SBATCH --job-name=gsd0410-idlib
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-recovery.L0IReu
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/idlib-2020-emep-validation.py 7dc305ca8dbd958f15fa9225f0ece87590da2988cfdd44ee838a8d889169093a 13a02e5272a4391a9d6d2199a0cd101233e985d2c722c19eaed3b5f85656de37
