"""Report entry field mismatches after the unchanged merge validator rejects."""

from collections import Counter
import json
from pathlib import Path
import runpy
import sys

import uygulamalar

here = Path(__file__).resolve().parent
original = uygulamalar.validate_practice_merge


def diagnose(snapshot):
    try:
        return original(snapshot)
    except ValueError as exc:
        if str(exc) != 'Birleşme girdisi kayıp':
            raise
        from uygulama_birlestirme import merge_packages
        for batch in snapshot.get('practice_merge_provenance', []):
            inputs = [dict(identity=r['input_identity'],raw=bytes.fromhex(r['raw_hex']))
                      for r in snapshot['practice_merge_input'] if r['provenance_id']==batch['id']]
            out = merge_packages(json.loads(batch['inventory_json']),inputs,bytes.fromhex(batch['decisions_hex']),
                                 decisions_sha256=batch['decisions_sha256'],
                                 base_records=json.loads(batch['base_records_json']))
            failures = []
            for entry in out['payload']['entries']:
                kind,wanted = entry['kind'],entry['values']
                rows = snapshot.get(kind,[])
                if any(all(row.get(k)==v for k,v in wanted.items()) for row in rows):
                    continue
                keys = [k for k in ('id','finding_id','passage_id','version_id','subject_id','scope_id') if k in wanted]
                close = next((row for row in rows if keys and all(row.get(k)==wanted[k] for k in keys)),None)
                difference = [k for k,v in wanted.items() if close is None or close.get(k)!=v]
                failures.append(dict(kind=kind,identity={k:wanted[k] for k in keys},
                    fields=difference, sqlite_match_exists=close is not None))
            print('MERGE_ENTRY_DIFFERENCES',json.dumps(dict(
                counts=dict(Counter(row['kind'] for row in failures)), examples=failures[:18]),
                ensure_ascii=False),file=sys.stderr,flush=True)
        raise


uygulamalar.validate_practice_merge = diagnose
runpy.run_path(str(here/'wave4-merge-rehearsal-preview-v2.py'))
