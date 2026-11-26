#!/bin/bash
#SBATCH --job-name=gsd0410-idlib-v2
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-recovery.L0IReu
export GSD0404_RECOVERY_RECEIPTS=/work/mg551/gsd-phase04-recovery.L0IReu
unset TMPDIR
python3 /work/mg551/gsd-phase04-recovery.L0IReu/run-audit.py .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/idlib-2020-emep-v2-validation.py 276844791716e0f4080dd4150425362dc6bd340f6f33e1a798001b2d4a2bce11 2694a8b41ac5b561b96f3d137f5fd7f6c482053209c2144243de9a68a26fde4a
