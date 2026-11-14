import datetime
import json
import os
import socket
import subprocess
import sys
import uuid
from pathlib import Path

name, *argv = sys.argv[1:]
base = Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-11-checks')
base.mkdir(exist_ok=True)
token = uuid.uuid4().hex
try:
    with (base / f'{name}.log').open('wb') as log:
        child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
        metadata = dict(started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), host=socket.gethostname(),
                        owner_pid=os.getpid(), child_pid=child.pid, owner_token=token, argv=argv)
        (base / f'{name}.run.json').write_text(json.dumps(metadata, ensure_ascii=False) + '\n')
        result = child.wait()
except Exception as exc:
    with (base / f'{name}.log').open('ab') as log:
        log.write(('RUNNER_ERROR ' + repr(exc) + '\n').encode())
    result = 125
(base / f'{name}.exit').write_text(str(result) + '\n')
