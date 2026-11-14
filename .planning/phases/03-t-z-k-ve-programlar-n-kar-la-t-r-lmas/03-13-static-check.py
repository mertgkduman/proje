import json
import sys
from pathlib import Path

sys.path.insert(0,'src')
from arsiv import validate_comparisons

base=json.loads(Path('data/releases/bcd3dd70ea6d4cefb3379b1a59ccf264/records.json').read_text())
root=Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas')
packages=[json.loads(Path('data/comparisons/03-demokrat-program-1.json').read_text()),json.loads((root/'03-13-program-2-draft.json').read_text())]
for package in packages:
    for record in package['records']:
        kind,values=record['kind'],record['values']
        if kind=='comparison_row':
            previous=next((i for i,x in enumerate(base[kind]) if x['id']==values['id']),None)
            if previous is not None: base[kind][previous]=values; continue
        base[kind].append(values)
validate_comparisons(base)
print('STATIC_COMPARISON_STRUCTURE_OK')
