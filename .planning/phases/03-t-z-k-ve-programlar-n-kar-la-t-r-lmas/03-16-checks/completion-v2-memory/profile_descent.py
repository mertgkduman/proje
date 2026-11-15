"""Profile one actual release-to-successor comparison without auditing again."""
import cProfile
import io
import json
from pathlib import Path
import pstats
import resource
import time

import arsiv


resource.setrlimit(resource.RLIMIT_AS, (3 * 1024 ** 3, 3 * 1024 ** 3))
releases = Path('/tmp/tmphj4lx7ev/data/releases')
arsiv.DATA = releases.parent
candidate_id = 'a87bc0aadf3546f0b46ff376c6b6a622'
candidate_dir = releases / candidate_id
base_id = json.loads((candidate_dir / 'manifest.json').read_text())['base_release']
start = time.monotonic()
base = json.loads((releases / base_id / 'records.json').read_text())
candidate = json.loads((candidate_dir / 'records.json').read_text())
print('base', base_id, 'candidate', candidate_id, flush=True)
print('parsed_seconds', round(time.monotonic() - start, 3), flush=True)
print('table_lengths', json.dumps({name: [len(base.get(name, [])), len(candidate.get(name, []))]
      for name in (*arsiv.COMPARISON_TABLES, *arsiv.LINEAGE_TABLES)}), flush=True)
profile = cProfile.Profile()
start = time.monotonic()
result = profile.runcall(arsiv.validate_comparison_descent, base, candidate)
print('result', result, 'elapsed_seconds', round(time.monotonic() - start, 3),
      'peak_rss_kib', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, flush=True)
out = io.StringIO()
pstats.Stats(profile, stream=out).strip_dirs().sort_stats('cumulative').print_stats(35)
print(out.getvalue(), flush=True)
