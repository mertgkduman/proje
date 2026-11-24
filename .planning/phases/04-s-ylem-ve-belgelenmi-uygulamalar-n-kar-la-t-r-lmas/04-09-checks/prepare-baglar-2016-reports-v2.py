from pathlib import Path
from hashlib import sha256
import json,sys
here=Path(sys.argv[1]);first=json.loads((here/'baglar-2016-reports-source-records.json').read_bytes())
entries=[e for e in first['entries'] if e['kind']=='passage']
for entry in entries:entry['values']['version_id']='0409-tokluca-council2016-v1'
out=here/'baglar-2016-reports-v2-source-records.json'
with out.open('x') as f:json.dump({'party_id':'dbp','entries':entries},f,ensure_ascii=False,indent=2);f.write('\n')
text=(here/'prepare-baglar-2016-reports.py').read_text().replace('baglar-2016-reports-source-records.json','baglar-2016-reports-v2-source-records.json').replace('baglar-2016-reports-draft.json','baglar-2016-reports-v2-draft.json').replace('baglar-2016-reports-review-draft.json','baglar-2016-reports-v2-review-draft.json').replace('baglar-2016-reports-reading-','baglar-2016-reports-v2-reading-')
exec(compile(text,str(here/'prepare-baglar-2016-reports.py'),'exec'))
