#!/bin/bash
#SBATCH --job-name=gsd0410-trelle
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
set -euo pipefail
cd /hpc/group/pfisterlab/mg551/storage/proje
export GSD0404_PREVIEW_STAGING=/work/mg551/gsd-phase04-previews.sgFrq4
unset TMPDIR
python3 .planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/trelle-2019-emep-validation.py 284da1e60fbc9b81271abbf79d41e551ace5337d9f32ced8b61cbdf81a25c874 6e2e3efb418e164a1af33f27008f1bd6681e2b15b2802db5726717e4ee025f53
