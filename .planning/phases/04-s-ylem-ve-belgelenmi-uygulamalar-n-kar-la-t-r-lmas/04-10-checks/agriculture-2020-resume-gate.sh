#!/bin/bash
#SBATCH --job-name=gsd0410-agriculture-review
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=01:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/agriculture-2020-resume-validation.py
