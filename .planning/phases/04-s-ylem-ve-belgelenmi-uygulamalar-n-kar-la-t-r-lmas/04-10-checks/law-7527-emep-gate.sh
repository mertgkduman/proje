#!/bin/bash
#SBATCH --job-name=gsd0410-7527
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-previews.sgFrq4
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/law-7527-emep-validation.py af55456da629874af718c722029ea44b8721cb440715fc01f26179c714037dfc b14fda3407a02d80c7d8572de4802b20566e4d26b4235791531fd3c13ec4af6a
