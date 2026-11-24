#!/bin/bash
#SBATCH --job-name=gsd0410-halic22v2
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-previews.sgFrq4
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/halic-2022-emep-v2-validation.py faf5b3a8e52a67c1fbf0d946ee81044bbbfef3a8231c58567bfd8b159a9390b2 9a325e0e74acbab72c7edbf35ff62b04db9fb2db0e6efae9677d5227adc8e7f6
