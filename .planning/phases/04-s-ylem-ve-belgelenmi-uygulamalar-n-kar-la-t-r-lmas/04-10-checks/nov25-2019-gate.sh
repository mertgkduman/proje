#!/bin/bash
#SBATCH --job-name=gsd0410-nov25
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-previews.sgFrq4
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/nov25-2019-validation.py f9a895b1b92577c3952898c9f7c6956798531530004750e3ffd2f951c5ff0701 50bc06f17456bb6dc41f37ff003d672179efc3e5515904f4c7128fb7cbebfe87
