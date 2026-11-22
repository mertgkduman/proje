"""Doğrulanmış snapshot ve Silopi fragmanıyla eksik bulgu işaretlerini ölç."""
import html,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import arsiv
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks');proof=json.loads((p/'dem-3961-full-62398995.json').read_text());data=json.loads((Path(proof['preview'])/'records.json').read_text());frag=json.loads((p/'silopi-event-fragment-draft.json').read_text())
for e in frag['entries']:
 if e['kind'] in data:data[e['kind']].append(e['values'])
for k,rows in frag['practice_records'].items():data.setdefault(k,[]).extend(rows)
report=arsiv.render_comparison_snapshot(data,arsiv.render_report); missing=[]
for e in frag['entries']:
 if e['kind']=='finding':
  ident=e['values']['id']; count=report.count('data-finding-id="'+html.escape(ident,quote=True)+'"');print('FINDING_MARKER',ident,count,flush=True)
  if not count:missing.append(ident)
for name in ('0305-dem-disiplin-yaptirim-dem-summary','0305-dem-disiplin-yaptirim-dem-quote','0305-dem-disiplin-yaptirim-hedep-summary','0305-dem-disiplin-yaptirim-hedep-quote'):
 count=report.count('data-finding-id="'+html.escape(name,quote=True)+'"');print('TARGET_MARKER',name,count,flush=True)
 if not count:missing.append(name)
print('MISSING',json.dumps(missing,ensure_ascii=False),flush=True)
