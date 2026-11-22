"""Son renderer31 önizlemesini üç veri görünümünde bağımsız denetle."""
import hashlib
import json
import sqlite3
from pathlib import Path

here=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
r=json.loads((here/'dem-two2025-full-62410574.json').read_text())
p=Path(r['preview']); manifest=json.loads((p/'manifest.json').read_text()); data=json.loads((p/'records.json').read_text()); report=(p/'index.html').read_text()
assert manifest['renderer_version']==31
assert hashlib.sha256((p/'manifest.json').read_bytes()).hexdigest()==r['preview_manifest_sha256']
db=sqlite3.connect((p/'records.sqlite3').resolve().as_uri()+'?mode=ro',uri=True)
events={'0406-2025-103464-gundem':'tbmm-28-4-24-10-3464-gundem','0406-2025-103465-gundem':'tbmm-28-4-24-10-3465-gundem'}
for event,key in events.items():
 assert db.execute('select event_at,common_event_key from practice_event where id=?',(event,)).fetchone()==('2025-12-03',key)
 assert any(x['id']==event and x['common_event_key']==key for x in data['practice_event'])
 number=key.split('-')[-2]
 assert db.execute('select 1 from practice_event_evidence where event_id=? and passage_id=?',(event,'0406-tbmm-10'+number+'-detail-number-p')).fetchone()
assert db.execute('select state,relation_id from practice_candidate where id=?',('0406-2025-103464-unmatched',)).fetchone()==('unmatched',None)
for prefix in ('party','comparison'):
 for kind,ident,finding in [('unmatched','0406-2025-103464-unmatched','0406-103464-contribution-f'),('practice','0406-2025-103465-relation','0406-103465-result-f')]:
  start=report.index(f'id="{prefix}-{kind}-{ident}"');end=report.index('</article>',start)
  assert f'data-finding-id="{finding}"' in report[start:end]
db.close()
print('TWO_EVENTS_DETAIL_NUMBERS_AND_FINDINGS_BOTH_VIEWS_OK',r['preview_manifest_sha256'])
