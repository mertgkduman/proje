"""Eski gerçek preview snapshot'ına Hakkâri fragmanını bellekte ekleyip marker farkını ölçer."""
import html,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import arsiv
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
proof=json.loads((checks/'dem-dossier-62393671.json').read_text());data=json.loads((Path(proof['preview'])/'records.json').read_text());frag=json.loads((checks/'hakkari-event-fragment-draft.json').read_text())
for e in frag['entries']:
 kind=e['kind']
 if kind in data:data[kind].append(e['values'])
for kind,rows in frag['practice_records'].items():
 data.setdefault(kind,[]).extend(rows)
report=arsiv.render_comparison_snapshot(data,arsiv.render_report)
missing=[]
for e in frag['entries']:
 if e['kind']=='finding':
  ident=e['values']['id'];count=report.count('data-finding-id="'+html.escape(ident,quote=True)+'"')
  print('FINDING_MARKER',ident,count,flush=True)
  if not count:missing.append(ident)
print('MISSING',json.dumps(missing,ensure_ascii=False),flush=True)
