#!/bin/bash
#SBATCH --job-name=gsd0410-agriculture
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-previews.sgFrq4
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/agriculture-2020-validation.py 9ab640a732034bf893e2702e28edd897f1f28178bc3754c92962a0236dee404f 2f2e58f00b788e7247f02d9b9a682fecf9ef7c7be01038fbd03a1fa79219a38d
