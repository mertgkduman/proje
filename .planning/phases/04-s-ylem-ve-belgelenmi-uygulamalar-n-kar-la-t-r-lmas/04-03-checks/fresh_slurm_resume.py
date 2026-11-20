#!/usr/bin/env python3
"""Run the existing sequential gate in a scheduler-owned allocation."""
import os, subprocess, sys
from pathlib import Path

here = Path(__file__).resolve().parent
env = dict(os.environ, GATE_EXTERNAL_TAXONOMY='1')
for name in ('GSD_PUBLIC_REPLAY_FIXTURE', 'GSD_PENDING_ACCEPTED_FIXTURE',
             'GSD_PENDING_ACCEPTED_MANIFEST_SHA256', 'GSD_PENDING_MERGE_FIXTURE'):
    env.pop(name, None)
job = env['SLURM_JOB_ID']
with (here / ('fresh-slurm-' + job + '.log')).open('x') as log:
    code = subprocess.call([sys.executable, str(here / 'fresh_gate.py')], stdout=log,
                           stderr=subprocess.STDOUT, env=env)
    log.flush(); os.fsync(log.fileno())
with (here / ('fresh-slurm-' + job + '.exit')).open('x') as result:
    result.write(str(code) + '\n'); result.flush(); os.fsync(result.fileno())
sys.exit(code)
