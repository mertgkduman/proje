"""03-15 yetkili yerel refresh: tek süreç, tek yazıcı kilidi."""
import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path('/hpc/group/pfisterlab/mg551/storage/proje')
sys.path.insert(0, str(ROOT / 'src'))
import arsiv

result = ROOT / '.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-15-checks/publish-result.json'
try:
    workspace = arsiv.open_workspace('/tmp')
    meta = json.loads((workspace / 'workspace.json').read_text())
    print(json.dumps({'workspace': str(workspace), 'pid': os.getpid(), 'host': os.uname().nodename, 'token': meta['token'], 'base': meta['base']}), flush=True)
    release = arsiv.publish_release(workspace, refresh=True)
    result.write_text(json.dumps({'exit': 0, 'release': release, 'workspace': str(workspace), 'base': meta['base']}, indent=2) + '\n')
    print('PUBLISH_RESULT', release, flush=True)
except Exception:
    traceback.print_exc()
    result.write_text(json.dumps({'exit': 1, 'error': traceback.format_exc()}, indent=2) + '\n')
    raise
