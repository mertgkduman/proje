"""5367 tam kapısı, önceki verinin korunumu ve iki görünüm denetimi."""
import importlib.util, json, os, sqlite3
from pathlib import Path
here=Path(__file__).resolve().parent; root=here.parents[3]; job=os.environ['SLURM_JOB_ID']
spec=importlib.util.spec_from_file_location('dem_tracer_validation',here/'tracer-validation.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
package=here/'5367-dem-draft.json'; review=here/'5367-dem-review-draft.json'
assert mod.sha(package)=='3b29f030c76cda43adafe2e33db8fb7008b1a233c83bc14f6f82dcb259d9c17c'
assert mod.sha(review)=='62534d40d4865a3fead5940678864ae3995bee7aee98f156055f3200b8d4a72e'
before=json.loads((root/'data/practices/04-dem.json').read_text()); candidate=json.loads(package.read_text())
canonical=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory'): assert {canonical(x) for x in before[k]} <= {canonical(x) for x in candidate[k]},k
for k,rows in before['practice_records'].items(): assert {canonical(x) for x in rows} <= {canonical(x) for x in candidate['practice_records'].get(k,[])},k
mod.main(package,review,'dem-5367','0406-2026-mdkd-report','0406-2025-224-relation','')
receipt=json.loads((here/f'dem-5367-{job}.json').read_text()); folder=Path(receipt['preview'])
snapshot=json.loads((folder/'records.json').read_text()); report=(folder/'index.html').read_text(); db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True)
assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
for event in [x['id'] for x in before['practice_records']['practice_event']]+['0406-2026-mdkd-report']:
 assert any(x['id']==event for x in snapshot['practice_event']) and db.execute('SELECT 1 FROM practice_event WHERE id=?',(event,)).fetchone(),event
assert db.execute("SELECT state FROM practice_candidate WHERE id='0406-2026-mdkd-dem-unmatched'").fetchone()==('unmatched',)
assert db.execute("SELECT 1 FROM practice_dispute WHERE id='0406-2026-mdkd-tally-dispute'").fetchone()
for prefix in ('party','comparison'):
 start=report.index('id="'+prefix+'-unmatched-0406-2026-mdkd-dem-unmatched"'); end=report.index('</article>',start)
 assert 'data-finding-id="0406-2026-mdkd-dem-f"' in report[start:end]
 assert 'data-finding-id="0406-2026-mdkd-tally-f"' in report[start:end]
 for relation,finding in [('0406-hakkari-selection-relation','0406-hakkari-dispute-finding'),('0406-101831-relation','0406-101831-debate-f')]:
  start=report.index('id="'+prefix+'-practice-'+relation+'"'); end=report.index('</article>',start)
  assert 'data-finding-id="'+finding+'"' in report[start:end]
db.close()
print('THIRTEEN_EVENTS_AND_ALL_DISPUTES_BOTH_VIEWS_OK',flush=True)
